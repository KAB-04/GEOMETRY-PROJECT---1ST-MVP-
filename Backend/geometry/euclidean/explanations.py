import math
import re


OPERATION_LABELS = {
    "distance": "Distance Between Two Points",
    "midpoint": "Midpoint",
    "slope": "Slope",
    "circle_area": "Area of a Circle",
    "circle_circumference": "Circumference of a Circle",
    "circle_circle_intersection": "Circle Intersection",
    "triangle_area": "Area of a Triangle",
    "triangle_perimeter": "Triangle Perimeter",
    "triangle_third_angle": "Triangle - Missing Angle",
    "pythagoras": "Pythagorean Theorem",
    "pythagoras_verify": "Pythagorean Theorem Check",
    "rectangle_area": "Rectangle Area",
    "rectangle_perimeter": "Rectangle Perimeter",
    "transform": "Geometric Transformation",
    "distance3d": "3D Distance Between Points",
    "midpoint3d": "3D Midpoint",
    "vector3d": "3D Vector",
    "line3d": "3D Line",
    "triangle3d": "3D Triangle",
    "plane3d": "3D Plane",
    "cuboid_volume": "Cuboid Volume",
    "cylinder_volume": "Cylinder Volume",
    "cylinder_lateral_surface_area": "Cylinder Lateral Surface Area",
    "cylinder_total_surface_area": "Cylinder Total Surface Area",
    "cylinder_solution": "Cylinder Solution",
    "cone_solution": "Cone Height and Volume",
    "cone_height_from_radius_slant_height": "Cone Height",
    "cone_volume": "Cone Volume",
    "cone_lateral_surface_area": "Cone Lateral Surface Area",
    "cone_total_surface_area": "Cone Total Surface Area",
}


def operation_label(operation):
    return OPERATION_LABELS.get(operation, operation.replace("_", " ").title())


def build_explanation(operation, data, result, question=None):
    builder = EXPLANATION_BUILDERS.get(operation)
    if builder is None:
        return {
            "concept": "Use the selected geometry relationship to calculate the answer.",
            "formula": "",
            "steps": [],
            "conclusion": f"Therefore, the answer is {format_number(result)}.",
        }
    return builder(data, result, question or "")


def _distance(data, result, question):
    dx = data["x2"] - data["x1"]
    dy = data["y2"] - data["y1"]
    dx2 = dx**2
    dy2 = dy**2
    total = dx2 + dy2
    unit = _linear_unit(question)
    return {
        "concept": "Use the distance formula to find the straight-line distance between two points.",
        "formula": r"d = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}",
        "steps": [
            rf"d = \sqrt{{({format_number(data['x2'])} - {format_number(data['x1'])})^2 + ({format_number(data['y2'])} - {format_number(data['y1'])})^2}}",
            rf"d = \sqrt{{{format_number(dx)}^2 + {format_number(dy)}^2}}",
            rf"d = \sqrt{{{format_number(dx2)} + {format_number(dy2)}}}",
            rf"d = \sqrt{{{format_number(total)}}}",
            rf"d = {format_number(result)}",
        ],
        "conclusion": f"Therefore, the distance between the two points is {format_number(result)} {unit}.",
    }


def _circle_area(data, result, question):
    radius = data["rho"]
    unit = _area_unit(question)
    return {
        "concept": "The area of a circle is found by multiplying pi by the radius squared.",
        "formula": r"A = \pi r^2",
        "steps": [
            f"r = {format_number(radius)}",
            rf"A = \pi({format_number(radius)})^2",
            rf"A = {format_number(radius**2)}\pi",
            rf"A \approx {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the area is approximately {format_number(result)} {unit}.",
    }


def _circle_circumference(data, result, question):
    radius = data["rho"]
    unit = _linear_unit(question)
    return {
        "concept": "The circumference of a circle is the distance around it.",
        "formula": r"C = 2\pi r",
        "steps": [
            f"r = {format_number(radius)}",
            rf"C = 2\pi({format_number(radius)})",
            rf"C = {format_number(2 * radius)}\pi",
            rf"C \approx {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the circumference is approximately {format_number(result)} {unit}.",
    }


def _circle_circle_intersection(data, result, question):
    final = result["final"]
    distance = result["intermediate"]["center_distance"]
    points = final["points"]
    relationship = final["relationship"]
    steps = [
        rf"d = \sqrt{{({format_number(data['x2'])}-{format_number(data['x1'])})^2+({format_number(data['y2'])}-{format_number(data['y1'])})^2}} = {format_number(distance)}",
        rf"r_1+r_2 = {format_number(data['r1'])}+{format_number(data['r2'])} = {format_number(data['r1'] + data['r2'])}",
    ]
    if points:
        steps.extend(
            rf"P_{index + 1} = ({format_number(point['x'])},{format_number(point['y'])})"
            for index, point in enumerate(points)
        )
        conclusion = f"The circles intersect at {len(points)} point{'s' if len(points) != 1 else ''}."
    elif relationship == "coincident":
        conclusion = "The circles are coincident, so they have infinitely many intersection points."
    else:
        conclusion = "The circles do not intersect."
    return {
        "concept": "Compare the distance between the centers with the sum and difference of the radii, then calculate the final intersection points.",
        "formula": r"|r_1-r_2| \le d \le r_1+r_2",
        "steps": steps,
        "conclusion": conclusion,
    }


def _triangle_area(data, result, question):
    unit = _area_unit(question)
    return {
        "concept": "The area of a triangle is one half of its base times its perpendicular height.",
        "formula": r"A = \frac{1}{2}bh",
        "steps": [
            rf"A = \frac{{1}}{{2}}({format_number(data['base'])})({format_number(data['height'])})",
            rf"A = {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the area of the triangle is {format_number(result)} {unit}.",
    }


def _triangle_perimeter(data, result, question):
    unit = _linear_unit(question)
    return {
        "concept": "The perimeter of a triangle is the sum of its three side lengths.",
        "formula": "P = a + b + c",
        "steps": [
            f"P = {format_number(data['a'])} + {format_number(data['b'])} + {format_number(data['c'])}",
            f"P = {format_number(result)} {unit}",
        ],
        "conclusion": f"Therefore, the perimeter is {format_number(result)} {unit}.",
    }


def _triangle_third_angle(data, result, question):
    known_sum = data["angle1"] + data["angle2"]
    return {
        "concept": "The angles inside a triangle always add up to 180 degrees.",
        "formula": r"C = 180^\circ - A - B",
        "steps": [
            rf"{format_number(data['angle1'])}^\circ + {format_number(data['angle2'])}^\circ = {format_number(known_sum)}^\circ",
            rf"180^\circ - {format_number(known_sum)}^\circ = {format_number(result)}^\circ",
        ],
        "conclusion": f"Therefore, the third angle is {format_number(result)} degrees.",
    }


def _midpoint(data, result, question):
    x_mid, y_mid = result
    return {
        "concept": "The midpoint is found by averaging the x-coordinates and averaging the y-coordinates.",
        "formula": r"M = \left(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2}\right)",
        "steps": [
            rf"x_M = \frac{{{format_number(data['x1'])}+{format_number(data['x2'])}}}{{2}} = {format_number(x_mid)}",
            rf"y_M = \frac{{{format_number(data['y1'])}+{format_number(data['y2'])}}}{{2}} = {format_number(y_mid)}",
        ],
        "conclusion": f"Therefore, the midpoint is ({format_number(x_mid)}, {format_number(y_mid)}).",
    }


def _slope(data, result, question):
    return {
        "concept": "The slope measures vertical change divided by horizontal change.",
        "formula": r"m = \frac{y_2-y_1}{x_2-x_1}",
        "steps": [
            rf"m = \frac{{{format_number(data['y2'])}-{format_number(data['y1'])}}}{{{format_number(data['x2'])}-{format_number(data['x1'])}}}",
            rf"m = \frac{{{format_number(data['y2'] - data['y1'])}}}{{{format_number(data['x2'] - data['x1'])}}}",
            rf"m = {format_number(result)}",
        ],
        "conclusion": f"Therefore, the slope is {format_number(result)}.",
    }


def _pythagoras(data, result, question):
    unit = _linear_unit(question)
    return {
        "concept": "For a right triangle, the Pythagorean theorem relates the two legs to the hypotenuse.",
        "formula": r"c = \sqrt{a^2+b^2}",
        "steps": [
            rf"c = \sqrt{{{format_number(data['a'])}^2+{format_number(data['b'])}^2}}",
            rf"c = \sqrt{{{format_number(data['a'] ** 2)}+{format_number(data['b'] ** 2)}}}",
            rf"c = \sqrt{{{format_number(data['a'] ** 2 + data['b'] ** 2)}}}",
            rf"c = {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the missing side is {format_number(result)} {unit}.",
    }


def _rectangle_area(data, result, question):
    unit = _area_unit(question)
    return {
        "concept": "The area of a rectangle is length times width.",
        "formula": r"A = \ell w",
        "steps": [
            rf"A = ({format_number(data['length'])})({format_number(data['width'])})",
            rf"A = {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the rectangle's area is {format_number(result)} {unit}.",
    }


def _rectangle_perimeter(data, result, question):
    unit = _linear_unit(question)
    return {
        "concept": "The perimeter of a rectangle is the total distance around all four sides.",
        "formula": r"P = 2(\ell+w)",
        "steps": [
            rf"P = 2({format_number(data['length'])}+{format_number(data['width'])})",
            rf"P = 2({format_number(data['length'] + data['width'])})",
            rf"P = {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the rectangle's perimeter is {format_number(result)} {unit}.",
    }


def _distance3d(data, result, question):
    first, second = data["points"][0], data["points"][1]
    dx = second["x"] - first["x"]
    dy = second["y"] - first["y"]
    dz = second["z"] - first["z"]
    total = dx**2 + dy**2 + dz**2
    unit = _linear_unit(question)
    return {
        "concept": "Use the three-dimensional distance formula to measure the straight-line distance between two points.",
        "formula": r"d = \sqrt{(x_2-x_1)^2+(y_2-y_1)^2+(z_2-z_1)^2}",
        "steps": [
            rf"d = \sqrt{{({format_number(second['x'])}-{format_number(first['x'])})^2+({format_number(second['y'])}-{format_number(first['y'])})^2+({format_number(second['z'])}-{format_number(first['z'])})^2}}",
            rf"d = \sqrt{{{format_number(dx**2)}+{format_number(dy**2)}+{format_number(dz**2)}}}",
            rf"d = \sqrt{{{format_number(total)}}}",
            rf"d \approx {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the distance is approximately {format_number(result)} {unit}.",
    }


def _midpoint3d(data, result, question):
    first, second = data["points"][0], data["points"][1]
    return {
        "concept": "The midpoint in 3D is found by averaging each coordinate.",
        "formula": r"M = \left(\frac{x_1+x_2}{2},\frac{y_1+y_2}{2},\frac{z_1+z_2}{2}\right)",
        "steps": [
            rf"x_M = \frac{{{format_number(first['x'])}+{format_number(second['x'])}}}{{2}} = {format_number(result['x'])}",
            rf"y_M = \frac{{{format_number(first['y'])}+{format_number(second['y'])}}}{{2}} = {format_number(result['y'])}",
            rf"z_M = \frac{{{format_number(first['z'])}+{format_number(second['z'])}}}{{2}} = {format_number(result['z'])}",
        ],
        "conclusion": f"Therefore, the midpoint is ({format_number(result['x'])}, {format_number(result['y'])}, {format_number(result['z'])}).",
    }


def _vector3d(data, result, question):
    start, end = result["from"], result["to"]
    components = [end[index] - start[index] for index in range(3)]
    return {
        "concept": "A 3D vector points from the starting point to the ending point.",
        "formula": r"v = B - A",
        "steps": [
            f"v = ({format_number(end[0])}, {format_number(end[1])}, {format_number(end[2])}) - ({format_number(start[0])}, {format_number(start[1])}, {format_number(start[2])})",
            f"v = ({format_number(components[0])}, {format_number(components[1])}, {format_number(components[2])})",
        ],
        "conclusion": "Therefore, the vector is shown from the starting point to the ending point.",
    }


def _line3d(data, result, question):
    direction = result["direction"]
    return {
        "concept": "A line in 3D can be defined by two points and the direction between them.",
        "formula": r"L(t) = P + tv",
        "steps": [
            f"Direction vector v = ({format_number(direction['x'])}, {format_number(direction['y'])}, {format_number(direction['z'])})",
        ],
        "conclusion": "Therefore, the line passes through the two given points and extends in that direction.",
    }


def _triangle3d(data, result, question):
    return {
        "concept": "A triangle in 3D is defined by three non-collinear vertices.",
        "formula": "vertices A, B, C determine the triangular face",
        "steps": [f"Use vertices {', '.join(result['vertices'])}."],
        "conclusion": "Therefore, the triangle is drawn using the three provided vertices.",
    }


def _plane3d(data, result, question):
    normal = result["normal"]
    return {
        "concept": "Three non-collinear points determine a unique plane.",
        "formula": r"n \cdot (X-P) = 0",
        "steps": [
            f"Normal vector n = ({format_number(normal['x'])}, {format_number(normal['y'])}, {format_number(normal['z'])})",
        ],
        "conclusion": "Therefore, the plane is drawn through the three given points.",
    }


def _cuboid_volume(data, result, question):
    return {
        "concept": "The volume of a cuboid is width times height times depth.",
        "formula": "V = width x height x depth",
        "steps": [
            f"V = {format_number(data['width'])} x {format_number(data['height'])} x {format_number(data['depth'])}",
            f"V = {format_number(result)} cubic units",
        ],
        "conclusion": f"Therefore, the volume is {format_number(result)} cubic units.",
    }


def _cylinder_volume(data, result, question):
    radius = data["radius"]
    height = data["height"]
    unit = _volume_unit(question)
    return {
        "concept": "The volume of a cylinder is the area of its circular base multiplied by its height.",
        "formula": r"V = \pi r^2h",
        "steps": [
            f"r = {format_number(radius)}, h = {format_number(height)}",
            rf"V = \pi({format_number(radius)})^2({format_number(height)})",
            rf"V = {format_number(radius**2 * height)}\pi",
            rf"V \approx {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the cylinder's volume is approximately {format_number(result)} {unit}.",
    }


def _cylinder_lateral_surface_area(data, result, question):
    radius = data["radius"]
    height = data["height"]
    unit = _area_unit(question)
    return {
        "concept": "The lateral surface area of a cylinder is the curved side area around the cylinder.",
        "formula": r"A = 2\pi rh",
        "steps": [
            f"r = {format_number(radius)}, h = {format_number(height)}",
            rf"A = 2\pi({format_number(radius)})({format_number(height)})",
            rf"A = {format_number(2 * radius * height)}\pi",
            rf"A \approx {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the cylinder's lateral surface area is approximately {format_number(result)} {unit}.",
    }


def _cylinder_total_surface_area(data, result, question):
    radius = data["radius"]
    height = data["height"]
    unit = _area_unit(question)
    return {
        "concept": "The total surface area of a cylinder includes the curved side and the two circular bases.",
        "formula": r"A = 2\pi r(r+h)",
        "steps": [
            f"r = {format_number(radius)}, h = {format_number(height)}",
            rf"A = 2\pi({format_number(radius)})({format_number(radius)}+{format_number(height)})",
            rf"A = {format_number(2 * radius * (radius + height))}\pi",
            rf"A \approx {format_number(result)}\,{_latex_unit(unit)}",
        ],
        "conclusion": f"Therefore, the cylinder's total surface area is approximately {format_number(result)} {unit}.",
    }


def _cone_solution(data, result, question):
    radius = data["radius"]
    height = result.get("height", data.get("height"))
    slant_height = data.get("slant_height")
    volume = result.get("volume")
    unit = _linear_unit(question)
    volume_unit = _volume_unit(question)
    steps = []
    if height is not None and slant_height is not None:
        steps.extend(
            [
                "The radius, vertical height, and slant height form a right triangle.",
                rf"h^2 + r^2 = l^2",
                rf"h = \sqrt{{{format_number(slant_height)}^2-{format_number(radius)}^2}}",
                rf"h = {format_number(height)}\,{_latex_unit(unit)}",
            ]
        )
    if volume is not None:
        steps.extend(
            [
                rf"V = \frac{{1}}{{3}}\pi r^2h",
                rf"V = \frac{{1}}{{3}}\pi({format_number(radius)})^2({format_number(height)})",
                rf"V = {format_number(radius**2 * height / 3)}\pi",
                rf"V \approx {format_number(volume)}\,{_latex_unit(volume_unit)}",
            ]
        )
    final_parts = []
    if "height" in result:
        final_parts.append(f"height = {format_number(result['height'])} {unit}")
    if volume is not None:
        final_parts.append(f"volume = {format_number(radius**2 * height / 3)}pi {volume_unit} approximately {format_number(volume)} {volume_unit}")
    return {
        "concept": "Solve the cone using its parent 3-D geometry, with the right-triangle relationship only as an intermediate step.",
        "formula": r"h^2+r^2=l^2,\quad V=\frac{1}{3}\pi r^2h",
        "steps": steps,
        "conclusion": f"Therefore, the cone's {', and '.join(final_parts)}.",
    }


def _cone_height_from_radius_slant_height(data, result, question):
    return _cone_solution(
        {"radius": data["radius"], "height": result, "slant_height": data["slant_height"]},
        {"height": result},
        question,
    )


def _cone_volume(data, result, question):
    return _cone_solution(data, {"volume": result}, question)


def _pythagoras_verify(data, result, question):
    left = data["a"] ** 2 + data["b"] ** 2
    right = data["c"] ** 2
    conclusion = "Therefore, the side lengths form a right triangle." if result else "Therefore, the side lengths do not form a right triangle."
    return {
        "concept": "A triangle is right-angled when a^2 + b^2 equals c^2.",
        "formula": r"a^2+b^2=c^2",
        "steps": [
            rf"{format_number(data['a'])}^2+{format_number(data['b'])}^2 = {format_number(left)}",
            rf"{format_number(data['c'])}^2 = {format_number(right)}",
        ],
        "conclusion": conclusion,
    }


def _transform(data, result, question):
    rules = {
        "reflection_y_axis": r"(x,y) \mapsto (-x,y)",
        "reflection_x_axis": r"(x,y) \mapsto (x,-y)",
        "reflection_origin": r"(x,y) \mapsto (-x,-y)",
        "reflection_y_equals_x": r"(x,y) \mapsto (y,x)",
        "translation": rf"(x,y) \mapsto (x+{format_number(data.get('dx', 0))},y+{format_number(data.get('dy', 0))})",
        "rotation_90_ccw": r"(x,y) \mapsto (-y,x)",
        "rotation_90_cw": r"(x,y) \mapsto (y,-x)",
        "rotation_180": r"(x,y) \mapsto (-x,-y)",
    }
    rule = rules.get(data["transformation"], r"Apply the selected transformation to each point.")
    steps = [
        rf"{original['id']}({format_number(original['x'])},{format_number(original['y'])}) \mapsto {transformed['id'][0]}^\prime({format_number(transformed['x'])},{format_number(transformed['y'])})"
        for original, transformed in zip(result["original"], result["transformed"])
    ]
    vertices = ", ".join(
        f"{point['label']}({format_number(point['x'])},{format_number(point['y'])})"
        for point in result["transformed"]
    )
    return {
        "concept": "Apply the transformation rule to every vertex while preserving the full point collection.",
        "formula": rule,
        "steps": steps,
        "conclusion": f"Therefore, the transformed points are {vertices}.",
    }


def format_number(value):
    if isinstance(value, (list, tuple)):
        return f"({', '.join(format_number(item) for item in value)})"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        if math.isclose(value, round(value), abs_tol=1e-9):
            return str(int(round(value)))
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def _linear_unit(question):
    unit = _unit_from_question(question)
    return unit or "units"


def _area_unit(question):
    unit = _unit_from_question(question)
    if unit in {"m", "meter", "meters", "metre", "metres"}:
        return "square metres" if "metre" in unit else "square meters"
    return f"square {unit}" if unit else "square units"


def _volume_unit(question):
    unit = _unit_from_question(question)
    if unit in {"m", "meter", "meters"}:
        return "cubic meters"
    if unit in {"metre", "metres"}:
        return "cubic metres"
    if unit in {"cm", "centimeters"}:
        return "cubic centimeters"
    if unit == "centimetres":
        return "cubic centimetres"
    if unit in {"feet", "foot", "ft"}:
        return "cubic feet"
    return f"cubic {unit}" if unit else "cubic units"


def _latex_unit(unit):
    if unit.startswith("square "):
        return f"{unit[7:]}^2"
    return unit.replace(" ", "\\,")


def _unit_from_question(question):
    match = re.search(r"\b(metres|metre|meters|meter|m|cm|centimeters|centimetres|feet|foot|ft)\b", question, re.I)
    if not match:
        return None
    return match.group(1).lower()


EXPLANATION_BUILDERS = {
    "distance": _distance,
    "circle_area": _circle_area,
    "circle_circumference": _circle_circumference,
    "circle_circle_intersection": _circle_circle_intersection,
    "triangle_area": _triangle_area,
    "triangle_perimeter": _triangle_perimeter,
    "triangle_third_angle": _triangle_third_angle,
    "midpoint": _midpoint,
    "slope": _slope,
    "pythagoras": _pythagoras,
    "pythagoras_verify": _pythagoras_verify,
    "rectangle_area": _rectangle_area,
    "rectangle_perimeter": _rectangle_perimeter,
    "transform": _transform,
    "distance3d": _distance3d,
    "midpoint3d": _midpoint3d,
    "vector3d": _vector3d,
    "line3d": _line3d,
    "triangle3d": _triangle3d,
    "plane3d": _plane3d,
    "cuboid_volume": _cuboid_volume,
    "cylinder_volume": _cylinder_volume,
    "cylinder_lateral_surface_area": _cylinder_lateral_surface_area,
    "cylinder_total_surface_area": _cylinder_total_surface_area,
    "cylinder_solution": _cylinder_volume,
    "cone_solution": _cone_solution,
    "cone_height_from_radius_slant_height": _cone_height_from_radius_slant_height,
    "cone_volume": _cone_volume,
    "cone_lateral_surface_area": _cone_volume,
    "cone_total_surface_area": _cone_volume,
}
