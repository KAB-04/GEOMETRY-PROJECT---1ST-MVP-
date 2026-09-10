import math

from .Euclidean2 import Point2D, PointSymmetry, Reflection, Rotation, Translation


def _apply_named_transformation(transformation, points, dx=0, dy=0):
    name = str(transformation).strip().lower().replace("-", "_").replace(" ", "_")
    transformation_object = _build_transformation(name, dx, dy)
    original = [_normalize_point(point) for point in points]
    identifiers = [point["id"] for point in original]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Transformation point IDs must be unique.")
    transformed_ids = [f"{identifier}′" for identifier in identifiers]
    if len(transformed_ids) != len(set(transformed_ids)) or set(transformed_ids) & set(identifiers):
        raise ValueError("Transformation point IDs must not collide with transformed IDs.")
    transformed = []
    for point, transformed_id in zip(original, transformed_ids):
        result = transformation_object.apply(Point2D(point["x"], point["y"]))
        transformed.append(
            {
                "id": transformed_id,
                "x": result.x,
                "y": result.y,
                "label": f"{point['id']}′",
            }
        )
    return {"original": original, "transformed": transformed, "transformation": name}


def _build_transformation(name, dx, dy):
    if name in {"reflection_y", "reflect_y", "reflection_y_axis", "reflect_y_axis"}:
        return Reflection(1, 0, 0)
    if name in {"reflection_x", "reflect_x", "reflection_x_axis", "reflect_x_axis"}:
        return Reflection(0, 1, 0)
    if name in {"reflection_origin", "reflect_origin", "origin_reflection"}:
        return PointSymmetry(Point2D(0, 0))
    if name in {"reflection_y_equals_x", "reflect_y_equals_x", "reflection_y_x"}:
        return Reflection(1, -1, 0)
    if name in {"translation", "translate"}:
        return Translation(dx, dy)
    if name in {"rotation_90_ccw", "rotate_90_ccw", "rotation_counterclockwise_90"}:
        return Rotation(Point2D(0, 0), math.pi / 2)
    if name in {"rotation_90_cw", "rotate_90_cw", "rotation_clockwise_90"}:
        return Rotation(Point2D(0, 0), -math.pi / 2)
    if name in {"rotation_180", "rotate_180"}:
        return Rotation(Point2D(0, 0), math.pi)
    raise ValueError(f"Unsupported 2-D transformation: {name}")


def _normalize_point(point):
    if not isinstance(point, dict) or not isinstance(point.get("id"), str):
        raise ValueError("Each transformation point must contain an id, x, and y.")
    x, y = point.get("x"), point.get("y")
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise ValueError("Each transformation point must contain numeric x and y coordinates.")
    return {"id": point["id"], "x": x, "y": y, "label": point.get("label", point["id"])}