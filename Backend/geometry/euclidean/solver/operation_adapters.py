def triangle_area(base: float, height: float) -> float:
    if base <= 0 or height <= 0:
        raise ValueError("Triangle base and height must be positive.")
    return 0.5 * base * height


def triangle_perimeter(a: float, b: float, c: float) -> float:
    if a <= 0 or b <= 0 or c <= 0:
        raise ValueError("Triangle side lengths must be positive.")
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("Triangle side lengths must satisfy the triangle inequality.")
    return a + b + c


def triangle_third_angle(angle1: float, angle2: float) -> float:
    if angle1 <= 0 or angle2 <= 0:
        raise ValueError("Triangle angles must be positive.")
    if angle1 + angle2 >= 180:
        raise ValueError("Known triangle angles must sum to less than 180 degrees.")
    return 180 - angle1 - angle2


def midpoint(x1: float, y1: float, x2: float, y2: float) -> tuple:
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def slope(x1: float, y1: float, x2: float, y2: float) -> float:
    if x2 == x1:
        raise ValueError("Slope is undefined for a vertical line.")
    return (y2 - y1) / (x2 - x1)


def rectangle_area(length: float, width: float) -> float:
    if length <= 0 or width <= 0:
        raise ValueError("Rectangle dimensions must be positive.")
    return length * width


def rectangle_perimeter(length: float, width: float) -> float:
    if length <= 0 or width <= 0:
        raise ValueError("Rectangle dimensions must be positive.")
    return 2 * (length + width)


def transform(transformation: str, points: list, dx: float = 0, dy: float = 0) -> dict:
    from ..Math_Engine.transformations import _apply_named_transformation

    return _apply_named_transformation(transformation, points, dx, dy)


def distance3d(points: list) -> float:
    first, second = _two_3d_points(points)
    return ((second["x"] - first["x"]) ** 2 + (second["y"] - first["y"]) ** 2 + (second["z"] - first["z"]) ** 2) ** 0.5


def midpoint3d(points: list) -> dict:
    first, second = _two_3d_points(points)
    return {"type": "point3d", "x": (first["x"] + second["x"]) / 2, "y": (first["y"] + second["y"]) / 2, "z": (first["z"] + second["z"]) / 2}


def vector3d(points: list) -> dict:
    first, second = _two_3d_points(points)
    return {"from": [first["x"], first["y"], first["z"]], "to": [second["x"], second["y"], second["z"]]}


def triangle3d(points: list) -> dict:
    _require_3d_points(points, 3)
    return {"vertices": [point["id"] for point in points]}


def plane3d(points: list) -> dict:
    _require_3d_points(points, 3)
    return {"points": [{key: point[key] for key in ("x", "y", "z")} for point in points]}


def cuboid_volume(width: float, height: float, depth: float) -> float:
    if width <= 0 or height <= 0 or depth <= 0:
        raise ValueError("Cuboid dimensions must be positive.")
    return width * height * depth


def _two_3d_points(points):
    _require_3d_points(points, 2)
    return points[0], points[1]


def _require_3d_points(points, minimum):
    if not isinstance(points, list) or len(points) < minimum:
        raise ValueError(f"At least {minimum} 3-D points are required.")
    for point in points:
        if not isinstance(point, dict) or not isinstance(point.get("id"), str):
            raise ValueError("Each 3-D point requires an id, x, y, and z.")
        if not all(isinstance(point.get(axis), (int, float)) for axis in ("x", "y", "z")):
            raise ValueError("3-D point coordinates must be numeric.")
