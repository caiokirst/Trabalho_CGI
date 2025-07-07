# utils.py
import cv2
import numpy as np
from configs import COLOR_RANGES_HSV

def get_car_color(roi):
    """
    Determina a cor dominante em uma Região de Interesse (ROI) usando o espaço de cor HSV.
    Args:
        roi (numpy.ndarray): A imagem recortada do carro.
    Returns:
        str: O nome da cor detectada (ex: "Branco", "Preto", "Azul").
    """
    if roi is None or roi.size == 0 or roi.shape[0] < 5 or roi.shape[1] < 5:
        return "N/A"

    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    max_pixels = 0
    detected_color = "Desconhecida"

    # Itera sobre as faixas de cor predefinidas para encontrar a cor dominante
    for color_name, (lower_hsv, upper_hsv) in COLOR_RANGES_HSV.items():
        # print(f"Verificando cor: {color_name} com limites {lower_hsv} - {upper_hsv}") # Manter para debug se quiser ver as faixas sendo testadas

        # Tratamento especial para o vermelho que tem duas faixas no HSV
        if color_name == "Vermelho":
            lower_red1 = np.array(COLOR_RANGES_HSV["Vermelho"][0], dtype=np.uint8)
            upper_red1 = np.array(COLOR_RANGES_HSV["Vermelho"][1], dtype=np.uint8)
            mask1 = cv2.inRange(hsv_roi, lower_red1, upper_red1)

            lower_red2 = np.array(COLOR_RANGES_HSV["Vermelho2"][0], dtype=np.uint8)
            upper_red2 = np.array(COLOR_RANGES_HSV["Vermelho2"][1], dtype=np.uint8)
            mask2 = cv2.inRange(hsv_roi, lower_red2, upper_red2)

            mask = cv2.bitwise_or(mask1, mask2)
        elif color_name == "Vermelho2": # Se já tratou o vermelho na primeira parte
            continue
        else:
            current_lower_bound = np.array(lower_hsv, dtype=np.uint8)
            current_upper_bound = np.array(upper_hsv, dtype=np.uint8)
            mask = cv2.inRange(hsv_roi, current_lower_bound, current_upper_bound)

        num_pixels = cv2.countNonZero(mask)

        # Se esta cor tem mais pixels que a cor detectada anteriormente, atualiza
        if num_pixels > max_pixels:
            max_pixels = num_pixels
            detected_color = color_name

    # Heurística para cores neutras (branco, preto, cinza) se NENHUMA cor forte for predominantemente detectada.
    total_pixels = roi.shape[0] * roi.shape[1]
    # Reduzi o limiar para 0.15. Se mais de 15% dos pixels do ROI caem em alguma cor vibrante, 
    # ele NÃO será classificado como cinza/preto/branco pela heurística.
    if total_pixels > 0 and max_pixels / total_pixels < 0.15: # Ajustado de 0.2 para 0.15
        avg_value = np.mean(hsv_roi[:,:,2])       # Média do canal Value (luminosidade)
        avg_saturation = np.mean(hsv_roi[:,:,1]) # Média do canal Saturation

        # Este limiar de saturação para cores neutras. Se a saturação é baixa, é neutro.
        # Aumentei para 40 para ser mais inclusivo com tons dessaturados que parecem cinza.
        if avg_saturation < 40: # Ajustado de 30 para 40
            if avg_value < 60:
                return "Preto"
            elif avg_value > 190: # Aumentei de 180 para 190 para ser mais rigoroso com o branco puro.
                return "Branco"
            else:
                return "Cinza" # Padrão para saturação baixa e valor intermediário

    # Corrige a detecção de "Vermelho2" para "Vermelho" no retorno final, se foi a parte detectada
    if detected_color == "Vermelho2":
        return "Vermelho"

    return detected_color