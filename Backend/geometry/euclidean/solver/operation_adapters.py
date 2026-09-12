from ..Math_Engine.Euclidean2 import Cone, Cylinder, Line3D, Plane3D, Point3D
import math


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
    return _point3d(first).distance_to(_point3d(second))


def midpoint3d(points: list) -> dict:
    first, second = _two_3d_points(points)
    return {"type": "point3d", "x": (first["x"] + second["x"]) / 2, "y": (first["y"] + second["y"]) / 2, "z": (first["z"] + second["z"]) / 2}


def vector3d(points: list) -> dict:
    first, second = _two_3d_points(points)
    return {"type": "vector3d", "from": _point_list(first), "to": _point_list(second)}


def line3d(points: list) -> dict:
    first, second = _two_3d_points(points)
    line = Line3D.from_two_points(_point3d(first), _point3d(second))
    return {
        "type": "line3d",
        "point": _point_to_dict(line.point),
        "direction": _point_to_dict(line.direction),
        "through": [first["id"], second["id"]],
    }


def triangle3d(points: list) -> dict:
    _require_3d_points(points, 3)
    return {"vertices": [point["id"] for point in points]}


def plane3d(points: list) -> dict:
    first, second, third = _require_3d_points(points, 3)
    plane = Plane3D.from_three_points(_point3d(first), _point3d(second), _point3d(third))
    return {
        "type": "plane",
        "point": _point_to_dict(plane.point),
        "normal": _point_to_dict(plane.normal),
        "points": [_point_to_dict(point) for point in points[:3]],
    }


def cuboid_volume(width: float, height: float, depth: float) -> float:
    if width <= 0 or height <= 0 or depth <= 0:
        raise ValueError("Cuboid dimensions must be positive.")
    return width * height * depth


def cylinder_volume(radius: float, height: float) -> float:
    _validate_cylinder_dimensions(radius, height)
    return Cylinder(radius, height).volume()


def cylinder_lateral_surface_area(radius: float, height: float) -> float:
    _validate_cylinder_dimensions(radius, height)
    return Cylinder(radius, height).lateral_area()


def cylinder_total_surface_area(radius: float, height: float) -> float:
    _validate_cylinder_dimensions(radius, height)
    return Cylinder(radius, height).total_area()


def _validate_cylinder_dimensions(radius, height):
    if radius <= 0 or height <= 0:
        raise ValueError("Cylinder radius and height must be positive.")


def cone_height_from_radius_slant_height(radius: float, slant_height: float) -> float:
    if radius <= 0 or slant_height <= 0:
        raise ValueError("Cone radius and slant height must be positive.")
    if slant_height <= radius:
        raise ValueError("Cone slant height must be greater than radius.")
    return math.sqrt(slant_height**2 - radius**2)


def cone_volume(radius: float, height: float) -> float:
    _validate_cone_dimensions(radius, height)
    return Cone(radius, height).volume()


def cone_lateral_surface_area(radius: float, height: float) -> float:
    _validate_cone_dimensions(radius, height)
    return Cone(radius, height).lateral_area()


def cone_total_surface_area(radius: float, height: float) -> float:
    _validate_cone_dimensions(radius, height)
    return Cone(radius, height).total_area()


def _validate_cone_dimensions(radius, height):
    if radius <= 0 or height <= 0:
        raise ValueError("Cone radius and height must be positive.")


def _two_3d_points(points):
    normalized = _require_3d_points(points, 2)
    return normalized[0], normalized[1]


def _require_3d_points(points, minimum):
    if not isinstance(points, list) or len(points) < minimum:
        raise ValueError(f"At least {minimum} 3-D points are required.")
    return [_normalize_3d_point(point, index) for index, point in enumerate(points[:minimum])]


def _normalize_3d_point(point, index):
    point_id = chr(ord("A") + index)
    if isinstance(point, dict):
        if isinstance(point.get("id"), str) and point["id"].strip():
            point_id = point["id"].strip()
        values = [point.get(axis) for axis in ("x", "y", "z")]
    elif isinstance(point, (list, tuple)):
        if len(point) != 3:
            raise ValueError("3-D point arrays must contain exactly three coordinates.")
        values = list(point)
    else:
        raise ValueError("Each 3-D point must be an object or a three-coordinate array.")

    coordinates = [_coerce_numeric_coordinate(value) for value in values]
    return {"id": point_id, "x": coordinates[0], "y": coordinates[1], "z": coordinates[2]}


def _coerce_numeric_coordinate(value):
    if isinstance(value, bool):
        raise ValueError("3-D point coordinates must be numeric.")
    if isinstance(value, (int, float)):
        return value
    if not isinstance(value, str):
        raise ValueError("3-D point coordinates must be numeric.")

    stripped = value.strip()
    try:
        number = float(stripped)
    except ValueError as exc:
        raise ValueError("3-D point coordinates must be numeric.") from exc
    if not math.isfinite(number):
        raise ValueError("3-D point coordinates must be numeric.")
    return int(number) if number.is_integer() and "." not in stripped else number


def _point3d(point):
    return Point3D(point["x"], point["y"], point["z"])


def _point_list(point):
    return [point["x"], point["y"], point["z"]]


def _point_to_dict(point):
    if isinstance(point, Point3D):
        return {"x": point.x, "y": point.y, "z": point.z}
    return {key: point[key] for key in ("x", "y", "z")}
