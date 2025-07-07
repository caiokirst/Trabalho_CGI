# configs.py
import numpy as np

# --- Configurações Básicas ---
# Caminho para o seu arquivo de vídeo.
# Certifique-se de que 'estacionamento.mp4' está na mesma pasta do seu script main.py,
# ou forneça o caminho completo para o arquivo.
VIDEO_PATH = 'estacionamento.mp4' 

# --- DEFINIÇÃO DAS VAGAS ESPECÍFICAS (Polígonos) ---
# IMPORTANTE: Estas coordenadas são EXEMPLOS APROXIMADOS.
# Você DEVE usar o script 'get_vaga_coords.py' para obter as coordenadas precisas
# para CADA vaga no SEU VÍDEO e SUBSTITUIR esta lista.
# Formato para vagas poligonais: np.array([[x1, y1], [x2, y2], ...], np.int32)
PARKING_SPOTS = [
    # Exemplo (substitua por suas coordenadas reais do get_vaga_coords.py):
    {'id': 1, 'type': 'poly', 'coords': np.array([(120, 528), (240, 229), (86, 182), (1, 310)], np.int32)},
    {'id': 2, 'type': 'poly', 'coords': np.array([(297, 136), (186, 529), (523, 528), (461, 128)], np.int32)},
    {'id': 3, 'type': 'poly', 'coords': np.array([(477, 124), (551, 525), (883, 514), (634, 128)], np.int32)},
    {'id': 4, 'type': 'poly', 'coords': np.array([(658, 184), (865, 156), (957, 217), (939, 531)], np.int32)}
]

# --- DEFINIÇÃO DA MÁSCARA DA ÁREA DE INTERESSE (ROI) GERAL DO ESTACIONAMENTO ---
# Esta é a área poligonal que o programa vai analisar, ignorando tudo fora dela (ex: rua ao fundo).
# Use o script get_vaga_coords.py para obter essas coordenadas.
PARKING_AREA_MASK_COORDS = np.array([[2, 537], [2, 159], [959, 116], [957, 538]], np.int32) 

# --- DEFINIÇÃO DAS FAIXAS DE COR HSV ---
# Estes valores são estimativas e podem precisar de ajuste fino!
# A iluminação do vídeo, reflexos e tons específicos de veículos afetam a precisão.
# Use ferramentas online (ex: "HSV Color Picker" ou "RGB to HSV converter") para obter faixas mais precisas se necessário.
# Formato: "Nome da Cor": ([H_min, S_min, V_min], [H_max, S_max, V_max])
COLOR_RANGES_HSV = {
    "Branco": ([0, 0, 180], [180, 20, 255]),      # Tons claros, baixa saturação
    "Preto": ([0, 0, 0], [180, 255, 40]),         # Tons escuros, qualquer saturação
    "Cinza": ([0, 0, 40], [180, 50, 180]),        # Tons médios, baixa saturação
    "Vermelho": ([0, 120, 70], [10, 255, 255]),   # Parte 1 do Vermelho (HUE 0-10)
    "Vermelho2": ([170, 120, 70], [180, 255, 255]),# Parte 2 do Vermelho (HUE 170-180)
    "Azul": ([100, 150, 0], [140, 255, 255]),     # Faixa para tons de azul
    "Verde": ([40, 70, 50], [80, 255, 255]),      # Faixa para tons de verde
    "Amarelo": ([20, 100, 100], [35, 255, 255]),  # Faixa para tons de amarelo
    "Laranja": ([10, 100, 100], [25, 255, 255]), # Faixa para tons de laranja
    # Adicione ou ajuste outras cores conforme necessário (ex: Marrom, Roxo, Prata)
}

# --- PARÂMETROS DO BACKGROUND SUBTRACTOR (MOG2) ---
# Estes parâmetros não são usados para a detecção PRINCIPAL de carros (que agora é por bordas),
# mas podem ser mantidos para depuração ou uso secundário.
MOG2_VAR_THRESHOLD = 40
MOG2_HISTORY = 300
MOG2_DETECT_SHADOWS = True

# --- PARÂMETROS PARA AJUSTE DE BRILHO E CONTRASTE LINEAR ---
# Ative/desative (True/False) em main.py se quiser experimentar.
APPLY_LINEAR_BRIGHTNESS_CONTRAST = False # Mudar para True para ativar
# alpha: Controle de contraste (1.0 = original, >1.0 = mais contraste, <1.0 = menos)
LINEAR_ALPHA = 1.2
# beta: Controle de brilho (0 = original, >0 = mais brilho, <0 = menos)
LINEAR_BETA = 10

# --- PARÂMETROS PARA EQUALIZAÇÃO DE HISTOGRAMA (CLAHE) ---
# Ative/desative (True/False) em main.py se quiser experimentar.
APPLY_CLAHE = False # Mudar para True para ativar
# clipLimit: Limite de contraste para a equalização (evita amplificação de ruído).
CLAHE_CLIP_LIMIT = 2.0
# tileGridSize: Tamanho da grade para a equalização adaptativa (divide a imagem em blocos).
CLAHE_TILE_GRID_SIZE = (8, 8)

# --- PARÂMETROS PARA PRÉ-PROCESSAMENTO (ANTES DE CANNY) ---
# Kernel para desfoque Gaussiano. Maior = mais agressivo, ajuda a remover textura (tijolos).
# Deve ser um número ímpar positivo. SigmaX=0 calcula automaticamente.
# Ajuste: Se ainda tiver muito ruído de fundo, AUMENTE. Se bordas de carros sumirem, DIMINUA.
GAUSSIAN_BLUR_KERNEL_SIZE = (7, 7) # Ajuste: ex: (5,5), (9,9), (11,11)
GAUSSIAN_BLUR_SIGMA_X = 0         

# Opcional: Aplicar limiar simples antes do Canny. Pode ajudar a isolar objetos.
# Ative/desative (True/False) em main.py se quiser experimentar.
APPLY_SIMPLE_THRESHOLD = False 
SIMPLE_THRESHOLD_VALUE = 120    # Valor do limiar (0 a 255). Ajuste se ativado.
SIMPLE_THRESHOLD_MAX_VALUE = 255

# --- PARÂMETROS PARA DETECÇÃO DE BORDAS COM CANNY ---
# minVal, maxVal: Limiares de histerese para o algoritmo Canny.
# Ajuste: Se a Canny Edges (Debug) estiver preta (nenhuma borda), DIMINUA estes valores.
# Se estiver com muito ruído dos tijolos (bordas demais), AUMENTE estes valores.
CANNY_THRESHOLD1 = 30   # Ajuste: ex: 5, 10, 30, 40
CANNY_THRESHOLD2 = 60   # Ajuste: ex: 15, 30, 90, 120

# --- PARÂMETROS PARA FECHAMENTO DE BORDAS (MORPH_CLOSE) ---
# CRÍTICO para conectar bordas fragmentadas e fazer os carros aparecerem como formas sólidas.
# Kernel maior e/ou mais iterações fecham buracos maiores.
# Observe a 'Closed Edges (Debug)'. Os carros devem ser sólidos lá.
CLOSE_KERNEL_SIZE = (13, 13) # Ajuste: ex: (9,9), (11,11), (15,15)
CLOSE_ITERATIONS = 3       # Ajuste: ex: 2, 4, 5

# --- PARÂMETROS DE FILTRAGEM DE CONTORNOS (PARA IDENTIFICAR APENAS CARROS) ---
# Ajuste com base nos valores de área e proporção (aspect_ratio) que você vê no console
# (descomente o print no main.py).
# ESTES SÃO OS MAIS IMPORTANTES PARA AJUSTAR AGORA!
MIN_CAR_AREA = 7500     # Áreas menores que isso provavelmente são ruído ou pessoas. Ajuste com base nos seus prints!
MAX_CAR_AREA = 100000    # Áreas maiores que isso são provavelmente ruído grande ou múltiplos objetos. Ajuste com base nos seus prints!
MIN_ASPECT_RATIO = 0.8  # Carros tendem a ser mais largos ou tão largos quanto altos. Ajuste com base nos seus prints!
MAX_ASPECT_RATIO = 6.0  # Para carros muito longos ou em ângulos extremos. Ajuste com base nos seus prints!

# --- PARÂMETROS DE INTERSEÇÃO DA VAGA ---
# Porcentagem da área da vaga que um contorno (carro detectado) deve cobrir para ser considerado como ocupante.
# Se carros detectados (bounding box azul) não marcam a vaga como vermelha, DIMINUA este valor.
MIN_INTERSECTION_AREA_PERCENT_POLY = 0.05  # Ajuste: ex: 0.1, 0.2, 0.3

# Padding adicionado ao retângulo delimitador (bounding box) do carro.
# Isso ajuda a garantir que a ROI do carro cubra bem o veículo para análise de cor e que
# a interseção com a vaga seja calculada de forma mais abrangente.
CAR_ROI_PADDING = 25

# --- PARÂMETROS PARA FILTRAGEM TEMPORAL (ESTABILIDADE) ---
# Número de frames consecutivos que uma vaga precisa ser detectada como ocupada
# antes que seu status mude para vermelho. Isso evita piscadas.
CONSECUTIVE_FRAMES_THRESHOLD = 3 # Ex: 3 a 5 frames