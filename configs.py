import numpy as np

# --- Configurações do Vídeo ---
VIDEO_PATH = 'estacionamento.mp4' 

# --- Vagas ---
PARKING_SPOTS = [
    {'id': 1, 'type': 'poly', 'coords': np.array([(59, 174), (228, 171), (160, 521), (1, 458)], np.int32)},
    {'id': 2, 'type': 'poly', 'coords': np.array([[285, 160], [173, 530], [480, 528], [450, 160]], np.int32)},
    {'id': 3, 'type': 'poly', 'coords': np.array([[480, 160], [523, 526], [861, 517], [636, 160]], np.int32)},
    {'id': 4, 'type': 'poly', 'coords': np.array([[957, 166], [659, 166], [880, 527], [957, 535]], np.int32)}
]

# --- Máscara de Região de Interesse (ROI) ---
PARKING_AREA_MASK_COORDS = np.array([[2, 537], [2, 160], [957, 160], [957, 538]], np.int32)

# --- Faixas de Cor HSV para Detecção de Cor de Carros ---
COLOR_RANGES_HSV = {
    "Branco": ([0, 0, 180], [180, 30, 255]),      
    "Preto": ([0, 0, 0], [180, 255, 50]),         
    "Cinza": ([0, 0, 50], [180, 60, 200]),        

    "Vermelho": ([0, 50, 20], [10, 255, 255]),   # S_min de 80 para 50 (Vermelho)
    "Vermelho2": ([170, 50, 20], [180, 255, 255]),# S_min de 80 para 50 (Vermelho2)

    "Azul": ([100, 50, 20], [140, 255, 255]),     # S_min de 80 para 50 (Azul)
    "Verde": ([40, 50, 20], [80, 255, 255]),      # S_min de 80 para 50 (Verde)
    "Amarelo": ([20, 50, 20], [35, 255, 255]),    # S_min de 80 para 50 (Amarelo)
    "Laranja": ([10, 50, 20], [25, 255, 255]),    # S_min de 80 para 50 (Laranja)
}

# --- Pré-processamento de Imagem ---
GAUSSIAN_BLUR_KERNEL_SIZE = (7, 7)
GAUSSIAN_BLUR_SIGMA_X = 0

# --- Detecção de Bordas (Canny) ---
CANNY_THRESHOLD1 = 30
CANNY_THRESHOLD2 = 60

# --- Fechamento de Bordas (Morph Close) ---
CLOSE_KERNEL_SIZE = (3, 3)
CLOSE_ITERATIONS = 4

# --- Filtragem de Contornos ---
MIN_CAR_AREA = 2000
MAX_CAR_AREA = 100000
MIN_ASPECT_RATIO = 0.3
MAX_ASPECT_RATIO = 6

# --- Interseção Vaga-Carro ---
MIN_INTERSECTION_AREA_PERCENT_POLY = 0.01
CAR_ROI_PADDING = 10

# --- Estabilidade Temporal ---
CONSECUTIVE_FRAMES_THRESHOLD = 5
