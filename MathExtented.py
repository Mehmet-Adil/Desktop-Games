import pygame
import math


def sin_degrees(value: float) -> float:
    return math.sin(value * math.pi / 180)


def cos_degrees(value: float) -> float:
    return math.cos(value * math.pi / 180)


def get_angle_vector2(vector2: pygame.Vector2) -> float:
    return 180 + math.degrees(math.atan2(vector2.x, vector2.y))


def get_distance_of_two_points(from_: pygame.Vector2, to: pygame.Vector2) -> (pygame.Vector2, int):
    vector2_dist = to - from_
    dist = math.sqrt(abs(vector2_dist[0]) ** 2 + abs(vector2_dist[1]) ** 2)

    return vector2_dist, dist


def rotate_point(x: float, y: float, angle: float, offset_x: float = 0, offset_y: float = 0) -> (float, float):

    point_x, point_y = x + offset_x, y + offset_y
    pivot_x, pivot_y = x, y

    new_x = pivot_x + cos_degrees(-angle) * (point_x - pivot_x) - sin_degrees(-angle) * (point_y - pivot_y)
    new_y = pivot_y + sin_degrees(-angle) * (point_x - pivot_x) + cos_degrees(-angle) * (point_y - pivot_y)

    return new_x, new_y
