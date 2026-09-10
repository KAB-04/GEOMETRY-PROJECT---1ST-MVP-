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
}
