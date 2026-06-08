"""
══════════════════════════════════════════════════════════════
        ANALYTICAL GEOMETRY ENGINE  —  2D & 3D               
               
══════════════════════════════════════════════════════════════

Contents:
   1  : CoordinateGeometry2D (section formula, midpoint, centroid, area)
   2  : StraightLine (all forms, distance, intersection, angles)
   3  : PairOfLines (homogeneous 2nd degree, angle, bisectors)
   4  : Circle (centre/radius, tangent, chord, pole/polar)
   5  : SystemOfCircles (radical axis, orthogonality, coaxal)
   6  : Parabola (focus/directrix, tangent, normal, parametric)
   7  : Ellipse (standard form, tangent, conjugate diameters)
   8  : Hyperbola (standard, rectangular, asymptotes)
   9  : PolarCoordinates (conversion, polar conic)
   10 : ConicTracing (general 2nd degree identification & tracing)
   11 : Geometry3D (distance, direction cosines, centroid)
   12 : Plane3D (equation forms, distance, angle)
   13 : Line3D (symmetric form, skew lines, intersection)
   14 : Sphere3D (centre/radius, tangent plane)
   15 : Cone3D (equation, semi-vertical angle)
   16 : Cylinder3D (equation of right circular cylinder)

Usage:
  python analytical_geometry_engine.py         
  import analytical_geometry_engine as ag       
"""

import math
import cmath


# ================================================================
# UTILITIES
# ================================================================

def _fmt(v, decimals=6):
    """Round a value neatly for display."""
    if isinstance(v, complex):
        r = round(v.real, decimals)
        i = round(v.imag, decimals)
        return complex(r, i)
    return round(float(v), decimals)

def _deg(radians):
    return round(math.degrees(radians), 6)

def _rad(degrees):
    return math.radians(degrees)


# ================================================================
# CHAPTER 1 — COORDINATE GEOMETRY (2D)
# ================================================================

class CoordinateGeometry2D:
    """Section formula, distance, midpoint, centroid, area of polygon."""

    @staticmethod
    def distance(P1, P2):
        """Distance between two points P1=(x1,y1), P2=(x2,y2)."""
        return _fmt(math.sqrt((P2[0]-P1[0])**2 + (P2[1]-P1[1])**2))

    @staticmethod
    def midpoint(P1, P2):
        """Midpoint of segment P1P2."""
        return (_fmt((P1[0]+P2[0])/2), _fmt((P1[1]+P2[1])/2))

    @staticmethod
    def section_formula(P1, P2, m, n, internal=True):
        """
        Point dividing P1P2 in ratio m:n.
        internal=True  → internal division
        internal=False → external division
        """
        if internal:
            x = (m*P2[0] + n*P1[0]) / (m + n)
            y = (m*P2[1] + n*P1[1]) / (m + n)
        else:
            if m == n:
                raise ValueError("External division undefined when m == n.")
            x = (m*P2[0] - n*P1[0]) / (m - n)
            y = (m*P2[1] - n*P1[1]) / (m - n)
        return (_fmt(x), _fmt(y))

    @staticmethod
    def centroid(points):
        """Centroid of a set of points [(x1,y1), ...]."""
        n = len(points)
        cx = sum(p[0] for p in points) / n
        cy = sum(p[1] for p in points) / n
        return (_fmt(cx), _fmt(cy))

    @staticmethod
    def area_of_triangle(P1, P2, P3):
        """Area of triangle using coordinate formula (shoelace)."""
        area = 0.5 * abs(
            P1[0]*(P2[1]-P3[1]) +
            P2[0]*(P3[1]-P1[1]) +
            P3[0]*(P1[1]-P2[1])
        )
        return _fmt(area)

    @staticmethod
    def area_of_polygon(points):
        """Area of a polygon using the shoelace formula."""
        n = len(points)
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        return _fmt(abs(area) / 2)

    @staticmethod
    def collinear(P1, P2, P3):
        """Check if three points are collinear (area == 0)."""
        area = CoordinateGeometry2D.area_of_triangle(P1, P2, P3)
        return area == 0


# ================================================================
# CHAPTER 2 — THE STRAIGHT LINE
# ================================================================

class StraightLine:
    """All standard forms of a straight line and related operations."""

    @staticmethod
    def slope(P1, P2):
        """Slope of line through P1 and P2."""
        if P2[0] == P1[0]:
            return float('inf')
        return _fmt((P2[1]-P1[1]) / (P2[0]-P1[0]))

    @staticmethod
    def slope_intercept(m, c):
        """y = mx + c  →  returns (m, c)."""
        return {"form": "y = mx + c", "m": m, "c": c,
                "equation": f"y = {m}x + {c}"}

    @staticmethod
    def intercept_form(a, b):
        """x/a + y/b = 1  →  returns coefficients."""
        return {"form": "x/a + y/b = 1", "a": a, "b": b,
                "standard": f"x/{a} + y/{b} = 1",
                "A": b, "B": a, "C": -a*b}  # Ax + By + C = 0

    @staticmethod
    def two_point_form(P1, P2):
        """
        Line through P1=(x1,y1) and P2=(x2,y2).
        Returns coefficients A, B, C for Ax + By + C = 0.
        """
        A = P2[1] - P1[1]
        B = P1[0] - P2[0]
        C = P2[0]*P1[1] - P1[0]*P2[1]
        return {"A": A, "B": B, "C": C,
                "equation": f"({A})x + ({B})y + ({C}) = 0"}

    @staticmethod
    def normal_form(p, alpha_deg):
        """
        Normal form: x·cos(α) + y·sin(α) = p
        p = perpendicular distance from origin, α = angle with x-axis.
        Returns A, B, C.
        """
        alpha = _rad(alpha_deg)
        A = _fmt(math.cos(alpha))
        B = _fmt(math.sin(alpha))
        return {"A": A, "B": B, "C": -p,
                "equation": f"{A}x + {B}y = {p}"}

    @staticmethod
    def point_slope_form(P, m):
        """y - y1 = m(x - x1)  →  Ax + By + C = 0."""
        # y - y1 = m(x - x1)  →  mx - y + (y1 - mx1) = 0
        A = m
        B = -1
        C = P[1] - m * P[0]
        return {"A": _fmt(A), "B": B, "C": _fmt(C),
                "equation": f"({_fmt(A)})x + ({B})y + ({_fmt(C)}) = 0"}

    @staticmethod
    def perpendicular_distance(A, B, C, P):
        """
        Distance from point P=(x0,y0) to line Ax + By + C = 0.
        Formula: |Ax0 + By0 + C| / sqrt(A²+B²)
        """
        num = abs(A*P[0] + B*P[1] + C)
        den = math.sqrt(A**2 + B**2)
        return _fmt(num / den)

    @staticmethod
    def intersection(A1, B1, C1, A2, B2, C2):
        """
        Intersection of A1x+B1y+C1=0 and A2x+B2y+C2=0.
        Returns (x, y) or None if parallel.
        """
        det = A1*B2 - A2*B1
        if abs(det) < 1e-12:
            return None  # parallel or coincident
        x = (B1*C2 - B2*C1) / det
        y = (A2*C1 - A1*C2) / det
        return (_fmt(x), _fmt(y))

    @staticmethod
    def angle_between(m1, m2):
        """Acute angle between two lines with slopes m1 and m2 (degrees)."""
        if m1 == float('inf') or m2 == float('inf'):
            # One line is vertical
            other = m2 if m1 == float('inf') else m1
            angle = 90 - abs(_deg(math.atan(other)))
            return _fmt(angle)
        tan_theta = abs((m1 - m2) / (1 + m1*m2)) if (1 + m1*m2) != 0 else float('inf')
        if tan_theta == float('inf'):
            return 90.0
        return _fmt(_deg(math.atan(tan_theta)))

    @staticmethod
    def are_parallel(m1, m2, tol=1e-9):
        return abs(m1 - m2) < tol

    @staticmethod
    def are_perpendicular(m1, m2, tol=1e-9):
        if m1 == float('inf'):
            return m2 == 0
        if m2 == float('inf'):
            return m1 == 0
        return abs(m1 * m2 + 1) < tol

    @staticmethod
    def angle_bisectors(A1, B1, C1, A2, B2, C2):
        """
        Equations of angle bisectors of lines A1x+B1y+C1=0 and A2x+B2y+C2=0.
        Returns two bisector equations as (A, B, C) tuples.
        """
        r1 = math.sqrt(A1**2 + B1**2)
        r2 = math.sqrt(A2**2 + B2**2)
        # (A1x+B1y+C1)/r1 = ±(A2x+B2y+C2)/r2
        # Bisector 1: A1*r2*x + B1*r2*y + C1*r2 - A2*r1*x - B2*r1*y - C2*r1 = 0
        b1 = (A1*r2 - A2*r1, B1*r2 - B2*r1, C1*r2 - C2*r1)
        b2 = (A1*r2 + A2*r1, B1*r2 + B2*r1, C1*r2 + C2*r1)
        return b1, b2

    @staticmethod
    def concurrent(lines):
        """
        Check if three lines [( A1,B1,C1), (A2,B2,C2), (A3,B3,C3)] are concurrent.
        Concurrent if det([[A1,B1,C1],[A2,B2,C2],[A3,B3,C3]]) == 0.
        """
        (A1,B1,C1),(A2,B2,C2),(A3,B3,C3) = lines
        det = (A1*(B2*C3-B3*C2) - B1*(A2*C3-A3*C2) + C1*(A2*B3-A3*B2))
        return abs(det) < 1e-9


# ================================================================
# CHAPTER 3 — PAIR OF STRAIGHT LINES
# ================================================================

class PairOfLines:
    """
    Homogeneous 2nd degree: ax² + 2hxy + by² = 0
    General 2nd degree:     ax² + 2hxy + by² + 2gx + 2fy + c = 0
    """

    @staticmethod
    def angle_between_pair(a, h, b):
        """
        Angle between the pair ax² + 2hxy + by² = 0.
        tan θ = 2√(h²-ab) / (a+b)
        """
        discriminant = h**2 - a*b
        if discriminant < 0:
            raise ValueError("h²-ab < 0: lines are imaginary.")
        if (a + b) == 0:
            return 90.0
        tan_theta = 2 * math.sqrt(discriminant) / abs(a + b)
        return _fmt(_deg(math.atan(tan_theta)))

    @staticmethod
    def is_pair_perpendicular(a, b):
        """Lines are perpendicular iff a + b = 0."""
        return abs(a + b) < 1e-9

    @staticmethod
    def bisector_pair(a, h, b):
        """
        Equation of bisectors of ax²+2hxy+by²=0.
        Returns (A, B, C) for: (x²-y²)/h = 2xy/(a-b)
        i.e., h(x²-y²) - (a-b)xy = 0  →  hx²-(a-b)xy-hy²=0
        """
        return {"equation": f"{h}x² - {a-b}xy - {h}y² = 0",
                "a_coeff": h, "h_coeff": -(a-b)/2, "b_coeff": -h}

    @staticmethod
    def condition_general_to_pair(a, h, b, g, f, c):
        """
        Condition for ax²+2hxy+by²+2gx+2fy+c=0 to represent a pair of lines.
        Δ = abc + 2fgh - af² - bg² - ch² = 0
        """
        delta = a*b*c + 2*f*g*h - a*f**2 - b*g**2 - c*h**2
        return {"delta": _fmt(delta), "is_pair_of_lines": abs(delta) < 1e-9}

    @staticmethod
    def individual_lines_from_homogeneous(a, h, b):
        """
        Solve ax²+2hxy+by²=0 for y/x = m.
        bm²+2hm+a=0  (treating y=mx).
        Returns the two slopes.
        """
        if b == 0:
            # one line is y-axis (x=0) and hx+by=0
            if h == 0:
                return (0, float('inf'))
            return (0, -a/(2*h))
        disc = h**2 - a*b
        if disc < 0:
            m1 = (-h + cmath.sqrt(disc)) / b
            m2 = (-h - cmath.sqrt(disc)) / b
        else:
            m1 = (-h + math.sqrt(disc)) / b
            m2 = (-h - math.sqrt(disc)) / b
        return (_fmt(m1), _fmt(m2))


# ================================================================
# CHAPTER 4 — CIRCLE
# ================================================================

class Circle:
    """
    General equation: x²+y²+2gx+2fy+c=0
    Centre = (-g, -f), Radius = √(g²+f²-c)
    """

    @staticmethod
    def from_centre_radius(h, k, r):
        """(x-h)²+(y-k)²=r²  →  x²+y²-2hx-2ky+(h²+k²-r²)=0."""
        g, f, c = -h, -k, h**2 + k**2 - r**2
        return {"centre": (h, k), "radius": r, "g": g, "f": f, "c": c,
                "equation": f"x² + y² + ({2*g})x + ({2*f})y + ({c}) = 0"}

    @staticmethod
    def from_general(g, f, c):
        """Extract centre and radius from x²+y²+2gx+2fy+c=0."""
        r_sq = g**2 + f**2 - c
        if r_sq < 0:
            raise ValueError("r² < 0: circle is imaginary.")
        return {"centre": (_fmt(-g), _fmt(-f)),
                "radius": _fmt(math.sqrt(r_sq)),
                "g": g, "f": f, "c": c}

    @staticmethod
    def from_diameter(P1, P2):
        """Circle with P1P2 as diameter: (x-x1)(x-x2)+(y-y1)(y-y2)=0."""
        g = -(P1[0]+P2[0])/2
        f = -(P1[1]+P2[1])/2
        c = P1[0]*P2[0] + P1[1]*P2[1]
        return Circle.from_general(g, f, c)

    @staticmethod
    def length_of_tangent(g, f, c, P):
        """Length of tangent from P=(x1,y1) to x²+y²+2gx+2fy+c=0."""
        val = P[0]**2 + P[1]**2 + 2*g*P[0] + 2*f*P[1] + c
        if val < 0:
            raise ValueError("Point is inside the circle.")
        return _fmt(math.sqrt(val))

    @staticmethod
    def tangent_at_point(g, f, c, P):
        """
        Equation of tangent at P=(x1,y1) on x²+y²+2gx+2fy+c=0.
        xx1 + yy1 + g(x+x1) + f(y+y1) + c = 0
        Returns (A, B, C).
        """
        x1, y1 = P
        A = x1 + g
        B = y1 + f
        C = g*x1 + f*y1 + c
        return {"A": _fmt(A), "B": _fmt(B), "C": _fmt(C),
                "equation": f"({_fmt(A)})x + ({_fmt(B)})y + ({_fmt(C)}) = 0"}

    @staticmethod
    def chord_of_contact(g, f, c, P):
        """
        Chord of contact of tangents from P=(x1,y1).
        Same form as tangent at a point on circle.
        """
        return Circle.tangent_at_point(g, f, c, P)

    @staticmethod
    def polar_of_point(g, f, c, P):
        """Polar of P=(x1,y1) w.r.t. circle — same as chord of contact."""
        return Circle.tangent_at_point(g, f, c, P)

    @staticmethod
    def condition_tangent_line(g, f, c, m, d):
        """
        Condition for y = mx + d to be tangent to x²+y²+2gx+2fy+c=0.
        Returns True/False and the condition value.
        """
        # centre=(-g,-f), radius=r
        centre = (-g, -f)
        r_sq = g**2 + f**2 - c
        r = math.sqrt(r_sq)
        dist = StraightLine.perpendicular_distance(m, -1, d, centre)
        return {"tangent": abs(dist - r) < 1e-9, "distance": dist, "radius": _fmt(r)}

    @staticmethod
    def chord_midpoint(g, f, c, M):
        """
        Equation of chord of x²+y²+2gx+2fy+c=0 whose midpoint is M=(h,k).
        T = S₁: xh+yk+g(x+h)+f(y+k)+c = h²+k²+2gh+2fk+c
        Simplified to Ax+By+C=0.
        """
        h, k = M
        A = h + g
        B = k + f
        C = g*h + f*k + c - (h**2 + k**2 + 2*g*h + 2*f*k + c)
        C = -(h**2 + k**2 + g*h + f*k)
        return {"A": _fmt(A), "B": _fmt(B), "C": _fmt(C),
                "equation": f"({_fmt(A)})x + ({_fmt(B)})y + ({_fmt(C)}) = 0"}


# ================================================================
# CHAPTER 5 — SYSTEM OF CIRCLES
# ================================================================

class SystemOfCircles:
    """Radical axis, orthogonality, coaxal systems."""

    @staticmethod
    def radical_axis(g1, f1, c1, g2, f2, c2):
        """
        Radical axis of two circles S1 and S2.
        S1 - S2 = 0  →  2(g1-g2)x + 2(f1-f2)y + (c1-c2) = 0
        """
        A = 2*(g1 - g2)
        B = 2*(f1 - f2)
        C = c1 - c2
        return {"A": A, "B": B, "C": C,
                "equation": f"({A})x + ({B})y + ({C}) = 0"}

    @staticmethod
    def are_orthogonal(g1, f1, c1, g2, f2, c2):
        """
        Two circles are orthogonal iff 2g1g2 + 2f1f2 = c1 + c2.
        """
        lhs = 2*g1*g2 + 2*f1*f2
        rhs = c1 + c2
        return {"orthogonal": abs(lhs - rhs) < 1e-9, "lhs": lhs, "rhs": rhs}

    @staticmethod
    def limiting_points(g, f, c, k_values):
        """
        Limiting points of the coaxal system S + λ·L = 0 at given λ values.
        Returns centres of the point-circles.
        """
        results = []
        for k in k_values:
            # Simplified: for coaxal system x²+y²+2gx+2fy+c+k(2lx+2my+n)=0
            results.append(f"λ={k}: depends on specific coaxal system definition.")
        return results


# ================================================================
# CHAPTER 6 — PARABOLA
# ================================================================

class Parabola:
    """Standard parabola y² = 4ax and its forms."""

    def __init__(self, a):
        """y² = 4ax with parameter a > 0."""
        self.a = a

    def focus(self):
        return (self.a, 0)

    def directrix(self):
        return f"x = {-self.a}"

    def vertex(self):
        return (0, 0)

    def latus_rectum_length(self):
        return 4 * self.a

    def point_on_parabola(self, t):
        """Parametric point: (at², 2at)."""
        return (_fmt(self.a * t**2), _fmt(2 * self.a * t))

    def tangent_at_t(self, t):
        """Tangent at parametric point t: ty = x + at²."""
        a = self.a
        return {"equation": f"ty = x + {_fmt(a*t**2)}",
                "A": -1, "B": t, "C": _fmt(a * t**2),
                "note": "ty - x - at² = 0"}

    def normal_at_t(self, t):
        """Normal at t: y + tx = 2at + at³."""
        a = self.a
        rhs = _fmt(2*a*t + a*t**3)
        return {"equation": f"y + {t}x = {rhs}",
                "A": t, "B": 1, "C": -rhs}

    def chord_joining_t1_t2(self, t1, t2):
        """Chord joining t1 and t2: y(t1+t2) = 2x + 2at1t2."""
        a = self.a
        return {"equation": f"y({t1+t2}) = 2x + {_fmt(2*a*t1*t2)}"}

    def tangent_at_point(self, x1, y1):
        """Tangent at (x1,y1) on y²=4ax: yy1 = 2a(x+x1)."""
        return {"equation": f"{y1}y = {2*self.a}(x + {x1})"}

    def chord_of_contact(self, P):
        """Chord of contact from external point P=(h,k): ky = 2a(x+h)."""
        h, k = P
        return {"equation": f"{k}y = {2*self.a}(x + {h})"}

    def condition_tangent_line(self, m, c):
        """y=mx+c is tangent to y²=4ax iff c = a/m."""
        expected_c = self.a / m
        return {"tangent": abs(c - expected_c) < 1e-9,
                "required_c": _fmt(expected_c), "given_c": c}

    def polar_of_point(self, P):
        """Polar of P=(h,k): ky = 2a(x+h)."""
        return self.chord_of_contact(P)

    def intersection_tangents(self, t1, t2):
        """Point of intersection of tangents at t1 and t2: (at1t2, a(t1+t2))."""
        a = self.a
        return (_fmt(a*t1*t2), _fmt(a*(t1+t2)))

    def normals_from_point(self, h, k):
        """
        Normals from (h,k): at³ + t(2a-h) - k = 0.
        Returns the cubic coefficients; roots give t values.
        """
        a = self.a
        # at³ + (2a-h)t - k = 0
        # Use numpy if available, else return coefficients
        coeffs = [a, 0, (2*a - h), -k]
        try:
            import numpy as np
            roots = np.roots(coeffs)
            return {"t_values": [_fmt(r) for r in roots],
                    "cubic": f"{a}t³ + ({2*a-h})t + ({-k}) = 0"}
        except ImportError:
            return {"cubic_coefficients": coeffs,
                    "cubic": f"{a}t³ + ({2*a-h})t + ({-k}) = 0"}


# ================================================================
# CHAPTER 7 — ELLIPSE
# ================================================================

class Ellipse:
    """Standard ellipse x²/a² + y²/b² = 1, a > b > 0."""

    def __init__(self, a, b):
        if a <= 0 or b <= 0:
            raise ValueError("a and b must be positive.")
        self.a, self.b = a, b
        self.c = math.sqrt(abs(a**2 - b**2))
        self.e = self.c / a  # eccentricity

    def info(self):
        a, b, c, e = self.a, self.b, self.c, self.e
        major_axis = "x" if a > b else "y"
        return {
            "a": a, "b": b,
            "centre": (0, 0),
            "foci": [(_fmt(c), 0), (_fmt(-c), 0)] if a > b else [(0,_fmt(c)),(0,_fmt(-c))],
            "eccentricity": _fmt(e),
            "semi_latus_rectum": _fmt(b**2 / a),
            "latus_rectum_length": _fmt(2*b**2 / a),
            "directrices": f"x = ±{_fmt(a/e)}" if a > b else f"y = ±{_fmt(a/e)}",
            "major_axis": major_axis
        }

    def is_on_ellipse(self, P, tol=1e-9):
        return abs(P[0]**2/self.a**2 + P[1]**2/self.b**2 - 1) < tol

    def parametric_point(self, theta_deg):
        """(a·cosθ, b·sinθ)."""
        t = _rad(theta_deg)
        return (_fmt(self.a * math.cos(t)), _fmt(self.b * math.sin(t)))

    def tangent_at_point(self, x1, y1):
        """Tangent at (x1,y1): xx1/a²+yy1/b²=1."""
        a, b = self.a, self.b
        return {"equation": f"x·{x1}/{a**2} + y·{y1}/{b**2} = 1"}

    def tangent_at_theta(self, theta_deg):
        """Tangent at eccentric angle θ: x·cosθ/a + y·sinθ/b = 1."""
        t = _rad(theta_deg)
        cos_t, sin_t = _fmt(math.cos(t)), _fmt(math.sin(t))
        return {"equation": f"x·{cos_t}/{self.a} + y·{sin_t}/{self.b} = 1"}

    def condition_tangent_line(self, m, c):
        """y=mx+c is tangent iff c²=a²m²+b²."""
        a, b = self.a, self.b
        required_c_sq = a**2 * m**2 + b**2
        return {"tangent": abs(c**2 - required_c_sq) < 1e-9,
                "c²_required": _fmt(required_c_sq), "c²_given": _fmt(c**2),
                "tangent_form": f"y = {m}x ± √({_fmt(required_c_sq)})"}

    def conjugate_diameters(self, m1):
        """
        If m1 is slope of one diameter, conjugate diameter slope m2.
        m1·m2 = -b²/a²
        """
        m2 = -(self.b**2) / (self.a**2 * m1)
        return _fmt(m2)

    def chord_midpoint(self, M):
        """Chord with midpoint M=(h,k): hx/a²+ky/b²=h²/a²+k²/b²."""
        h, k = M
        a, b = self.a, self.b
        rhs = _fmt(h**2/a**2 + k**2/b**2)
        return {"equation": f"{h}x/{a**2} + {k}y/{b**2} = {rhs}"}

    def focal_distances(self, x1):
        """Focal radii from point with x-coordinate x1."""
        a, e = self.a, self.e
        r1 = _fmt(a - e*x1)  # from nearer focus
        r2 = _fmt(a + e*x1)  # from farther focus
        return {"SP": r1, "S'P": r2, "sum": _fmt(r1+r2), "check_2a": 2*a}


# ================================================================
# CHAPTER 8 — HYPERBOLA
# ================================================================

class Hyperbola:
    """Standard hyperbola x²/a² - y²/b² = 1."""

    def __init__(self, a, b):
        self.a, self.b = a, b
        self.c = math.sqrt(a**2 + b**2)
        self.e = self.c / a

    def info(self):
        a, b, c, e = self.a, self.b, self.c, self.e
        return {
            "a": a, "b": b,
            "foci": [(_fmt(c), 0), (_fmt(-c), 0)],
            "eccentricity": _fmt(e),
            "asymptotes": [f"y = {_fmt(b/a)}x", f"y = {_fmt(-b/a)}x"],
            "latus_rectum": _fmt(2*b**2/a),
            "directrices": f"x = ±{_fmt(a/e)}"
        }

    def asymptotes(self):
        """Returns slopes of asymptotes."""
        return (_fmt(self.b/self.a), _fmt(-self.b/self.a))

    def condition_tangent_line(self, m, c):
        """y=mx+c tangent to hyperbola iff c²=a²m²-b²."""
        required_c_sq = self.a**2 * m**2 - self.b**2
        return {"tangent": abs(c**2 - required_c_sq) < 1e-9,
                "c²_required": _fmt(required_c_sq)}

    def tangent_at_point(self, x1, y1):
        return {"equation": f"x·{x1}/{self.a**2} - y·{y1}/{self.b**2} = 1"}

    def rectangular_hyperbola_xy(self, c_sq):
        """
        Rectangular hyperbola xy = c² (when a=b, rotated 45°).
        Parametric point: (c·t, c/t).
        """
        c = math.sqrt(c_sq)
        return {"equation": f"xy = {c_sq}",
                "parametric": "(ct, c/t)",
                "tangent_at_t": f"x + t²y = 2ct",
                "normal_at_t": f"t³x - ty = c(t⁴-1)"}


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 9 — POLAR COORDINATES
# ─────────────────────────────────────────────────────────────────────────────

class PolarCoordinates:
    """Conversion and polar forms of curves."""

    @staticmethod
    def to_cartesian(r, theta_deg):
        """Polar (r, θ) → Cartesian (x, y)."""
        t = _rad(theta_deg)
        return (_fmt(r * math.cos(t)), _fmt(r * math.sin(t)))

    @staticmethod
    def to_polar(x, y):
        """Cartesian (x, y) → Polar (r, θ_deg)."""
        r = math.sqrt(x**2 + y**2)
        theta = math.atan2(y, x)
        return (_fmt(r), _fmt(_deg(theta)))

    @staticmethod
    def polar_line_normal_form(p, alpha_deg):
        """
        Polar equation of line in normal form: r·cos(θ-α) = p.
        """
        return {"equation": f"r·cos(θ - {alpha_deg}°) = {p}",
                "p": p, "alpha_deg": alpha_deg}

    @staticmethod
    def polar_circle(a, alpha_deg):
        """
        Circle r = 2a·cos(θ-α): centre at (a, α) in polar, passes through pole.
        """
        return {"equation": f"r = {2*a}·cos(θ - {alpha_deg}°)"}

    @staticmethod
    def polar_conic(l, e):
        """
        Polar equation of conic: r = l/(1 - e·cosθ) or r = l/(1 + e·cosθ).
        l = semi-latus rectum, e = eccentricity.
        Returns conic type.
        """
        if e < 1:
            conic_type = "Ellipse"
        elif e == 1:
            conic_type = "Parabola"
        else:
            conic_type = "Hyperbola"
        return {"equation": f"r = {l} / (1 - {e}·cosθ)",
                "conic_type": conic_type, "e": e, "l": l}


# ================================================================
# CHAPTER 10 — CONIC TRACING (General 2nd Degree)
# ================================================================

class ConicTracing:
    """
    General 2nd degree: ax²+2hxy+by²+2gx+2fy+c=0.
    Identify, find centre, trace the conic.
    """

    def __init__(self, a, h, b, g, f, c):
        self.a, self.h, self.b = a, h, b
        self.g, self.f, self.c = g, f, c

    def delta(self):
        """Discriminant Δ = abc+2fgh-af²-bg²-ch²."""
        a, h, b, g, f, c = self.a, self.h, self.b, self.g, self.f, self.c
        return a*b*c + 2*f*g*h - a*f**2 - b*g**2 - c*h**2

    def J(self):
        """J = ab - h²."""
        return self.a*self.b - self.h**2

    def I(self):
        """I = a + b (sum of diagonal terms)."""
        return self.a + self.b

    def identify(self):
        """Identify the conic from invariants."""
        D = self.delta()
        J = self.J()
        a, b, h = self.a, self.b, self.h

        if abs(D) < 1e-9:
            # Degenerate
            if abs(J) < 1e-9:
                return "Pair of parallel lines (or two coincident lines)"
            elif J < 0:
                return "Pair of intersecting real lines"
            else:
                return "Pair of imaginary lines (degenerate ellipse)"
        else:
            if abs(J) < 1e-9:
                return "Parabola"
            elif J > 0:
                if (a + b) * D < 0:
                    return "Real Ellipse"
                else:
                    return "Imaginary Ellipse (no real curve)"
            else:
                return "Hyperbola (J < 0)" if abs(a-b)>1e-9 or abs(h)>1e-9 else "Rectangular Hyperbola"

    def centre(self):
        """
        Centre of conic: solve ∂F/∂x=0, ∂F/∂y=0.
        ax+hy+g=0, hx+by+f=0.
        """
        a, h, b, g, f = self.a, self.h, self.b, self.g, self.f
        det = a*b - h**2
        if abs(det) < 1e-9:
            return None  # parabola has no centre
        x0 = (h*f - b*g) / det
        y0 = (h*g - a*f) / det
        return (_fmt(x0), _fmt(y0))

    def full_analysis(self):
        return {
            "conic_type": self.identify(),
            "Δ (delta)": _fmt(self.delta()),
            "J (=ab-h²)": _fmt(self.J()),
            "I (=a+b)": _fmt(self.I()),
            "centre": self.centre()
        }


# ================================================================
# CHAPTER 11 — THREE-DIMENSIONAL GEOMETRY
# ================================================================

class Geometry3D:
    """Distance, direction cosines, centroid in 3D."""

    @staticmethod
    def distance(P1, P2):
        return _fmt(math.sqrt(sum((b-a)**2 for a,b in zip(P1,P2))))

    @staticmethod
    def midpoint(P1, P2):
        return tuple(_fmt((a+b)/2) for a,b in zip(P1,P2))

    @staticmethod
    def section_formula(P1, P2, m, n, internal=True):
        if internal:
            pt = tuple((m*b + n*a)/(m+n) for a,b in zip(P1,P2))
        else:
            pt = tuple((m*b - n*a)/(m-n) for a,b in zip(P1,P2))
        return tuple(_fmt(v) for v in pt)

    @staticmethod
    def centroid_triangle(P1, P2, P3):
        return tuple(_fmt((a+b+c)/3) for a,b,c in zip(P1,P2,P3))

    @staticmethod
    def centroid_tetrahedron(P1, P2, P3, P4):
        return tuple(_fmt((a+b+c+d)/4) for a,b,c,d in zip(P1,P2,P3,P4))

    @staticmethod
    def direction_cosines(direction_vector):
        """Compute l, m, n from direction vector (a,b,c)."""
        a, b, c = direction_vector
        mag = math.sqrt(a**2 + b**2 + c**2)
        l, m, n = a/mag, b/mag, c/mag
        return {"l": _fmt(l), "m": _fmt(m), "n": _fmt(n),
                "check_l²+m²+n²": _fmt(l**2+m**2+n**2)}

    @staticmethod
    def direction_ratios_to_cosines(a, b, c):
        return Geometry3D.direction_cosines((a, b, c))

    @staticmethod
    def angle_between_lines(dv1, dv2):
        """Angle between two lines given direction vectors."""
        dot = sum(a*b for a,b in zip(dv1,dv2))
        mag1 = math.sqrt(sum(x**2 for x in dv1))
        mag2 = math.sqrt(sum(x**2 for x in dv2))
        cos_theta = dot / (mag1 * mag2)
        cos_theta = max(-1, min(1, cos_theta))
        return _fmt(_deg(math.acos(abs(cos_theta))))  # acute angle


# ================================================================
# CHAPTER 12 — PLANE
# ================================================================

class Plane3D:
    """General plane ax+by+cz+d=0 and related operations."""

    @staticmethod
    def from_intercepts(a, b, c):
        """Intercept form x/a+y/b+z/c=1  →  bcx+acy+abz-abc=0."""
        A, B, C, D = b*c, a*c, a*b, -a*b*c
        return {"A": A, "B": B, "C": C, "D": D,
                "equation": f"({A})x + ({B})y + ({C})z + ({D}) = 0"}

    @staticmethod
    def from_normal_and_point(normal, P):
        """Plane with normal n=(a,b,c) passing through P=(x0,y0,z0)."""
        a, b, c = normal
        D = -(a*P[0] + b*P[1] + c*P[2])
        return {"A": a, "B": b, "C": c, "D": D,
                "equation": f"({a})x + ({b})y + ({c})z + ({D}) = 0"}

    @staticmethod
    def distance_point_plane(A, B, C, D, P):
        """Distance from P=(x0,y0,z0) to Ax+By+Cz+D=0."""
        num = abs(A*P[0] + B*P[1] + C*P[2] + D)
        den = math.sqrt(A**2 + B**2 + C**2)
        return _fmt(num / den)

    @staticmethod
    def angle_between_planes(n1, n2):
        """Angle between planes with normals n1, n2."""
        return Geometry3D.angle_between_lines(n1, n2)

    @staticmethod
    def angle_between_plane_and_line(normal, direction):
        """Angle between plane (normal n) and line (direction d). sin θ = |n·d|/(|n||d|)."""
        dot = abs(sum(a*b for a,b in zip(normal, direction)))
        mag_n = math.sqrt(sum(x**2 for x in normal))
        mag_d = math.sqrt(sum(x**2 for x in direction))
        sin_theta = dot / (mag_n * mag_d)
        sin_theta = min(1, sin_theta)
        return _fmt(_deg(math.asin(sin_theta)))

    @staticmethod
    def three_points_plane(P1, P2, P3):
        """Plane through three points."""
        # Two vectors in plane
        v1 = [P2[i]-P1[i] for i in range(3)]
        v2 = [P3[i]-P1[i] for i in range(3)]
        # Normal = v1 × v2
        a = v1[1]*v2[2] - v1[2]*v2[1]
        b = v1[2]*v2[0] - v1[0]*v2[2]
        c = v1[0]*v2[1] - v1[1]*v2[0]
        return Plane3D.from_normal_and_point((a, b, c), P1)


# ================================================================
# CHAPTER 13 — STRAIGHT LINE IN 3D
# ================================================================

class Line3D:
    """Straight line in 3D: symmetric and parametric forms, skew lines."""

    @staticmethod
    def symmetric_form(P, direction):
        """
        Symmetric form: (x-x0)/l = (y-y0)/m = (z-z0)/n
        """
        x0,y0,z0 = P
        l,m,n = direction
        return {"equation": f"(x-{x0})/{l} = (y-{y0})/{m} = (z-{z0})/{n}",
                "point": P, "direction": direction}

    @staticmethod
    def parametric_point(P, direction, t):
        """Point on line at parameter t."""
        return tuple(_fmt(P[i] + t*direction[i]) for i in range(3))

    @staticmethod
    def angle_between_lines(d1, d2):
        return Geometry3D.angle_between_lines(d1, d2)

    @staticmethod
    def skew_lines_distance(P1, d1, P2, d2):
        """
        Shortest distance between two skew lines.
        SD = |(P2-P1)·(d1×d2)| / |d1×d2|
        """
        # Cross product d1 × d2
        n = [d1[1]*d2[2]-d1[2]*d2[1],
             d1[2]*d2[0]-d1[0]*d2[2],
             d1[0]*d2[1]-d1[1]*d2[0]]
        mag_n = math.sqrt(sum(x**2 for x in n))
        if mag_n < 1e-12:
            # Lines are parallel
            v = [P2[i]-P1[i] for i in range(3)]
            cross = [d1[1]*v[2]-d1[2]*v[1],
                     d1[2]*v[0]-d1[0]*v[2],
                     d1[0]*v[1]-d1[1]*v[0]]
            return _fmt(math.sqrt(sum(x**2 for x in cross)) / math.sqrt(sum(x**2 for x in d1)))
        diff = [P2[i]-P1[i] for i in range(3)]
        dot = sum(diff[i]*n[i] for i in range(3))
        return _fmt(abs(dot) / mag_n)

    @staticmethod
    def two_planes_to_line(A1,B1,C1,D1, A2,B2,C2,D2):
        """
        Line as intersection of two planes — returns direction vector (cross product of normals).
        """
        n1, n2 = [A1,B1,C1], [A2,B2,C2]
        d = [n1[1]*n2[2]-n1[2]*n2[1],
             n1[2]*n2[0]-n1[0]*n2[2],
             n1[0]*n2[1]-n1[1]*n2[0]]
        return {"direction_vector": tuple(_fmt(x) for x in d)}


# ================================================================
# CHAPTER 14 — SPHERE
# ================================================================

class Sphere3D:
    """Sphere: (x-a)²+(y-b)²+(z-c)²=r², general: x²+y²+z²+2ux+2vy+2wz+d=0."""

    @staticmethod
    def from_centre_radius(centre, r):
        a, b, c = centre
        d = a**2 + b**2 + c**2 - r**2
        return {"centre": centre, "radius": r,
                "u": -a, "v": -b, "w": -c, "d": d,
                "equation": f"x²+y²+z²+({-2*a})x+({-2*b})y+({-2*c})z+({d})=0"}

    @staticmethod
    def from_general(u, v, w, d):
        r_sq = u**2 + v**2 + w**2 - d
        if r_sq < 0:
            raise ValueError("r² < 0: imaginary sphere.")
        return {"centre": (_fmt(-u), _fmt(-v), _fmt(-w)),
                "radius": _fmt(math.sqrt(r_sq))}

    @staticmethod
    def from_diameter(P1, P2):
        """Sphere with P1P2 as diameter."""
        x1,y1,z1 = P1
        x2,y2,z2 = P2
        u = -(x1+x2)/2; v = -(y1+y2)/2; w = -(z1+z2)/2
        d = x1*x2 + y1*y2 + z1*z2
        return Sphere3D.from_general(u, v, w, d)

    @staticmethod
    def tangent_plane(u, v, w, d, P):
        """Tangent plane at P=(x1,y1,z1) to x²+y²+z²+2ux+2vy+2wz+d=0."""
        x1,y1,z1 = P
        # xx1+yy1+zz1+u(x+x1)+v(y+y1)+w(z+z1)+d=0
        A = x1 + u; B = y1 + v; C = z1 + w
        D = u*x1 + v*y1 + w*z1 + d
        return {"A": _fmt(A), "B": _fmt(B), "C": _fmt(C), "D": _fmt(D),
                "equation": f"({_fmt(A)})x+({_fmt(B)})y+({_fmt(C)})z+({_fmt(D)})=0"}


# ================================================================
# CHAPTER 15 — CONE
# ================================================================

class Cone3D:
    """Right circular cone and general cone through vertex."""

    @staticmethod
    def right_circular(vertex, axis_direction, semi_vertical_angle_deg):
        """
        Equation of right circular cone.
        If vertex at origin, axis along (l,m,n), semi-vertical angle α:
        (lx+my+nz)² = cos²α · (x²+y²+z²)(l²+m²+n²)
        """
        l, m, n = axis_direction
        alpha = _rad(semi_vertical_angle_deg)
        cos2 = _fmt(math.cos(alpha)**2)
        mag2 = l**2 + m**2 + n**2
        return {"equation": f"({l}x+{m}y+{n}z)² = {cos2}·(x²+y²+z²)·{mag2}",
                "vertex": vertex, "axis": axis_direction,
                "semi_vertical_angle_deg": semi_vertical_angle_deg}

    @staticmethod
    def semi_vertical_angle(vertex, axis_direction, point_on_cone):
        """Compute semi-vertical angle from vertex, axis direction, and a point on cone."""
        v = [point_on_cone[i]-vertex[i] for i in range(3)]
        l, m, n = axis_direction
        dot = l*v[0] + m*v[1] + n*v[2]
        mag_axis = math.sqrt(l**2+m**2+n**2)
        mag_v = math.sqrt(sum(x**2 for x in v))
        cos_alpha = dot / (mag_axis * mag_v)
        cos_alpha = max(-1, min(1, cos_alpha))
        return _fmt(_deg(math.acos(abs(cos_alpha))))


# ================================================================
# CHAPTER 16 — CYLINDER
# ================================================================

class Cylinder3D:
    """Right circular cylinder."""

    @staticmethod
    def right_circular(axis_point, axis_direction, r):
        """
        Right circular cylinder: axis through P0=(x0,y0,z0) with direction (l,m,n), radius r.
        The equation is |d|² - (d·v̂)² = r²  where d = P - P0.
        """
        x0,y0,z0 = axis_point
        l,m,n = axis_direction
        mag2 = l**2+m**2+n**2
        return {
            "axis_point": axis_point,
            "axis_direction": axis_direction,
            "radius": r,
            "description": (
                f"Points (x,y,z) where distance from axis = {r}. "
                f"Axis: (x-{x0})/{l}=(y-{y0})/{m}=(z-{z0})/{n}."
            )
        }

    @staticmethod
    def axis_along_z(r):
        """Right circular cylinder x²+y²=r² (axis along z-axis)."""
        return {"equation": f"x² + y² = {r**2}", "radius": r,
                "axis": "z-axis"}


