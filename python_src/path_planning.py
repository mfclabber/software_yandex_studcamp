import heapq
from test_move import RobotDirection
import time


rd = RobotDirection()
class Graph:
    def __init__(self):
        self.edges = {}

    def add_edge(self, from_node, to_node, weight=1):
        # Добавляем ребро в обе стороны, так как это неориентированный граф
        if from_node not in self.edges:
            self.edges[from_node] = []
        if to_node not in self.edges:
            self.edges[to_node] = []
        self.edges[from_node].append((to_node, weight))
        self.edges[to_node].append((from_node, weight))

def dijkstra(graph, start):
    # Алгоритм Дейкстры
    distances = {node: float('infinity') for node in graph.edges}
    distances[start] = 0
    priority_queue = [(0, start)]
    previous_nodes = {node: None for node in graph.edges}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph.edges[current_node]:
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, previous_nodes

def shortest_path(graph, start, end):
    distances, previous_nodes = dijkstra(graph, start)
    path = []
    current_node = end

    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes[current_node]

    path = path[::-1]  # Разворачиваем путь
    return path

# Определяем направление движения робота
DIRECTIONS = ['N', 'E', 'S', 'W']  # Север, Восток, Юг, Запад

class Robot:
    def __init__(self, start_direction='N'):
        self.direction = start_direction

    def turn_left(self):
        rd.forward_with_angle(50,100)
        time.sleep(0.7)
        # rd.stop()
        # time.sleep(1)
        current_index = DIRECTIONS.index(self.direction)
        self.direction = DIRECTIONS[(current_index - 1) % 4]
        print("Turned left. Now facing:", self.direction)

    def turn_right(self):
        rd.forward_with_angle(50,-100)
        time.sleep(0.7)
        # rd.stop()
        # time.sleep(1)
        current_index = DIRECTIONS.index(self.direction)
        self.direction = DIRECTIONS[(current_index + 1) % 4]
        print("Turned right. Now facing:", self.direction)

    def go_forward(self):
        print("Moved forward while facing:", self.direction)
        rd.stop()
        rd.forward_with_angle(70,0)
        time.sleep(2)
        # rd.stop()

    def execute_path(self, path, positions):
        # positions содержит координаты клеток в формате (x, y)
        for i in range(1, len(path)):
            current_pos = positions[path[i - 1]]
            next_pos = positions[path[i]]

            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]

            if dx == 1:  # Движение на восток
                desired_direction = 'E'
            elif dx == -1:  # Движение на запад
                desired_direction = 'W'
            elif dy == 1:  # Движение на север
                desired_direction = 'N'
            elif dy == -1:  # Движение на юг
                desired_direction = 'S'

            while self.direction != desired_direction:
                if DIRECTIONS.index(self.direction) - DIRECTIONS.index(desired_direction) == 1 or \
                   (self.direction == 'N' and desired_direction == 'W'):
                    self.turn_left()
                else:
                    self.turn_right()

            self.go_forward()

# Пример использования

# Создаем лабиринт в виде графа
# graph = Graph()

# # Добавляем ребра (переходы между клетками лабиринта)
# # Предположим, что клетки пронумерованы от 0 до 5 и соединены следующим образом:
# graph.add_edge(1, 2)
# graph.add_edge(1, 6)
# graph.add_edge(2, 3)
# graph.add_edge(3, 4)
# graph.add_edge(4, 5)
# graph.add_edge(5, 10)
# graph.add_edge(6, 11)
# graph.add_edge(7, 8)
# graph.add_edge(7, 12)
# graph.add_edge(8, 9)
# graph.add_edge(8, 13)
# graph.add_edge(9, 14)
# graph.add_edge(10, 15)
# graph.add_edge(11, 12)
# graph.add_edge(11, 16)
# graph.add_edge(12, 17)
# graph.add_edge(13, 18)
# graph.add_edge(14, 15)
# graph.add_edge(14, 19)
# graph.add_edge(15, 20)
# graph.add_edge(16, 21)
# graph.add_edge(17, 18)
# graph.add_edge(18, 19)
# graph.add_edge(20, 25)
# graph.add_edge(21, 22)
# graph.add_edge(22, 23)
# graph.add_edge(23, 24)
# graph.add_edge(24, 25)

# # Задаем позиции клеток лабиринта на плоскости
# positions = {
#     1: (0, 0),
#     2: (1, 0),
#     3: (2, 0),
#     4: (3, 0),
#     5: (4, 0),
#     6: (0, 1),
#     7: (1, 1),
#     8: (2, 1),
#     9: (3, 1),
#     10: (4, 1),
#     11: (0, 2),
#     12: (1, 2),
#     13: (2, 2),
#     14: (3, 2),
#     15: (4, 2),
#     16: (0, 3),
#     17: (1, 3),
#     18: (2, 3),
#     19: (3, 3),
#     20: (4, 3),
#     21: (0, 4),
#     22: (1, 4),
#     23: (2, 4),
#     24: (3, 4),
#     25: (4, 4)
# }

# # Находим кратчайший путь из клетки 0 в клетку 5
# path = shortest_path(graph, 21, 13)
# print("Shortest path:", path)

# # Создаем робота и заставляем его пройти по кратчайшему пути
# robot = Robot(start_direction='S')
# robot.execute_path(path, positions)
