import cv2
import numpy as np

# Caminho para o seu arquivo de vídeo
VIDEO_PATH = 'estacionamento.mp4'

# Lista temporária para armazenar os pontos clicados para uma vaga poligonal
current_polygon_points = []
# Lista para armazenar todas as vagas definidas (como retângulos ou polígonos)
defined_parking_spots = []
# ID para as vagas
vaga_id_counter = 1

# Variável para armazenar a posição atual do mouse para o desenho temporário
temp_mouse_pos = (0, 0)

# Função de callback para eventos do mouse
def mouse_callback(event, x, y, flags, param):
    global current_polygon_points, defined_parking_spots, vaga_id_counter, temp_mouse_pos

    temp_mouse_pos = (x, y) # Atualiza a posição do mouse para desenho temporário

    if event == cv2.EVENT_LBUTTONDOWN:
        current_polygon_points.append((x, y))
        print(f"Ponto adicionado para Vaga {vaga_id_counter}: ({x}, {y})")

        # Se 4 pontos foram clicados, consideramos a vaga poligonal completa
        if len(current_polygon_points) == 4:
            # Converte a lista de tuplas para um array NumPy (formato exigido por cv2.fillPoly/polylines)
            poly_coords = np.array(current_polygon_points, np.int32)
            
            defined_parking_spots.append({
                'id': vaga_id_counter,
                'type': 'poly',
                'coords': poly_coords
            })
            print(f"Vaga {vaga_id_counter} (Polígono) definida: {current_polygon_points}")
            
            current_polygon_points = [] # Reseta para a próxima vaga
            vaga_id_counter += 1

# Carrega o primeiro frame do vídeo para definir as vagas
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print(f"Erro: Não foi possível abrir o vídeo em {VIDEO_PATH}")
    exit()

ret, frame = cap.read()
if not ret:
    print("Erro: Não foi possível ler o primeiro frame do vídeo.")
    cap.release()
    exit()

# Redimensiona o frame para o mesmo tamanho que será usado no main.py
frame = cv2.resize(frame, (960, 540))
clone_frame = frame.copy() # Cria uma cópia para desenhar e manter o original

cv2.namedWindow('Definir Vagas - Clique nos 4 cantos. Pressione R para resetar, Q para sair.')
cv2.setMouseCallback('Definir Vagas - Clique nos 4 cantos. Pressione R para resetar, Q para sair.', mouse_callback)

print("\nInstruções para definir vagas poligonais (4 pontos):")
print("1. Para cada vaga, clique nos SEUS 4 CANTOS (em qualquer ordem, mas consistente ajuda).")
print("2. Após o 4º clique, a vaga será definida.")
print("3. Repita para todas as vagas. Se algumas forem retangulares, use 4 cliques para elas também.")
print("4. Pressione 'R' para resetar todas as vagas definidas.")
print("5. Pressione 'Q' para sair. As coordenadas serão impressas no console.")

while True:
    display_frame = clone_frame.copy()

    # Desenha os pontos temporários e a linha para o polígono em construção
    if len(current_polygon_points) > 0:
        for i, point in enumerate(current_polygon_points):
            cv2.circle(display_frame, point, 5, (0, 255, 255), -1) # Pontos amarelos
            if i > 0:
                cv2.line(display_frame, current_polygon_points[i-1], point, (0, 0, 255), 2) # Linhas vermelhas
        # Desenha a linha do último ponto clicado até a posição atual do mouse
        if len(current_polygon_points) < 4:
            cv2.line(display_frame, current_polygon_points[-1], temp_mouse_pos, (0, 0, 255), 2)

    # Desenha as vagas já definidas
    for vaga in defined_parking_spots:
        if vaga['type'] == 'poly':
            # Nota: cv2.polylines espera uma lista de arrays, mesmo para um único polígono
            cv2.polylines(display_frame, [vaga['coords']], isClosed=True, color=(0, 255, 0), thickness=2) # Verde
            cv2.putText(display_frame, f"Vaga {vaga['id']}", tuple(vaga['coords'][0] + np.array([0, -10])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
    cv2.imshow('Definir Vagas - Clique nos 4 cantos. Pressione R para resetar, Q para sair.', display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        defined_parking_spots = []
        current_polygon_points = []
        vaga_id_counter = 1
        print("Vagas resetadas.")

cv2.destroyAllWindows()
cap.release()

print("\n--- COORDENADAS DAS VAGAS DEFINIDAS (Copie para o seu código principal) ---")
for vaga in defined_parking_spots:
    # A saída agora é um array NumPy, então usamos tolist() para impressão e depois convertemos de volta
    print(f"{{'id': {vaga['id']}, 'type': 'poly', 'coords': np.array({vaga['coords'].tolist()}, np.int32)}},")
print("--------------------------------------------------------------------------")