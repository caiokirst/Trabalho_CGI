# main.py
import cv2
import numpy as np

# Importa todas as configurações do arquivo configs.py
from configs import (VIDEO_PATH, PARKING_SPOTS, COLOR_RANGES_HSV,
                     GAUSSIAN_BLUR_KERNEL_SIZE, GAUSSIAN_BLUR_SIGMA_X,
                     APPLY_LINEAR_BRIGHTNESS_CONTRAST, LINEAR_ALPHA, LINEAR_BETA,
                     APPLY_CLAHE, CLAHE_CLIP_LIMIT, CLAHE_TILE_GRID_SIZE,
                     APPLY_SIMPLE_THRESHOLD, SIMPLE_THRESHOLD_VALUE, SIMPLE_THRESHOLD_MAX_VALUE,
                     CANNY_THRESHOLD1, CANNY_THRESHOLD2, 
                     CLOSE_KERNEL_SIZE, CLOSE_ITERATIONS,
                     MIN_CAR_AREA, MAX_CAR_AREA, MIN_ASPECT_RATIO, MAX_ASPECT_RATIO, 
                     MIN_INTERSECTION_AREA_PERCENT_POLY, CAR_ROI_PADDING,
                     PARKING_AREA_MASK_COORDS, CONSECUTIVE_FRAMES_THRESHOLD)

# Importa funções auxiliares do arquivo utils.py
from utils import get_car_color

# --- Funções Auxiliares (Para Manter o main.py Limpo) ---

def initialize_video_capture(video_path):
    """Tenta abrir e verificar a captura de vídeo, com tratamento de erros."""
    cap = cv2.VideoCapture(video_path)
    cv2.waitKey(100) # Pequeno atraso para janelas serem criadas

    if not cap.isOpened() or not cap.read()[0]: # Tenta ler um frame para ter certeza
        print(f"Erro CRÍTICO: Não foi possível abrir ou ler o vídeo em {video_path}.")
        print("Possíveis causas: Caminho incorreto, arquivo corrompido, codecs faltando.")
        exit()
    
    # Reinicializa o cap, pois já lemos um frame na verificação.
    return cv2.VideoCapture(video_path)

def apply_image_enhancements(img_gray):
    """Aplica ajustes de brilho/contraste e CLAHE conforme configurado."""
    processed_img = img_gray.copy()

    if APPLY_LINEAR_BRIGHTNESS_CONTRAST:
        # Converte para float para cálculos precisos, depois de volta para uint8
        processed_img = cv2.convertScaleAbs(processed_img, alpha=LINEAR_ALPHA, beta=LINEAR_BETA)
        cv2.imshow('Linear Adjust (Debug)', processed_img) # Debug da imagem ajustada
    
    return processed_img

def find_car_contours(source_image_for_canny, roi_mask_general):
    """Detecta bordas com Canny e fecha-as para encontrar contornos de carros."""
    
    # Detecção de Bordas com Canny
    canny_edges = cv2.Canny(source_image_for_canny, CANNY_THRESHOLD1, CANNY_THRESHOLD2)

    # Operações Morfológicas PÓS-CANNY para fechar buracos e conectar bordas dos carros
    close_kernel = np.ones(CLOSE_KERNEL_SIZE, np.uint8)
    closed_edges = cv2.morphologyEx(canny_edges, cv2.MORPH_CLOSE, close_kernel, iterations=CLOSE_ITERATIONS)
    
    # Aplica a máscara da ROI geral para garantir que contornos fora dela sejam ignorados.
    closed_edges_final = cv2.bitwise_and(closed_edges, closed_edges, mask=roi_mask_general)

    # Encontra contornos nas bordas processadas
    contours, _ = cv2.findContours(closed_edges_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    return contours, canny_edges, closed_edges_final

def draw_vaga_status(display_frame, vaga_data, status_color_box, status_text):
    """Desenha o polígono da vaga e seu status na tela."""
    vaga_type = vaga_data['type']
    vaga_coords = vaga_data['coords']
    
    if vaga_type == 'poly':
        cv2.polylines(display_frame, [vaga_coords], isClosed=True, color=status_color_box, thickness=2)
        pt_texto = tuple(vaga_coords[0] + np.array([0, -10])) # Posição do texto acima da vaga
        cv2.putText(display_frame, status_text, pt_texto,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color_box, 2, cv2.LINE_AA)

# --- Processamento Principal do Vídeo ---

cap = initialize_video_capture(VIDEO_PATH)

print("Sistema de Monitoramento de Estacionamento Iniciado (Foco na Vaga e Cor).")
print("Pressione 'q' para sair a qualquer momento.")

consecutive_occupied_frames_count = [0] * len(PARKING_SPOTS)

# Loop principal de leitura e processamento de frames
while True:
    ret, frame = cap.read()
    if not ret:
        print("Fim do vídeo ou erro na leitura do frame.")
        break
    
    frame = cv2.resize(frame, (960, 540))
    display_frame = frame.copy() # Cópia para desenhar

    # --- 1. Criar e Aplicar a Máscara de ROI Geral do Estacionamento ---
    roi_mask_general = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(roi_mask_general, [PARKING_AREA_MASK_COORDS], 255)
    
    masked_display_frame = cv2.bitwise_and(display_frame, display_frame, mask=roi_mask_general)


    # --- 2. Pré-processamento de Imagem (Aplicando Máscara e Ajustes de Imagem) ---
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplica ajustes de brilho/contraste ou CLAHE
    enhanced_image = apply_image_enhancements(gray_image)

    # Aplica desfoque Gaussiano
    blurred = cv2.GaussianBlur(enhanced_image, GAUSSIAN_BLUR_KERNEL_SIZE, GAUSSIAN_BLUR_SIGMA_X)
    
    # Aplica a máscara de ROI na imagem borrada ANTES do Canny
    source_for_canny = cv2.bitwise_and(blurred, blurred, mask=roi_mask_general)

    # Opcional: Aplicar limiar simples ANTES do Canny, se ativado em configs.py
    if APPLY_SIMPLE_THRESHOLD:
        _, thresholded = cv2.threshold(source_for_canny, SIMPLE_THRESHOLD_VALUE, SIMPLE_THRESHOLD_MAX_VALUE, cv2.THRESH_BINARY_INV)
        source_for_canny = thresholded
        cv2.imshow('Thresholded (Debug)', thresholded) 

    # --- 3. Detectar Contornos de Carros ---
    contours, canny_edges_debug, closed_edges_debug = find_car_contours(source_for_canny, roi_mask_general)

    # Inicializa a contagem de vagas livres
    vagas_livres_count = len(PARKING_SPOTS)
    
    # --- 4. Processa cada vaga individualmente para verificar ocupação e cor ---
    for i, vaga_data in enumerate(PARKING_SPOTS):
        vaga_id = vaga_data['id']
        vaga_coords = vaga_data['coords']
        
        current_frame_is_occupied = False 
        detected_car_color = "Livre" 
        
        vaga_specific_mask = np.zeros(closed_edges_debug.shape, dtype=np.uint8)
        cv2.fillPoly(vaga_specific_mask, [vaga_coords], 255)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(cnt)
            
            aspect_ratio = float(w_cnt) / h_cnt if h_cnt > 0 else 0

            # DEBUG: Imprime a área e a proporção para ajudar a ajustar os limiares em configs.py
            # Descomente a linha abaixo para ver os valores no console e ajustar!
            print(f"Contorno - Área: {area:.2f}, Proporção: {aspect_ratio:.2f}") 
            
            if (MIN_CAR_AREA < area < MAX_CAR_AREA) and \
               (MIN_ASPECT_RATIO < aspect_ratio < MAX_ASPECT_RATIO):
                
                # Desenha um retângulo azul ao redor do contorno que passou pelos filtros (indicando um carro detectado)
                cv2.rectangle(masked_display_frame, (x_cnt, y_cnt), (x_cnt + w_cnt, y_cnt + h_cnt), (255, 0, 0), 2)

                # --- Verifica a interseção do contorno do carro com a VAGA ESPECÍFICA ---
                car_contour_mask_for_intersection = np.zeros(closed_edges_debug.shape, dtype=np.uint8)
                cv2.drawContours(car_contour_mask_for_intersection, [cnt], -1, 255, -1)
                
                intersection_mask = cv2.bitwise_and(vaga_specific_mask, car_contour_mask_for_intersection)
                intersection_pixels = cv2.countNonZero(intersection_mask)
                
                vaga_poly_area = cv2.contourArea(vaga_coords)

                if vaga_poly_area > 0 and intersection_pixels > vaga_poly_area * MIN_INTERSECTION_AREA_PERCENT_POLY:
                    current_frame_is_occupied = True
                    
                    x_roi_car = max(0, x_cnt - CAR_ROI_PADDING)
                    y_roi_car = max(0, y_cnt - CAR_ROI_PADDING)
                    w_roi_car = min(frame.shape[1] - x_roi_car, w_cnt + 2 * CAR_ROI_PADDING)
                    h_roi_car = min(frame.shape[0] - y_roi_car, h_cnt + 2 * CAR_ROI_PADDING)
                    car_roi = frame[y_roi_car : y_roi_car + h_roi_car, x_roi_car : x_roi_car + w_roi_car]
                    
                    detected_car_color = get_car_color(car_roi)
                    
                    break 
        
        # --- 5. Filtragem Temporal e Desenho do Status da Vaga ---
        if current_frame_is_occupied:
            consecutive_occupied_frames_count[i] += 1 
        else:
            consecutive_occupied_frames_count[i] = 0 

        if consecutive_occupied_frames_count[i] >= CONSECUTIVE_FRAMES_THRESHOLD:
            color_box = (0, 0, 255) # Vermelho
            vagas_livres_count -= 1 
            text_to_show = f"Vaga {vaga_id} - {detected_car_color}"
        else:
            color_box = (0, 255, 0) # Verde
            text_to_show = f"Vaga {vaga_id} - Livre" 

        draw_vaga_status(masked_display_frame, vaga_data, color_box, text_to_show)

    # --- 6. Exibir Contagem Total de Vagas Livres ---
    total_vagas = len(PARKING_SPOTS)
    cv2.putText(masked_display_frame, f'Vagas Livres: {vagas_livres_count}/{total_vagas}', (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

    # --- 7. Exibir Janelas de Visualização e Debug ---
    cv2.imshow('Estacionamento Inteligente', masked_display_frame) 
    cv2.imshow('Canny Edges (Debug)', canny_edges_debug) 
    cv2.imshow('Closed Edges (Debug)', closed_edges_debug) 

    if APPLY_SIMPLE_THRESHOLD:
        cv2.imshow('Thresholded (Debug)', source_for_canny)
    if APPLY_LINEAR_BRIGHTNESS_CONTRAST:
        cv2.imshow('Linear Adjust (Debug)', enhanced_image) 
    if APPLY_CLAHE:
        cv2.imshow('CLAHE (Debug)', enhanced_image) 


    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):
        break

# --- Limpeza e Liberação de Recursos ---
cap.release()
cv2.destroyAllWindows()
print("Programa finalizado.")