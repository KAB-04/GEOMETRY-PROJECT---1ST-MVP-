from math import sqrt, pi


def calculate_distance(x1, y1, x2, y2):
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calculate_circle_area(radius):
    return pi * radius ** 2
