import cv2
import numpy as np

# Importa configurações
from configs import (VIDEO_PATH, PARKING_SPOTS, COLOR_RANGES_HSV,
                    CANNY_THRESHOLD1, CANNY_THRESHOLD2,
                    GAUSSIAN_BLUR_KERNEL_SIZE, GAUSSIAN_BLUR_SIGMA_X,
                    CLOSE_KERNEL_SIZE, CLOSE_ITERATIONS,
                    MIN_CAR_AREA, MAX_CAR_AREA, MIN_ASPECT_RATIO, MAX_ASPECT_RATIO,
                    MIN_INTERSECTION_AREA_PERCENT_POLY, CAR_ROI_PADDING,
                    PARKING_AREA_MASK_COORDS, CONSECUTIVE_FRAMES_THRESHOLD)

from utils import get_car_color

def initialize_video_capture(video_path):
    cap = cv2.VideoCapture(video_path)
    cv2.waitKey(100)
    if not cap.isOpened() or not cap.read()[0]:
        print(f"Erro ao abrir vídeo em {video_path}")
        exit()
    return cv2.VideoCapture(video_path)

def find_car_contours(source_image_for_canny):
    canny_edges = cv2.Canny(source_image_for_canny, CANNY_THRESHOLD1, CANNY_THRESHOLD2)
    close_kernel = np.ones(CLOSE_KERNEL_SIZE, np.uint8)
    closed_edges = cv2.morphologyEx(canny_edges, cv2.MORPH_CLOSE, close_kernel, iterations=CLOSE_ITERATIONS)
    
    roi_mask_general = np.zeros(source_image_for_canny.shape[:2], dtype=np.uint8)
    cv2.fillPoly(roi_mask_general, [PARKING_AREA_MASK_COORDS], 255)
    closed_edges_final = cv2.bitwise_and(closed_edges, closed_edges, mask=roi_mask_general)

    contours, _ = cv2.findContours(closed_edges_final, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, canny_edges, closed_edges_final

def draw_vaga_status(display_frame, vaga_data, status_color_box, status_text):
    vaga_coords = vaga_data['coords']
    vaga_id = vaga_data['id']

    # Desenha a vaga
    cv2.polylines(display_frame, [vaga_coords], isClosed=True, color=status_color_box, thickness=2)

    texto_vagas = {
        1: (30, 150),
        2: (270, 150),
        3: (510, 150),
        4: (750, 150),
      
    }
    
    # Desenha o texto de status na vaga
    pt_texto = texto_vagas.get(vaga_id, vaga_coords[0])  
    cv2.putText(display_frame, status_text, pt_texto,
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color_box, 2, cv2.LINE_AA)

cap = initialize_video_capture(VIDEO_PATH)
print("Pressione 'q' para sair.")
consecutive_occupied_frames_count = [0] * len(PARKING_SPOTS)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fim do vídeo.")
        break

    frame = cv2.resize(frame, (960, 540))
    display_frame = frame.copy()

    roi_mask_general = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(roi_mask_general, [PARKING_AREA_MASK_COORDS], 255)
    masked_display_frame = cv2.bitwise_and(display_frame, display_frame, mask=roi_mask_general)

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_image, GAUSSIAN_BLUR_KERNEL_SIZE, GAUSSIAN_BLUR_SIGMA_X)
    source_for_canny = cv2.bitwise_and(blurred, blurred, mask=roi_mask_general)

    contours, canny_edges_debug, closed_edges_debug = find_car_contours(source_for_canny)
    vagas_livres_count = len(PARKING_SPOTS)

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
            # DEBUG: Imprime a área e a proporção para ajudar a ajustar os limiares 
            #print(f"Contorno - Área: {area:.2f}, Proporção: {aspect_ratio:.2f}") 
            
            # Verifica se o contorno é um carro com base na área e proporção
            if (MIN_CAR_AREA < area < MAX_CAR_AREA) and (MIN_ASPECT_RATIO < aspect_ratio < MAX_ASPECT_RATIO):
                cv2.rectangle(masked_display_frame, (x_cnt, y_cnt), (x_cnt + w_cnt, y_cnt + h_cnt), (255, 0, 0), 2)

                car_contour_mask = np.zeros(closed_edges_debug.shape, dtype=np.uint8)
                cv2.drawContours(car_contour_mask, [cnt], -1, 255, -1)
                intersection_mask = cv2.bitwise_and(vaga_specific_mask, car_contour_mask)
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
                    #print(car_roi)
                    break

        if current_frame_is_occupied:
            consecutive_occupied_frames_count[i] += 1
        else:
            consecutive_occupied_frames_count[i] = 0

        if consecutive_occupied_frames_count[i] >= CONSECUTIVE_FRAMES_THRESHOLD:
            color_box = (0, 0, 255)
            vagas_livres_count -= 1
            text_to_show = f"Vaga {vaga_id} - {detected_car_color}"
        else:
            color_box = (0, 255, 0)
            text_to_show = f"Vaga {vaga_id} - Livre"

        draw_vaga_status(masked_display_frame, vaga_data, color_box, text_to_show)

    total_vagas = len(PARKING_SPOTS)
    cv2.putText(masked_display_frame, f'Vagas Livres: {vagas_livres_count}/{total_vagas}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

    cv2.imshow('Estacionamento Inteligente', masked_display_frame)
    cv2.imshow('Canny Edges (Debug)', canny_edges_debug)
    cv2.imshow('Closed Edges (Debug)', closed_edges_debug)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
