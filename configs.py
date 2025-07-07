# configs.py
import numpy as np

# --- Configurações Básicas do Vídeo ---
VIDEO_PATH = 'estacionamento.mp4' 

# --- Definição das Vagas do Estacionamento ---
# *** CRÍTICO: REFAZER COM EXTREMA PRECISÃO usando 'get_vaga_coords.py' ***
# As coordenadas abaixo são as últimas que você forneceu. Elas DEVEM ser revisadas e refeitas.
PARKING_SPOTS = [
    {'id': 1, 'type': 'poly', 'coords': np.array([(59, 174), (228, 171), (160, 521), (1, 458)], np.int32)},
    {'id': 2, 'type': 'poly', 'coords': np.array([[285, 160], [173, 530], [480, 528], [450, 160]], np.int32)},
    {'id': 3, 'type': 'poly', 'coords': np.array([[480, 160], [523, 526], [861, 517], [636, 160]], np.int32)},
    {'id': 4, 'type': 'poly', 'coords': np.array([[957, 166], [659, 166], [880, 527], [957, 535]], np.int32)}
]

# --- Definição da Máscara de Região de Interesse (ROI) Geral do Estacionamento ---
# Esta área poligonal define a região do frame que o programa irá analisar.
# *** CRÍTICO: REFAZER COM EXTREMA PRECISÃO usando 'get_vaga_coords.py' ***
PARKING_AREA_MASK_COORDS = np.array([[2, 537], [2, 160], [957, 160], [957, 538]], np.int32) 

# --- Definição das Faixas de Cor HSV ---
# Ajustes para cobrir variações de tons. Teste com carros reais no vídeo.
COLOR_RANGES_HSV = {
    "Branco": ([0, 0, 180], [180, 30, 255]),      
    "Preto": ([0, 0, 0], [180, 255, 50]),         
    "Cinza": ([0, 0, 50], [180, 60, 200]),        
    "Vermelho": ([0, 120, 70], [10, 255, 255]),   
    "Vermelho2": ([170, 120, 70], [180, 255, 255]),
    "Azul": ([100, 150, 0], [140, 255, 255]),     
    "Verde": ([40, 70, 50], [80, 255, 255]),      
    "Amarelo": ([20, 100, 100], [35, 255, 255]),  
    "Laranja": ([10, 100, 100], [25, 255, 255]), 
}

# --- Parâmetros de Pré-processamento de Imagem (A ordem de aplicação é importante no main.py) ---

# Ajuste de Brilho e Contraste Linear
APPLY_LINEAR_BRIGHTNESS_CONTRAST = False # Ative APENAS se o CLAHE não for suficiente ou introduzir artefatos.
LINEAR_ALPHA = 1.2                       # Contraste (1.0 = original, >1.0 = mais)
LINEAR_BETA = 10                         # Brilho (0 = original, >0 = mais)

# Equalização de Histograma Adaptativa (CLAHE): Ótimo para iluminação irregular.
APPLY_CLAHE = False                       # ATIVAR. Ajuda a melhorar o contraste localmente.
CLAHE_CLIP_LIMIT = 1.2                   # Limite de contraste (evita amplificar ruído).
CLAHE_TILE_GRID_SIZE = (8, 8)            # Tamanho da grade (8,8) é um bom começo.

# Desfoque Gaussiano: Suaviza ruídos e textura (tijolos) antes do Canny.
GAUSSIAN_BLUR_KERNEL_SIZE = (7, 7)       # Kernel ímpar positivo. Ajustar para balanço.
GAUSSIAN_BLUR_SIGMA_X = 0                # 0 = calcula automaticamente.

# Limiar Simples (Thresholding): Geralmente não é o ideal para detecção de bordas em cenas variadas.
APPLY_SIMPLE_THRESHOLD = False           # Manter DESATIVADO.
SIMPLE_THRESHOLD_VALUE = 70              
SIMPLE_THRESHOLD_MAX_VALUE = 255

# --- Parâmetros para Detecção de Bordas (Canny) ---
# minVal, maxVal: Limiares de histerese do Canny.
# Ajuste: Se a Canny Edges (Debug) estiver preta (nenhuma borda), DIMINUA estes valores.
# Se estiver com muito ruído dos tijolos (bordas demais), AUMENTE estes valores.
# Tente um valor que capture as bordas de TODOS os carros.
CANNY_THRESHOLD1 = 30     
CANNY_THRESHOLD2 = 60                 

# --- Parâmetros para Fechamento de Bordas (Operação Morfológica MORPH_CLOSE) ---
# CRÍTICO para conectar bordas fragmentadas e fazer os carros aparecerem como formas sólidas.
# Kernel maior e/ou mais iterações fecham buracos maiores.
# Observe a 'Closed Edges (Debug)'. Os carros devem ser sólidos e compactos lá.
CLOSE_KERNEL_SIZE = (3,3)             # Kernel ímpar positivo.
CLOSE_ITERATIONS = 4                 # Número de vezes que a operação é aplicada.

# --- Parâmetros para Filtragem de Contornos (Identificação de Carros) ---
# Contornos detectados são filtrados por área e proporção para serem considerados "carros".
# Ajuste com base nos prints de debug (Contorno - Área, Proporção).
MIN_CAR_AREA = 2000                      # Ajustado para capturar carros menores/distantes.
MAX_CAR_AREA = 100000                  # Área máxima do contorno de um carro.
MIN_ASPECT_RATIO = 0.3                # Proporção mínima (largura/altura).
MAX_ASPECT_RATIO = 6                  # Proporção máxima (largura/altura).

# --- Parâmetros para Interseção de Vagas e Detecção de Ocupação ---
# Porcentagem da área da vaga que um contorno de carro deve cobrir para ser considerada ocupada.
# Se carros detectados (com bounding box azul) não marcam a vaga como vermelha, DIMINUA este valor.
MIN_INTERSECTION_AREA_PERCENT_POLY = 0.01 # Tolerância de 15% de sobreposição.

# Padding adicionado ao retângulo delimitador (bounding box) do carro.
# Ajuda a garantir que a ROI da cor e a interseção com a vaga sejam precisas.
CAR_ROI_PADDING = 0

# --- Parâmetros para Filtragem Temporal (Estabilidade) ---
# Número de frames consecutivos que uma vaga precisa ser detectada como ocupada antes de mudar de status.
# Crucial para evitar "piscadas" e tornar o programa estável.
CONSECUTIVE_FRAMES_THRESHOLD = 5 # Sugiro 3 a 5 para uma boa estabilidade.