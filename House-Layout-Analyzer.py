import cv2
import numpy as np
import json

def find_red_points(image_path):
    image = cv2.imread(image_path)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    red_points = []
    point_names = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 10:
            M = cv2.moments(contour)
            centroid_x = int(M["m10"] / M["m00"])
            centroid_y = int(M["m01"] / M["m00"])
            point_name = point_names[len(red_points)]
            red_points.append((point_name, centroid_x, centroid_y))
            cv2.circle(image, (centroid_x, centroid_y), 5, (0, 0, 255), -1)
            cv2.putText(image, point_name, (centroid_x+10, centroid_y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    walls = []
    for i in range(len(red_points)):
        for j in range(i+1, len(red_points)):
            x1, y1 = red_points[i][1:]
            x2, y2 = red_points[j][1:]
            if abs(x1 - x2) < 10:  # Проверяем вертикальную линию
                wall = [red_points[i], red_points[j]]
                walls.append(wall)
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            elif abs(y1 - y2) < 10:  # Проверяем горизонтальную линию
                wall = [red_points[i], red_points[j]]
                walls.append(wall)
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    rooms = []
    for wall1 in walls:
        for wall2 in walls:
            if wall1 != wall2:
                if abs(wall1[0][1] - wall1[1][1]) == abs(wall2[0][1] - wall2[1][1]) and abs(wall1[0][2] - wall1[1][2]) == abs(wall2[0][2] - wall2[1][2]):  # Проверка параллельности стен
                    if wall1[0][1] == wall1[1][1] and wall2[0][1] == wall2[1][1]:  # Проверка, что стены находятся на одной горизонтальной линии
                        room_points = [wall1[0], wall1[1], wall2[0], wall2[1]]
                        room = [(point_name, x, y) for point_name, x, y in red_points if (point_name, x, y) in room_points]
                        if len(room) == 4:  # Комната должна состоять из 4 точек
                            is_inside = False
                            for other_room in rooms:
                                if set(room).issubset(set(other_room)):
                                    is_inside = True
                                    break
                            if not is_inside:
                                rooms.append(room)

    # Сохраняем информацию о комнатах в JSON
    rooms_json = [{"Room": i+1, "Points": [(point_name, x, y) for point_name, x, y in room]} for i, room in enumerate(rooms)]
    with open('rooms_info.json', 'w') as f:
        json.dump(rooms_json, f, indent=4)

    cv2.imshow('Detected Rooms', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

image_path = 'tochka.jpg'
find_red_points(image_path)

# Функция для загрузки данных из JSON файла
def load_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Функция для сохранения данных в JSON файл
def save_data_to_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Пример использования функций
file_path = 'rooms_info.json'

# Загрузка данных из файла
shared_data = load_data_from_json(file_path)

# Изменение данных
shared_data.append({'new_key': 'new_value'})

# Сохранение обновленных данных в файл
save_data_to_json(shared_data, file_path)
