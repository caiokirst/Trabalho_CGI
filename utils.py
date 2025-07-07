# utils.py
import cv2
import numpy as np
# Importa KNOWN_COLORS_BGR e os novos parâmetros de filtro de cor do configs.py
from configs import KNOWN_COLORS_BGR, S_MIN_FILTER_COLOR_ANALYSIS, V_MIN_FILTER_COLOR_ANALYSIS

def get_car_color(roi):
    """
    Determina a cor dominante em uma Região de Interesse (ROI) de um carro.
    Primeiro, filtra pixels de vidro/sombra. Em seguida, usa K-Means Clustering 
    e compara a cor dominante com uma paleta de cores BGR conhecidas.

    Args:
        roi (numpy.ndarray): A imagem recortada da Região de Interesse (ROI) do carro (em formato BGR).

    Returns:
        str: O nome da cor detectada (ex: "Branco", "Preto", "Azul", "Desconhecida", "N/A").
             Retorna "N/A" se a ROI for inválida ou muito pequena para processamento.
    """
    # 1. Validação da ROI de entrada.
    if roi is None or roi.size == 0 or roi.shape[0] < 5 or roi.shape[1] < 5:
        return "N/A"

    # 2. Filtrar pixels de vidro/sombra antes do K-Means.
    # Converte a ROI para HSV para trabalhar com Saturação (S) e Valor (V - Brilho).
    hsv_roi_filter = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Cria uma máscara para pixels que NÃO SÃO MUITO ESCUROS E NÃO SÃO MUITO DESSATURADOS.
    # Pixels com S > S_MIN_FILTER_COLOR_ANALYSIS OU V > V_MIN_FILTER_COLOR_ANALYSIS serão mantidos.
    mask_color_filter = cv2.inRange(hsv_roi_filter, 
                                    np.array([0, S_MIN_FILTER_COLOR_ANALYSIS, V_MIN_FILTER_COLOR_ANALYSIS]),
                                    np.array([180, 255, 255]))

    # Aplica a máscara para obter apenas os pixels da "pintura" (ou o que sobrou).
    filtered_pixels_roi = cv2.bitwise_and(roi, roi, mask=mask_color_filter)
    
    # 3. Lógica de fallback se nenhum pixel "útil" restar após a filtragem.
    # Verifica se a ROI filtrada está vazia ou se todos os pixels restantes são pretos (0,0,0).
    if filtered_pixels_roi.size == 0 or cv2.countNonZero(cv2.cvtColor(filtered_pixels_roi, cv2.COLOR_BGR2GRAY)) == 0:
        # Se não sobraram pixels válidos da pintura, tenta classificar a cor original como Preto/Desconhecida.
        avg_value_orig = np.mean(hsv_roi_filter[:,:,2])
        if avg_value_orig < 60: # Limiar baixo para considerar "Preto"
            return "Preto"
        else:
            return "Desconhecida" 
            
    # 4. Preparação dos Dados Filtrados para K-Means.
    # Redimensiona a ROI filtrada para uma lista de pixels (num_pixels, 3 canais BGR).
    pixels = filtered_pixels_roi.reshape((-1, 3))
    # Remove quaisquer pixels (0,0,0) que foram gerados pela máscara (resultado de pixels filtrados).
    pixels = pixels[~np.all(pixels == 0, axis=1)] 
    
    # Última verificação de pixels restantes para K-Means.
    if pixels.shape[0] == 0:
        avg_value_orig = np.mean(hsv_roi_filter[:,:,2])
        if avg_value_orig < 60:
            return "Preto"
        else:
            return "Desconhecida"

    pixels = np.float32(pixels) # K-Means espera float32.

    # 5. Execução do K-Means Clustering.
    # Queremos encontrar a cor mais dominante (k=1).
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    k = 1 
    
    try:
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    except cv2.error as e:
        print(f"Erro no K-Means: {e}. ROI shape: {roi.shape}. Pixels after filter: {pixels.shape}")
        return "N/A"

    # A cor BGR mais dominante é o centro do primeiro (e único) cluster.
    dominant_bgr = centers[0].astype(np.uint8)

    # DEBUG: Imprimir a cor dominante BGR encontrada pelo K-Means (após filtragem).
    print(f"DEBUG - Cor Dominante BGR da ROI (Filtrada): {dominant_bgr}") 

    # 6. Comparação da Cor Dominante com a Paleta de Cores Conhecidas.
    min_distance = float('inf') 
    detected_color_name = "Desconhecida" 

    for color_name, known_bgr_value in KNOWN_COLORS_BGR.items():
        known_bgr_array = np.array(known_bgr_value)
        # Calcula a distância euclidiana entre a cor dominante do carro e cada cor na paleta.
        distance = np.sqrt(np.sum((dominant_bgr - known_bgr_array)**2))
        
        if distance < min_distance:
            min_distance = distance
            detected_color_name = color_name

    # 7. Classificação Final Baseada na Distância e Limiar de Tolerância.
    # Este limiar define quão "próxima" a cor dominante do carro precisa estar
    # de uma cor na sua paleta para não ser classificada como "Desconhecida".
    if min_distance > 30: # Se a cor dominante está muito longe de qualquer cor conhecida na sua paleta.
        return "Desconhecida"

    return detected_color_name