# main.py
import cv2
import numpy as np
# Importa todas as configurações do arquivo configs.py
from configs import VIDEO_PATH, PARKING_SPOTS, \
                    CANNY_THRESHOLD1, CANNY_THRESHOLD2, \
                    GAUSSIAN_BLUR_KERNEL_SIZE, GAUSSIAN_BLUR_SIGMA_X, \
                    CLOSE_KERNEL_SIZE, CLOSE_ITERATIONS, \
                    MIN_CAR_AREA, MAX_CAR_AREA, MIN_ASPECT_RATIO, MAX_ASPECT_RATIO, \
                    MIN_INTERSECTION_AREA_PERCENT_POLY, \
                    CAR_ROI_PADDING, \
                    APPLY_SIMPLE_THRESHOLD, SIMPLE_THRESHOLD_VALUE, SIMPLE_THRESHOLD_MAX_VALUE, \
                    PARKING_AREA_MASK_COORDS, \
                    CONSECUTIVE_FRAMES_THRESHOLD, \
                    APPLY_LINEAR_BRIGHTNESS_CONTRAST, LINEAR_ALPHA, LINEAR_BETA, \
                    APPLY_CLAHE, CLAHE_CLIP_LIMIT, CLAHE_TILE_GRID_SIZE # Importa os novos parâmetros de ajuste de imagem

# Importa funções auxiliares do arquivo utils.py
from utils import get_car_color

# --- Processamento Principal do Vídeo ---

# Abre o arquivo de vídeo
cap = cv2.VideoCapture(VIDEO_PATH)

# Adiciona um pequeno atraso para as janelas de vídeo serem criadas (pode ajudar com o problema de "não abrir")
cv2.waitKey(100) # Espera 100 ms

# Verifica se o vídeo foi aberto corretamente e se é possível ler o primeiro frame.
# Se o vídeo não abrir, este print será mostrado no console.
if not cap.isOpened() or not cap.read()[0]:
    print(f"Erro CRÍTICO: Não foi possível abrir ou ler o vídeo em {VIDEO_PATH}.")
    print("Possíveis causas: Caminho incorreto, arquivo corrompido, codecs faltando.")
    exit()
# Reinicializa o cap, pois já lemos um frame na verificação.
cap = cv2.VideoCapture(VIDEO_PATH)


print("Sistema de Monitoramento de Estacionamento Iniciado (Foco na Vaga e Cor).")
print("Pressione 'q' para sair a qualquer momento.")

# Lista para manter a contagem de frames consecutivos de ocupação para cada vaga
# Isso é usado para a filtragem temporal, tornando a detecção mais estável.
consecutive_occupied_frames_count = [0] * len(PARKING_SPOTS)

# Loop principal de leitura e processamento de frames
while True:
    ret, frame = cap.read() # Lê um frame do vídeo
    if not ret:
        print("Fim do vídeo ou erro na leitura do frame.")
        break
    
    # Redimensiona o frame para um tamanho padrão para processamento consistente (960x540)
    frame = cv2.resize(frame, (960, 540))
    display_frame = frame.copy() # Cria uma cópia do frame original para desenhar sobre ela

    # --- 1. Criar e Aplicar a Máscara de ROI Geral do Estacionamento ---
    # Cria uma máscara preta do tamanho do frame
    roi_mask_general = np.zeros(frame.shape[:2], dtype=np.uint8)
    # Preenche o polígono da área de interesse com branco (255) na máscara
    cv2.fillPoly(roi_mask_general, [PARKING_AREA_MASK_COORDS], 255)
    
    # Aplica a máscara no frame original para visualização
    # Isso fará com que a área fora da ROI fique preta na janela "Estacionamento Inteligente"
    masked_display_frame = cv2.bitwise_and(display_frame, display_frame, mask=roi_mask_general)


    # --- Pré-processamento de Imagem (Aplicando Máscara e Ajustes de Imagem) ---
    processing_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Começa com a imagem em escala de cinza

    # Ajuste de Brilho e Contraste Linear
    if APPLY_LINEAR_BRIGHTNESS_CONTRAST:
        # Converte para float para cálculos precisos, depois de volta para uint8
        processing_image = cv2.convertScaleAbs(processing_image, alpha=LINEAR_ALPHA, beta=LINEAR_BETA)
        cv2.imshow('Linear Adjust (Debug)', processing_image) # Debug da imagem ajustada

    # Equalização de Histograma Adaptativa (CLAHE)
    if APPLY_CLAHE:
        clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID_SIZE)
        processing_image = clahe.apply(processing_image)
        cv2.imshow('CLAHE (Debug)', processing_image) # Debug da imagem CLAHE

    # Aplicar desfoque Gaussiano. Aplica na imagem após ajustes de brilho/contraste/CLAHE
    blurred = cv2.GaussianBlur(processing_image, GAUSSIAN_BLUR_KERNEL_SIZE, GAUSSIAN_BLUR_SIGMA_X)
    
    # Aplica a máscara de ROI na imagem borrada ANTES do Canny
    # Isso é crucial para que o Canny não detecte bordas fora da sua área de interesse.
    blurred_masked = cv2.bitwise_and(blurred, blurred, mask=roi_mask_general)


    # Opcional: Aplicar limiar simples ANTES do Canny, se ativado em configs.py
    if APPLY_SIMPLE_THRESHOLD:
        _, thresholded = cv2.threshold(blurred_masked, SIMPLE_THRESHOLD_VALUE, SIMPLE_THRESHOLD_MAX_VALUE, cv2.THRESH_BINARY_INV)
        source_for_canny = thresholded
        cv2.imshow('Thresholded (Debug)', thresholded) # Nova janela de debug para o limiar simples
    else:
        source_for_canny = blurred_masked # Canny agora usa a imagem borrada e MASCARADA


    # Detecção de Bordas com Canny
    canny_edges = cv2.Canny(source_for_canny, CANNY_THRESHOLD1, CANNY_THRESHOLD2)

    # Operações Morfológicas PÓS-CANNY para fechar buracos e conectar bordas dos carros
    close_kernel = np.ones(CLOSE_KERNEL_SIZE, np.uint8)
    closed_edges = cv2.morphologyEx(canny_edges, cv2.MORPH_CLOSE, close_kernel, iterations=CLOSE_ITERATIONS)
    
    # Opcional: Aplicar a máscara também na imagem de bordas fechadas para garantir.
    # Embora a máscara já tenha sido aplicada antes do Canny, um bitwise_and aqui garante que não haja
    # nenhum pixel residual fora da ROI.
    closed_edges_final = cv2.bitwise_and(closed_edges, closed_edges, mask=roi_mask_general)


    # Encontra contornos nas bordas processadas (agora sobre a imagem FINALMENTE MASCARADA)
    contours, _ = cv2.findContours(closed_edges_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Inicializa a variável de contagem de vagas livres
    vagas_livres_count = len(PARKING_SPOTS)
    
    # --- Processa cada vaga individualmente para verificar ocupação e cor ---
    for i, vaga_data in enumerate(PARKING_SPOTS):
        vaga_id = vaga_data['id']
        vaga_coords = vaga_data['coords']
        
        current_frame_is_occupied = False # Status da vaga NO FRAME ATUAL (antes da filtragem temporal)
        detected_car_color = "Livre" # Padrão inicial
        
        # Cria uma máscara específica para a VAGA atual
        vaga_specific_mask = np.zeros(closed_edges_final.shape, dtype=np.uint8)
        cv2.fillPoly(vaga_specific_mask, [vaga_coords], 255)

        # Procura por um contorno de carro dentro desta vaga específica
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(cnt)
            
            aspect_ratio = float(w_cnt) / h_cnt if h_cnt > 0 else 0

            # DEBUG: Imprime a área e a proporção para ajudar a ajustar os limiares em configs.py
            # Descomente a linha abaixo para ver os valores no console e ajustar!
            # print(f"Contorno - Área: {area:.2f}, Proporção: {aspect_ratio:.2f}") 
            
            # Filtra contornos com base nas propriedades esperadas de um carro
            if (MIN_CAR_AREA < area < MAX_CAR_AREA) and \
               (MIN_ASPECT_RATIO < aspect_ratio < MAX_ASPECT_RATIO):
                
                # Desenha um retângulo azul ao redor do contorno que passou pelos filtros (indicando um carro detectado)
                # OBS: Este retângulo aparecerá mesmo se o carro não ocupar uma vaga, útil para debug.
                cv2.rectangle(masked_display_frame, (x_cnt, y_cnt), (x_cnt + w_cnt, y_cnt + h_cnt), (255, 0, 0), 2)

                # --- Verifica a interseção do contorno do carro com a VAGA ESPECÍFICA ---
                car_contour_mask_for_intersection = np.zeros(closed_edges_final.shape, dtype=np.uint8)
                cv2.drawContours(car_contour_mask_for_intersection, [cnt], -1, 255, -1) # Desenha o contorno do carro preenchido
                
                intersection_mask = cv2.bitwise_and(vaga_specific_mask, car_contour_mask_for_intersection)
                intersection_pixels = cv2.countNonZero(intersection_mask)
                
                vaga_poly_area = cv2.contourArea(vaga_coords)

                # Se houver uma interseção significativa, a vaga está ocupada
                if vaga_poly_area > 0 and intersection_pixels > vaga_poly_area * MIN_INTERSECTION_AREA_PERCENT_POLY:
                    current_frame_is_occupied = True
                    
                    # Recorta a ROI do carro para detecção de cor
                    x_roi_car = max(0, x_cnt - CAR_ROI_PADDING)
                    y_roi_car = max(0, y_cnt - CAR_ROI_PADDING)
                    w_roi_car = min(frame.shape[1] - x_roi_car, w_cnt + 2 * CAR_ROI_PADDING)
                    h_roi_car = min(frame.shape[0] - y_roi_car, h_cnt + 2 * CAR_ROI_PADDING)
                    car_roi = frame[y_roi_car : y_roi_car + h_roi_car, x_roi_car : x_roi_car + w_roi_car]
                    
                    detected_car_color = get_car_color(car_roi)
                    
                    # Uma vez que um carro é encontrado e ocupa esta vaga, não precisa verificar outros contornos para esta vaga.
                    break 
        
        # --- Desenha o status da vaga (vermelho/verde) e exibe a cor (se ocupada) ---
        if current_frame_is_occupied:
            consecutive_occupied_frames_count[i] += 1 # Incrementa o contador
        else:
            consecutive_occupied_frames_count[i] = 0 # Reseta se não estiver ocupada neste frame

        # Determina o status FINAL da vaga com base na contagem consecutiva
        if consecutive_occupied_frames_count[i] >= CONSECUTIVE_FRAMES_THRESHOLD:
            # Vaga é considerada ocupada de forma estável
            color_box = (0, 0, 255) # Vermelho
            vagas_livres_count -= 1 # Decrementa o contador de vagas livres
            text_to_show = f"Vaga {vaga_id} - {detected_car_color}"
        else:
            # Vaga é considerada livre ou não estável o suficiente para ser ocupada
            color_box = (0, 255, 0) # Verde
            text_to_show = f"Vaga {vaga_id} - Livre" # Exibe "Livre" (a cor será "Livre" se não detectada de forma estável)

        # Desenha o polígono da vaga na tela principal
        cv2.polylines(masked_display_frame, [vaga_coords], isClosed=True, color=color_box, thickness=2)
        pt_texto = tuple(vaga_coords[0] + np.array([0, -10])) # Posição do texto acima da vaga
        cv2.putText(masked_display_frame, text_to_show, pt_texto,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_box, 2, cv2.LINE_AA)

    # --- Exibir contagem da quantidade de vagas disponíveis (3.0 pontos) ---
    total_vagas = len(PARKING_SPOTS)
    cv2.putText(masked_display_frame, f'Vagas Livres: {vagas_livres_count}/{total_vagas}', (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

    # --- Exibir o vídeo carregado (1.0 ponto) ---
    cv2.imshow('Estacionamento Inteligente', masked_display_frame) # Exibe o frame com a máscara aplicada
    
    # --- Debug das imagens de bordas ---
    cv2.imshow('Canny Edges (Debug)', canny_edges) # Canny antes da última máscara
    cv2.imshow('Closed Edges (Debug)', closed_edges_final) # A imagem mais importante para ver a detecção!

    # Se APPLY_SIMPLE_THRESHOLD for True, a janela 'Thresholded (Debug)' também será exibida.
    # Se APPLY_LINEAR_BRIGHTNESS_CONTRAST for True, a janela 'Linear Adjust (Debug)' também será exibida.
    # Se APPLY_CLAHE for True, a janela 'CLAHE (Debug)' também será exibida.

    # Espera por 30ms ou até que 'q' seja pressionado
    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):
        break

# --- Limpeza e Liberação de Recursos ---
cap.release()
cv2.destroyAllWindows()
print("Programa finalizado.")