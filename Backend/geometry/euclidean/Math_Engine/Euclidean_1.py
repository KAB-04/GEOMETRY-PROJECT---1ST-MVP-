# ================================================================
#  EUCLIDEAN MATHEMATICAL ENGINE 1
#  Contents:
#    1. Point
#    2. Segment
#    3. Line
#    4. Angle
#    5. Triangle
#    6. Circle
#    7. Polygon  (convex, general)
#    8. Quadrilateral  (general + Parallelogram + Rectangle)
#    9. SimilarTriangles
#   10. Trigonometry  (sin / cos / tan rules)
# ================================================================

from __future__ import annotations
import math
from typing import List


# ================================================================
#  1. POINT
#  The atomic primitive — every other shape is built from points.
# ================================================================

class Point:
    """A point in 2D Euclidean space."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: Point) -> float:
        """Straight-line distance using the Pythagorean theorem."""
        return math.hypot(other.x - self.x, other.y - self.y)

    def midpoint_to(self, other: Point) -> Point:
        """Midpoint between this point and another."""
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)

    def __eq__(self, other: object) -> bool:
        """Floating-point safe equality via math.isclose."""
        if not isinstance(other, Point):
            return NotImplemented
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


# ================================================================
#  2. SEGMENT
#  A bounded piece of a line — has length and a midpoint.
# ================================================================

class Segment:
    """Line segment between two endpoints."""

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def length(self) -> float:
        """Distance between the two endpoints."""
        return self.p1.distance_to(self.p2)

    def midpoint(self) -> Point:
        """The point exactly halfway along the segment."""
        return self.p1.midpoint_to(self.p2)

    def __repr__(self) -> str:
        return f"Segment({self.p1}, {self.p2})"


# ================================================================
#  3. LINE
#  Infinite line stored as  ax + by + c = 0  (general form).
#  Preferred over y = mx + c because it handles vertical lines
#  without any special-casing.
# ================================================================

class Line:
    """An infinite straight line: ax + by + c = 0."""

    def __init__(self, a: float, b: float, c: float):
        self.a = a
        self.b = b
        self.c = c

    @classmethod
    def from_two_points(cls, p1: Point, p2: Point) -> Line:
        """Unique line through two given points."""
        a = p2.y - p1.y
        b = p1.x - p2.x
        c = a * p1.x + b * p1.y
        return cls(a, b, -c)

    def contains_point(self, p: Point, tol: float = 1e-9) -> bool:
        """True if p satisfies ax + by + c ≈ 0."""
        return abs(self.a * p.x + self.b * p.y + self.c) < tol

    def intersection_with(self, other: Line) -> Point | None:
        """
        Intersection point via Cramer's rule.
        Returns None if the lines are parallel (or identical).
        """
        det = self.a * other.b - other.a * self.b
        if math.isclose(det, 0):
            return None
        x = (-self.c * other.b + other.c * self.b) / det
        y = (-self.a * other.c + other.a * self.c) / det
        return Point(x, y)

    def is_parallel_to(self, other: Line) -> bool:
        """Parallel iff direction vectors are proportional."""
        return math.isclose(self.a * other.b - other.a * self.b, 0)

    def is_perpendicular_to(self, other: Line) -> bool:
        """Perpendicular iff dot product of normal vectors = 0."""
        return math.isclose(self.a * other.a + self.b * other.b, 0)

    def distance_to_point(self, p: Point) -> float:
        """
        Perpendicular distance from point p to this line.
        Formula: |ax + by + c| / sqrt(a^2 + b^2)
        """
        return abs(self.a * p.x + self.b * p.y + self.c) / math.hypot(self.a, self.b)

    def perpendicular_through(self, p: Point) -> Line:
        """The line through p perpendicular to this line."""
        k = -(self.b * p.x - self.a * p.y)
        return Line(self.b, -self.a, k)

    def parallel_through(self, p: Point) -> Line:
        """The line through p parallel to this line."""
        c = -(self.a * p.x + self.b * p.y)
        return Line(self.a, self.b, c)

    def __repr__(self) -> str:
        return f"Line({self.a}x + {self.b}y + {self.c} = 0)"


# ================================================================
#  4. ANGLE
#  The angle at vertex B formed by rays BA and BC.
# ================================================================

class Angle:
    """Angle ABC with vertex at B."""

    def __init__(self, A: Point, B: Point, C: Point):
        self.A = A   # first arm
        self.B = B   # vertex
        self.C = C   # second arm

    def measure_radians(self) -> float:
        """
        Angle in radians via dot product:
            cos(theta) = (v1.v2) / (|v1| |v2|)
        Clamped to [-1, 1] to prevent math.acos domain errors
        from floating-point drift.
        """
        v1 = (self.A.x - self.B.x, self.A.y - self.B.y)
        v2 = (self.C.x - self.B.x, self.C.y - self.B.y)
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if math.isclose(mag1, 0) or math.isclose(mag2, 0):
            raise ValueError("Angle undefined: two points are coincident.")
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        return math.acos(max(-1.0, min(1.0, dot / (mag1 * mag2))))

    def measure_degrees(self) -> float:
        """Angle in degrees."""
        return math.degrees(self.measure_radians())

    def is_right(self, tol: float = 1e-9) -> bool:
        return math.isclose(self.measure_radians(), math.pi / 2, abs_tol=tol)

    def is_acute(self) -> bool:
        return self.measure_radians() < math.pi / 2

    def is_obtuse(self) -> bool:
        return self.measure_radians() > math.pi / 2

    def is_straight(self, tol: float = 1e-9) -> bool:
        """180 degrees — the three points are collinear."""
        return math.isclose(self.measure_radians(), math.pi, abs_tol=tol)

    def supplementary(self) -> float:
        """The supplementary angle (pi - theta) in radians."""
        return math.pi - self.measure_radians()

    def complementary(self) -> float:
        """
        The complementary angle (pi/2 - theta) in radians.
        Only defined for acute angles.
        """
        if not self.is_acute():
            raise ValueError("Complementary angle only defined for acute angles.")
        return math.pi / 2 - self.measure_radians()

    def __repr__(self) -> str:
        return f"Angle(A={self.A}, vertex={self.B}, C={self.C})"


# ================================================================
#  5. TRIANGLE
#  Defined by three non-collinear vertices A, B, C.
#  Side convention (Pamfilos Ch.1):
#      a = BC  (opposite A)
#      b = CA  (opposite B)
#      c = AB  (opposite C)
# ================================================================

class Triangle:
    """Triangle ABC."""

    def __init__(self, A: Point, B: Point, C: Point):
        if Triangle._are_collinear(A, B, C):
            raise ValueError("Points are collinear — no triangle is formed.")
        self.A = A
        self.B = B
        self.C = C

    @staticmethod
    def _are_collinear(A: Point, B: Point, C: Point, tol: float = 1e-9) -> bool:
        """Cross product = 0  means three points lie on the same line."""
        cross = (B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x)
        return math.isclose(cross, 0, abs_tol=tol)

    # ── Sides ────────────────────────────────────────────────

    def side_a(self) -> float:
        """Length of BC (opposite A)."""
        return self.B.distance_to(self.C)

    def side_b(self) -> float:
        """Length of CA (opposite B)."""
        return self.C.distance_to(self.A)

    def side_c(self) -> float:
        """Length of AB (opposite C)."""
        return self.A.distance_to(self.B)

    def sides(self) -> tuple:
        return self.side_a(), self.side_b(), self.side_c()

    # ── Perimeter / area ─────────────────────────────────────

    def perimeter(self) -> float:
        return sum(self.sides())

    def semi_perimeter(self) -> float:
        """tau in Pamfilos' notation — used in Heron's formula."""
        return self.perimeter() / 2

    def area(self) -> float:
        """Area via cross product: epsilon = 0.5 * |(B-A) x (C-A)|."""
        cross = ((self.B.x - self.A.x) * (self.C.y - self.A.y)
               - (self.B.y - self.A.y) * (self.C.x - self.A.x))
        return abs(cross) / 2

    def area_heron(self) -> float:
        """Heron's formula: epsilon = sqrt(tau*(tau-a)*(tau-b)*(tau-c))."""
        t = self.semi_perimeter()
        a, b, c = self.sides()
        return math.sqrt(max(0.0, t * (t - a) * (t - b) * (t - c)))

    # ── Angles ───────────────────────────────────────────────

    def angle_at_A(self) -> Angle:
        return Angle(self.B, self.A, self.C)

    def angle_at_B(self) -> Angle:
        return Angle(self.A, self.B, self.C)

    def angle_at_C(self) -> Angle:
        return Angle(self.A, self.C, self.B)

    def angle_sum(self) -> float:
        """Should always equal pi — use as a built-in theorem test."""
        return (self.angle_at_A().measure_radians()
              + self.angle_at_B().measure_radians()
              + self.angle_at_C().measure_radians())

    # ── Special points ───────────────────────────────────────

    def centroid(self) -> Point:
        """G = average of vertices. Intersection of the three medians."""
        return Point(
            (self.A.x + self.B.x + self.C.x) / 3,
            (self.A.y + self.B.y + self.C.y) / 3
        )

    def circumcenter(self) -> Point:
        """O = intersection of perpendicular bisectors."""
        ax, ay = self.A.x, self.A.y
        bx, by = self.B.x, self.B.y
        cx, cy = self.C.x, self.C.y
        D = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if math.isclose(D, 0):
            raise ValueError("Circumcenter undefined for degenerate triangle.")
        ux = ((ax**2 + ay**2) * (by - cy)
            + (bx**2 + by**2) * (cy - ay)
            + (cx**2 + cy**2) * (ay - by)) / D
        uy = ((ax**2 + ay**2) * (cx - bx)
            + (bx**2 + by**2) * (ax - cx)
            + (cx**2 + cy**2) * (bx - ax)) / D
        return Point(ux, uy)

    def circumradius(self) -> float:
        """R = (a * b * c) / (4 * epsilon)."""
        a, b, c = self.sides()
        return (a * b * c) / (4 * self.area())

    def incenter(self) -> Point:
        """I = weighted average of vertices by opposite side lengths."""
        a, b, c = self.sides()
        total = a + b + c
        return Point(
            (a * self.A.x + b * self.B.x + c * self.C.x) / total,
            (a * self.A.y + b * self.B.y + c * self.C.y) / total
        )

    def inradius(self) -> float:
        """r = epsilon / tau."""
        return self.area() / self.semi_perimeter()

    def orthocenter(self) -> Point:
        """H = intersection of the three altitudes."""
        alt_A = Triangle._altitude_line(self.A, self.B, self.C)
        alt_B = Triangle._altitude_line(self.B, self.A, self.C)
        result = alt_A.intersection_with(alt_B)
        if result is None:
            raise ValueError("Orthocenter undefined for degenerate triangle.")
        return result

    def nine_point_center(self) -> Point:
        """
        N9 = midpoint of the segment from circumcenter O to orthocenter H.
        The nine-point circle passes through:
          - midpoints of the three sides
          - feet of the three altitudes
          - midpoints of segments from each vertex to the orthocenter
        (Pamfilos Ch.5 — Euler's circle)
        """
        O = self.circumcenter()
        H = self.orthocenter()
        return Point((O.x + H.x) / 2, (O.y + H.y) / 2)

    def nine_point_radius(self) -> float:
        """Radius of the nine-point circle = R / 2."""
        return self.circumradius() / 2

    def euler_line(self) -> Line:
        """
        The Euler line passes through orthocenter H, centroid G,
        and circumcenter O. All three are collinear.
        """
        O = self.circumcenter()
        H = self.orthocenter()
        return Line.from_two_points(O, H)

    @staticmethod
    def _altitude_line(vertex: Point, foot1: Point, foot2: Point) -> Line:
        """Line through vertex, perpendicular to the segment foot1 to foot2."""
        dx = foot2.x - foot1.x
        dy = foot2.y - foot1.y
        k = -dy * vertex.x + dx * vertex.y
        return Line(dy, -dx, -k)

    # ── Special segments ─────────────────────────────────────

    def median_to_A(self) -> Segment:
        """Median from A to midpoint of BC."""
        return Segment(self.A, Segment(self.B, self.C).midpoint())

    def median_to_B(self) -> Segment:
        return Segment(self.B, Segment(self.C, self.A).midpoint())

    def median_to_C(self) -> Segment:
        return Segment(self.C, Segment(self.A, self.B).midpoint())

    def altitude_length_from_A(self) -> float:
        """h_A = 2*epsilon / a."""
        return 2 * self.area() / self.side_a()

    def altitude_length_from_B(self) -> float:
        return 2 * self.area() / self.side_b()

    def altitude_length_from_C(self) -> float:
        return 2 * self.area() / self.side_c()

    def angle_bisector_length_A(self) -> float:
        """
        Length of the bisector from A to side BC.
        Pamfilos (Section 3.12) via Stewart's theorem:
            t_a = (2*b*c * cos(alpha/2)) / (b + c)
        """
        b, c = self.side_b(), self.side_c()
        alpha = self.angle_at_A().measure_radians()
        return (2 * b * c * math.cos(alpha / 2)) / (b + c)

    # ── Classification ───────────────────────────────────────

    def is_equilateral(self, tol: float = 1e-9) -> bool:
        a, b, c = self.sides()
        return math.isclose(a, b, abs_tol=tol) and math.isclose(b, c, abs_tol=tol)

    def is_isosceles(self, tol: float = 1e-9) -> bool:
        a, b, c = self.sides()
        return (math.isclose(a, b, abs_tol=tol)
             or math.isclose(b, c, abs_tol=tol)
             or math.isclose(a, c, abs_tol=tol))

    def is_scalene(self, tol: float = 1e-9) -> bool:
        return not self.is_isosceles(tol)

    def is_right(self, tol: float = 1e-9) -> bool:
        """Verified via Pythagorean theorem (sorted so c is the hypotenuse)."""
        a, b, c = sorted(self.sides())
        return math.isclose(a**2 + b**2, c**2, abs_tol=tol)

    def is_acute(self) -> bool:
        return all(ang.is_acute() for ang in
                   [self.angle_at_A(), self.angle_at_B(), self.angle_at_C()])

    def is_obtuse(self) -> bool:
        return any(ang.is_obtuse() for ang in
                   [self.angle_at_A(), self.angle_at_B(), self.angle_at_C()])

    # ── Sine / Cosine rules ──────────────────────────────────

    def sine_rule_check(self) -> bool:
        """
        Sine rule: a/sin(alpha) = b/sin(beta) = c/sin(gamma) = 2R.
        Returns True if all three ratios agree.
        """
        a, b, c = self.sides()
        alpha = self.angle_at_A().measure_radians()
        beta  = self.angle_at_B().measure_radians()
        gamma = self.angle_at_C().measure_radians()
        r1 = a / math.sin(alpha)
        r2 = b / math.sin(beta)
        r3 = c / math.sin(gamma)
        return math.isclose(r1, r2) and math.isclose(r2, r3)

    def cosine_rule_side_a(self) -> float:
        """
        Cosine rule: a^2 = b^2 + c^2 - 2*b*c*cos(alpha).
        Cross-check with side_a().
        """
        b, c = self.side_b(), self.side_c()
        alpha = self.angle_at_A().measure_radians()
        return math.sqrt(b**2 + c**2 - 2 * b * c * math.cos(alpha))

    def __repr__(self) -> str:
        return f"Triangle(A={self.A}, B={self.B}, C={self.C})"


# ================================================================
#  6. CIRCLE
#  Defined by center O and radius rho. kappa(O, rho) in Pamfilos.
#  Covers Ch.2 (circle/line/chord) and Ch.4 (power of a point).
# ================================================================

class Circle:
    """Circle kappa(O, rho) — all points at distance rho from center O."""

    def __init__(self, center: Point, radius: float):
        if radius <= 0:
            raise ValueError("Radius must be positive.")
        self.center = center
        self.radius = radius

    # ── Basic properties ─────────────────────────────────────

    def diameter(self) -> float:
        """2 * rho."""
        return 2 * self.radius

    def circumference(self) -> float:
        """Perimeter: 2 * pi * rho."""
        return 2 * math.pi * self.radius

    def area(self) -> float:
        """Area enclosed: pi * rho^2."""
        return math.pi * self.radius ** 2

    # ── Point relations ──────────────────────────────────────

    def contains_point(self, p: Point, tol: float = 1e-9) -> bool:
        """True if p is inside or on the circle."""
        return self.center.distance_to(p) <= self.radius + tol

    def point_on_circle(self, p: Point, tol: float = 1e-9) -> bool:
        """True if p lies exactly on the circle boundary."""
        return math.isclose(self.center.distance_to(p), self.radius, abs_tol=tol)

    def power_of_point(self, p: Point) -> float:
        """
        Power of point X relative to circle kappa(O, rho):
            p(X) = |OX|^2 - rho^2
        Pamfilos uses this throughout Ch.4.
          p(X) < 0  means X is inside the circle
          p(X) = 0  means X is on the circle
          p(X) > 0  means X is outside the circle
        """
        return self.center.distance_to(p) ** 2 - self.radius ** 2

    # ── Line / circle relations ──────────────────────────────

    def intersect_with_line(self, line: Line) -> list:
        """
        Intersection of the circle with a line (Ch.2).
        Returns a list of 0, 1, or 2 Points:
          0 points: line does not meet the circle
          1 point : line is tangent to the circle
          2 points: line is a secant (chord endpoints)
        """
        dist = line.distance_to_point(self.center)
        if dist > self.radius + 1e-9:
            return []
        perp = line.perpendicular_through(self.center)
        foot = line.intersection_with(perp)
        if math.isclose(dist, self.radius, abs_tol=1e-9):
            return [foot]
        half_chord = math.sqrt(max(0.0, self.radius**2 - dist**2))
        norm = math.hypot(line.a, line.b)
        dx = -line.b / norm
        dy =  line.a / norm
        return [
            Point(foot.x + half_chord * dx, foot.y + half_chord * dy),
            Point(foot.x - half_chord * dx, foot.y - half_chord * dy),
        ]

    def is_tangent_to_line(self, line: Line, tol: float = 1e-9) -> bool:
        """True if the line is tangent to the circle."""
        return math.isclose(line.distance_to_point(self.center),
                            self.radius, abs_tol=tol)

    def tangent_at_point(self, p: Point) -> Line:
        """
        The tangent line at point p (must lie on the circle).
        The tangent is perpendicular to the radius OP at p.
        """
        if not self.point_on_circle(p):
            raise ValueError("Point does not lie on the circle.")
        radius_line = Line.from_two_points(self.center, p)
        return radius_line.perpendicular_through(p)

    # ── Two-circle relations ─────────────────────────────────

    def distance_to_circle(self, other: Circle) -> float:
        """Distance between the two centers."""
        return self.center.distance_to(other.center)

    def intersects_circle(self, other: Circle) -> bool:
        """True if the two circles have common points."""
        d = self.distance_to_circle(other)
        return abs(self.radius - other.radius) <= d <= self.radius + other.radius

    def is_internally_tangent_to(self, other: Circle, tol: float = 1e-9) -> bool:
        """One circle inside the other, touching at exactly one point."""
        d = self.distance_to_circle(other)
        return math.isclose(d, abs(self.radius - other.radius), abs_tol=tol)

    def is_externally_tangent_to(self, other: Circle, tol: float = 1e-9) -> bool:
        """Two circles outside each other, touching at exactly one point."""
        d = self.distance_to_circle(other)
        return math.isclose(d, self.radius + other.radius, abs_tol=tol)

    def radical_axis(self, other: Circle) -> Line:
        """
        The radical axis of two circles: the locus of points with equal
        power relative to both circles. (Pamfilos Section 4.3)
        """
        cx1, cy1, r1 = self.center.x, self.center.y, self.radius
        cx2, cy2, r2 = other.center.x, other.center.y, other.radius
        D1, E1, F1 = -2 * cx1, -2 * cy1, cx1**2 + cy1**2 - r1**2
        D2, E2, F2 = -2 * cx2, -2 * cy2, cx2**2 + cy2**2 - r2**2
        return Line(D1 - D2, E1 - E2, F1 - F2)

    # ── Arc / chord ──────────────────────────────────────────

    def arc_length(self, central_angle_rad: float) -> float:
        """Arc length for a given central angle theta: s = rho * theta."""
        return self.radius * central_angle_rad

    def chord_length(self, central_angle_rad: float) -> float:
        """
        Chord length for a given central angle theta:
            chord = 2 * rho * sin(theta / 2)
        """
        return 2 * self.radius * math.sin(central_angle_rad / 2)

    def inscribed_angle(self, central_angle_rad: float) -> float:
        """
        Inscribed angle theorem (Pamfilos Section 2.13):
        An inscribed angle is half the central angle subtending the same arc.
        """
        return central_angle_rad / 2

    @classmethod
    def circumscribed_circle(cls, triangle: Triangle) -> Circle:
        """Circumscribed circle of a triangle (Pamfilos Corollary 2.6)."""
        return cls(triangle.circumcenter(), triangle.circumradius())

    @classmethod
    def inscribed_circle(cls, triangle: Triangle) -> Circle:
        """Inscribed circle of a triangle."""
        return cls(triangle.incenter(), triangle.inradius())

    def __repr__(self) -> str:
        return f"Circle(center={self.center}, radius={self.radius})"


# ================================================================
#  7. POLYGON
#  A convex polygon defined by an ordered list of vertices.
#  Covers perimeter, area (shoelace), angle sum (Pamfilos Section 2.11).
# ================================================================

class Polygon:
    """
    A convex polygon with vertices given in order (clockwise or
    counter-clockwise). Minimum 3 vertices.
    """

    def __init__(self, vertices: List[Point]):
        if len(vertices) < 3:
            raise ValueError("A polygon requires at least 3 vertices.")
        self.vertices = vertices

    def num_sides(self) -> int:
        """Number of sides (equals number of vertices)."""
        return len(self.vertices)

    def perimeter(self) -> float:
        """Sum of all side lengths."""
        n = self.num_sides()
        return sum(
            self.vertices[i].distance_to(self.vertices[(i + 1) % n])
            for i in range(n)
        )

    def area(self) -> float:
        """
        Area via the Shoelace formula (Gauss):
            epsilon = 0.5 * |sum(x_i * y_(i+1) - x_(i+1) * y_i)|
        Works for any simple (non-self-intersecting) polygon.
        """
        n = self.num_sides()
        total = 0.0
        for i in range(n):
            j = (i + 1) % n
            total += self.vertices[i].x * self.vertices[j].y
            total -= self.vertices[j].x * self.vertices[i].y
        return abs(total) / 2

    def angle_sum_degrees(self) -> float:
        """
        Sum of interior angles of an n-gon:
            Sum = (n - 2) * 180 degrees
        Pamfilos Section 2.11: generalises the triangle (n=3 gives 180 degrees).
        """
        return (self.num_sides() - 2) * 180.0

    def is_regular(self, tol: float = 1e-9) -> bool:
        """
        A regular polygon has all sides equal.
        For convex polygons equal sides also imply equal angles.
        """
        n = self.num_sides()
        side0 = self.vertices[0].distance_to(self.vertices[1])
        return all(
            math.isclose(
                self.vertices[i].distance_to(self.vertices[(i + 1) % n]),
                side0, abs_tol=tol
            )
            for i in range(n)
        )

    def centroid(self) -> Point:
        """Centroid: average of all vertex coordinates."""
        n = self.num_sides()
        cx = sum(v.x for v in self.vertices) / n
        cy = sum(v.y for v in self.vertices) / n
        return Point(cx, cy)

    def __repr__(self) -> str:
        return f"Polygon({self.vertices})"


# ================================================================
#  8. QUADRILATERAL  +  PARALLELOGRAM  +  RECTANGLE
#  Pamfilos Sections 2.5 through 2.10.
# ================================================================

class Quadrilateral(Polygon):
    """
    A convex quadrilateral ABCD.
    Inherits perimeter, area, centroid from Polygon.
    """

    def __init__(self, A: Point, B: Point, C: Point, D: Point):
        super().__init__([A, B, C, D])
        self.A, self.B, self.C, self.D = A, B, C, D

    def diagonal_AC(self) -> float:
        """Length of diagonal AC."""
        return self.A.distance_to(self.C)

    def diagonal_BD(self) -> float:
        """Length of diagonal BD."""
        return self.B.distance_to(self.D)

    def diagonals_intersect(self) -> Point | None:
        """Intersection point of the two diagonals."""
        line_AC = Line.from_two_points(self.A, self.C)
        line_BD = Line.from_two_points(self.B, self.D)
        return line_AC.intersection_with(line_BD)

    def angle_sum_degrees(self) -> float:
        """Sum of interior angles of any quadrilateral = 360 degrees (Pamfilos Section 2.6)."""
        return 360.0

    def is_cyclic(self, tol: float = 1e-9) -> bool:
        """
        A cyclic quadrilateral has opposite angles summing to 180 degrees.
        Pamfilos Section 2.14.
        """
        alpha = Angle(self.D, self.A, self.B).measure_degrees()
        gamma = Angle(self.B, self.C, self.D).measure_degrees()
        return math.isclose(alpha + gamma, 180.0, abs_tol=tol)

    def __repr__(self) -> str:
        return f"Quadrilateral(A={self.A}, B={self.B}, C={self.C}, D={self.D})"


class Parallelogram(Quadrilateral):
    """
    A parallelogram: opposite sides parallel and equal. (Pamfilos Section 2.5)
    Key properties:
      - Opposite sides are equal and parallel
      - Diagonals bisect each other
      - Opposite angles are equal; consecutive angles are supplementary
    """

    def __init__(self, A: Point, B: Point, C: Point, D: Point):
        super().__init__(A, B, C, D)

    def is_valid_parallelogram(self, tol: float = 1e-9) -> bool:
        """Verifies that opposite sides are equal (the defining property)."""
        ab = self.A.distance_to(self.B)
        dc = self.D.distance_to(self.C)
        ad = self.A.distance_to(self.D)
        bc = self.B.distance_to(self.C)
        return (math.isclose(ab, dc, abs_tol=tol) and
                math.isclose(ad, bc, abs_tol=tol))

    def diagonals_bisect_each_other(self) -> bool:
        """
        Key theorem: diagonals of a parallelogram bisect each other.
        Verified by checking that both diagonals share the same midpoint.
        """
        mid_AC = Segment(self.A, self.C).midpoint()
        mid_BD = Segment(self.B, self.D).midpoint()
        return mid_AC == mid_BD

    def __repr__(self) -> str:
        return f"Parallelogram(A={self.A}, B={self.B}, C={self.C}, D={self.D})"


class Rectangle(Parallelogram):
    """
    A rectangle: a parallelogram with all right angles. (Pamfilos Section 2.9)
    The diagonals of a rectangle are equal in length.
    """

    def is_valid_rectangle(self, tol: float = 1e-9) -> bool:
        """Verifies right angle at A (implies all angles are right)."""
        return Angle(self.D, self.A, self.B).is_right(tol)

    def area(self) -> float:
        """Area = |AB| x |AD|."""
        return self.A.distance_to(self.B) * self.A.distance_to(self.D)

    def is_square(self, tol: float = 1e-9) -> bool:
        """A square is a rectangle with all sides equal."""
        return math.isclose(
            self.A.distance_to(self.B),
            self.A.distance_to(self.D),
            abs_tol=tol
        )

    def diagonal_length(self) -> float:
        """
        Diagonal of a rectangle via Pythagoras: d = sqrt(a^2 + b^2).
        Both diagonals are equal — a property unique to rectangles
        among parallelograms.
        """
        a = self.A.distance_to(self.B)
        b = self.A.distance_to(self.D)
        return math.hypot(a, b)

    def __repr__(self) -> str:
        return f"Rectangle(A={self.A}, B={self.B}, C={self.C}, D={self.D})"


# ================================================================
#  9. SIMILAR TRIANGLES
#  Two triangles are similar if their angles are equal and their
#  sides are proportional. Pamfilos Section 3.9.
#  Criteria: AA, SAS~, SSS~
# ================================================================

class SimilarTriangles:
    """Encapsulates the similarity relationship between two triangles."""

    def __init__(self, T1: Triangle, T2: Triangle):
        self.T1 = T1
        self.T2 = T2

    def similarity_ratio(self) -> float:
        """
        k = corresponding side of T2 / corresponding side of T1.
        Uses the ratio of the longest (sorted) sides.
        """
        sides1 = sorted(self.T1.sides())
        sides2 = sorted(self.T2.sides())
        return sides2[2] / sides1[2]

    def are_similar_AA(self, tol: float = 1e-6) -> bool:
        """
        AA criterion: two pairs of equal angles imply similarity.
        The third pair follows from the angle sum being pi.
        """
        angles1 = sorted([self.T1.angle_at_A().measure_radians(),
                          self.T1.angle_at_B().measure_radians(),
                          self.T1.angle_at_C().measure_radians()])
        angles2 = sorted([self.T2.angle_at_A().measure_radians(),
                          self.T2.angle_at_B().measure_radians(),
                          self.T2.angle_at_C().measure_radians()])
        return all(math.isclose(a1, a2, abs_tol=tol)
                   for a1, a2 in zip(angles1, angles2))

    def are_similar_SSS(self, tol: float = 1e-9) -> bool:
        """SSS~ criterion: all three side ratios equal."""
        s1 = sorted(self.T1.sides())
        s2 = sorted(self.T2.sides())
        ratios = [s2[i] / s1[i] for i in range(3)]
        return (math.isclose(ratios[0], ratios[1], abs_tol=tol) and
                math.isclose(ratios[1], ratios[2], abs_tol=tol))

    def area_ratio(self) -> float:
        """
        Area ratio = k^2 where k is the similarity ratio.
        Areas of similar figures scale as the square of the similarity ratio.
        (Pamfilos Section 3.9)
        """
        return self.similarity_ratio() ** 2

    def __repr__(self) -> str:
        return (f"SimilarTriangles(\n  T1={self.T1},\n  T2={self.T2},\n"
                f"  ratio={self.similarity_ratio():.4f})")


# ================================================================
#  10. TRIGONOMETRY
#  Standalone functions for triangle trigonometric rules.
#  Pamfilos Sections 3.6 and 3.11.
# ================================================================

def sin_rule(a: float, alpha_rad: float) -> float:
    """
    Returns 2R from the sine rule: a / sin(alpha) = 2R.
    Any side divided by its opposite sine gives the same value.
    """
    return a / math.sin(alpha_rad)


def cosine_rule_side(b: float, c: float, alpha_rad: float) -> float:
    """
    Cosine rule — find side a opposite angle alpha:
        a^2 = b^2 + c^2 - 2*b*c*cos(alpha)
    """
    return math.sqrt(b**2 + c**2 - 2 * b * c * math.cos(alpha_rad))


def cosine_rule_angle(a: float, b: float, c: float) -> float:
    """
    Cosine rule — find angle alpha opposite side a:
        cos(alpha) = (b^2 + c^2 - a^2) / (2*b*c)
    Returns angle in radians.
    """
    cos_alpha = (b**2 + c**2 - a**2) / (2 * b * c)
    return math.acos(max(-1.0, min(1.0, cos_alpha)))


def thales_theorem(A: Point, B: Point, C: Point) -> bool:
    """
    Thales' theorem (Pamfilos Section 3.7):
    If AB is a diameter, any point C on the circle sees AB at 90 degrees.
    Checks: is the angle at C a right angle?
    """
    return Angle(A, C, B).is_right()


def pythagoras(a: float, b: float) -> float:
    """Hypotenuse c = sqrt(a^2 + b^2) for a right triangle with legs a and b."""
    return math.hypot(a, b)


def pythagoras_verify(a: float, b: float, c: float, tol: float = 1e-9) -> bool:
    """Verifies a^2 + b^2 = c^2 (where c is the hypotenuse)."""
    return math.isclose(a**2 + b**2, c**2, abs_tol=tol)


