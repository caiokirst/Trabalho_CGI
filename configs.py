import numpy as np

# --- Configurações do Vídeo ---
VIDEO_PATH = 'estacionamento.mp4' 

# --- Vagas ---
PARKING_SPOTS = [
    {'id': 1, 'type': 'poly', 'coords': np.array([[(142, 510), (254, 189), (79, 184), (1, 354)]], np.int32)},
    {'id': 2, 'type': 'poly', 'coords': np.array([[285, 160], [173, 530], [480, 528], [450, 160]], np.int32)},
    {'id': 3, 'type': 'poly', 'coords': np.array([[480, 160], [523, 526], [861, 517], [636, 160]], np.int32)},
    {'id': 4, 'type': 'poly', 'coords': np.array([[957, 166], [659, 166], [880, 527], [957, 535]], np.int32)}
]

# --- Máscara de Região de Interesse (ROI) ---
PARKING_AREA_MASK_COORDS = np.array([[2, 500], [2, 160], [957, 160], [957, 500]], np.int32)

# S_MIN_FILTER: Saturação mínima para um pixel ser considerado na análise de cor.
#               Pixels com saturação abaixo disso (e brilho abaixo de V_MIN_FILTER) são ignorados.
#               Aumente se vidros ainda causarem problemas. Diminua se a pintura for muito dessaturada.
S_MIN_FILTER_COLOR_ANALYSIS = 30 # Saturação mínima para análise de cor (era 30)

# V_MIN_FILTER: Brilho (Valor) mínimo para um pixel ser considerado na análise de cor.
#               Pixels com brilho abaixo disso (e saturação abaixo de S_MIN_FILTER) são ignorados.
#               Aumente se vidros/sombras ainda causarem problemas. Diminua se a pintura for muito escura.
V_MIN_FILTER_COLOR_ANALYSIS = 80 # Brilho mínimo para análise de cor (era 80)


KNOWN_COLORS_BGR = {
    "Branco": (97, 91, 91),  
    "Preto": (113, 115, 115),      # <-- Ajustado para o valor real do carro preto!
    "Cinza": (110, 97, 95),   
    "Vermelho": (84, 97, 114),
    "Azul": (115, 99, 95),      
}

# --- Pré-processamento de Imagem ---
GAUSSIAN_BLUR_KERNEL_SIZE = (7, 7)
GAUSSIAN_BLUR_SIGMA_X = 0

# --- Detecção de Bordas (Canny) ---
CANNY_THRESHOLD1 = 30
CANNY_THRESHOLD2 = 60

# --- Fechamento de Bordas (Morph Close) ---
CLOSE_KERNEL_SIZE = (5, 5)
CLOSE_ITERATIONS = 2

# --- Filtragem de Contornos ---
MIN_CAR_AREA = 2000
MAX_CAR_AREA = 100000
MIN_ASPECT_RATIO = 0.30
MAX_ASPECT_RATIO = 4

# --- Interseção Vaga-Carro ---
MIN_INTERSECTION_AREA_PERCENT_POLY = 0.01
CAR_ROI_PADDING = 10

# --- Estabilidade Temporal ---
CONSECUTIVE_FRAMES_THRESHOLD = 3
