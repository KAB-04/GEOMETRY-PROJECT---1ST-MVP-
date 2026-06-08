# ================================================================
#  EUCLIDEAN GEOMETRY ENGINE 2
#  Contents:
# 1.Circle Measurement 
# 2.Plane Transformations (reflections, translations, rotations, homotheties, similarities, inversions)
# 3.Space Geometry(lines, planes, angles, distances)
# 4.Areas & Volumes (solids: sphere, cylinder, cone, pyramid, prism)
# 5.Conic Sections (parabola, ellipse, hyperbola)
# 6.Space Transformations (reflections, translations, rotations,homotheties, similarities in 3-D)
# ================================================================

from __future__ import annotations
import math
import cmath
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union
import sys

# ================================================================
# 0.  Foundations & Axiom.
# ================================================================

def axiom1_1_limit(seq_fn, start: int = 4, doublings: int = 18) -> float:
    """
     Every bounded increasing sequence of reals has a limit.
    
    Numerically realises the axiom by generating the sequence
        a_n = seq_fn(n)   for n = start, 2*start, 4*start, ...
    and returning the limiting value once successive terms agree to
    machine precision.  Used internally by circle-perimeter and area
    limits (Lemmas 1.2, 1.3, 1.6, 1.7).
    """
    n = start
    prev = seq_fn(n)
    for _ in range(doublings):
        n *= 2
        curr = seq_fn(n)
        if abs(curr - prev) < 1e-14 * abs(curr):
            return curr
        prev = curr
    return curr


# ================================================================
# 1.  Basic geometry primitives
# ================================================================

@dataclass
class Point2D:
    x: float
    y: float

    def __add__(self, other: "Point2D") -> "Point2D":
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point2D") -> "Point2D":
        return Point2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Point2D":
        return Point2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Point2D":
        return self.__mul__(scalar)

    def distance_to(self, other: "Point2D") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def norm(self) -> float:
        return math.hypot(self.x, self.y)

    def dot(self, other: "Point2D") -> float:
        return self.x * other.x + self.y * other.y

    def __repr__(self) -> str:
        return f"Point2D({self.x:.6g}, {self.y:.6g})"


@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def __add__(self, other: "Point3D") -> "Point3D":
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Point3D") -> "Point3D":
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, s: float) -> "Point3D":
        return Point3D(self.x * s, self.y * s, self.z * s)

    def __rmul__(self, s: float) -> "Point3D":
        return self.__mul__(s)

    def norm(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def dot(self, other: "Point3D") -> float:
        return self.x*other.x + self.y*other.y + self.z*other.z

    def cross(self, other: "Point3D") -> "Point3D":
        return Point3D(
            self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y - self.y*other.x,
        )

    def distance_to(self, other: "Point3D") -> float:
        return (self - other).norm()

    def __repr__(self) -> str:
        return f"Point3D({self.x:.6g}, {self.y:.6g}, {self.z:.6g})"


# ================================================================
# 2.  Chapter 1 – Circle Measurement
# ================================================================-

PI = math.pi  # π, the constant proved unique in Theorem 1.1


# ------ Lemma 1.1 – inscribed regular polygon side & apothem ---------------

def inscribed_polygon_side(rho: float, mu: int) -> float:
    """
    Lemma 1.1.  Side length of a regular µ-gon inscribed in circle of radius ρ.
      s = 2ρ sin(π/µ)
    """
    return 2 * rho * math.sin(PI / mu)


def inscribed_polygon_apothem(rho: float, mu: int) -> float:
    """
    Lemma 1.1.  Apothem (inradius) of regular µ-gon inscribed in circle ρ.
      a = ρ cos(π/µ)
    """
    return rho * math.cos(PI / mu)


def inscribed_polygon_perimeter(rho: float, mu: int) -> float:
    """Lemma 1.1.  p_µ = µ · s_µ = 2µρ sin(π/µ)."""
    return mu * inscribed_polygon_side(rho, mu)


def inscribed_polygon_area(rho: float, mu: int) -> float:
    """
    Lemma 1.5.  Area of regular µ-gon inscribed in circle of radius ρ.
      E_µ = (1/2) µ ρ² sin(2π/µ)
    """
    return 0.5 * mu * rho**2 * math.sin(2 * PI / mu)


# ------ Lemma 1.4 – perimeter-to-diameter ratio for regular polygons --------

def perimeter_diameter_ratio(mu: int) -> float:
    """
    Lemma 1.4.  For a regular µ-gon inscribed in a circle of radius ρ,
      p_µ / (2ρ) = µ sin(π/µ).
    As µ → ∞ this converges to π (Theorem 1.1).
    """
    return mu * math.sin(PI / mu)


# ------ Theorem 1.1 – π is the universal ratio of circumference to diameter --

def theorem1_1_pi_as_limit(n_sides: int = 1_000_000) -> float:
    """
    Theorem 1.1.  For every circle the ratio circumference / diameter = π.
    Demonstrates via Axiom 1.1 that p_µ / (2ρ) → π as µ → ∞.
    """
    return perimeter_diameter_ratio(n_sides)


# ------ Corollary 1.1 – circumference formula --------------------------------

def circle_circumference(rho: float) -> float:
    """Corollary 1.1.  C = 2πρ."""
    return 2 * PI * rho


# ------ Theorem 1.2 – area of a circle ---------------------------------------

def circle_area(rho: float) -> float:
    """Theorem 1.2.  Area of circle of radius ρ is πρ²."""
    return PI * rho**2


# ------ Arc length & sectors (§1.4, §1.6) ------------------------------------

def arc_length(rho: float, theta_rad: float) -> float:
    """Arc length for central angle θ (radians):  L = ρθ."""
    return rho * abs(theta_rad)


def sector_area(rho: float, theta_rad: float) -> float:
    """Area of circular sector:  E = ½ρ²θ."""
    return 0.5 * rho**2 * abs(theta_rad)


def degrees_to_radians(deg: float) -> float:
    return deg * PI / 180.0


def radians_to_degrees(rad: float) -> float:
    return rad * 180.0 / PI


# ------ Theorem 1.3 – isoperimetric inequality for convex polygons -----------

def theorem1_3_isoperimetric(L: float, E: float) -> dict:
    """
    Theorem 1.3.  For every convex polygon with perimeter L and area E:
        4π E ≤ L²
    Equality holds iff the polygon is a circle.
    Returns the ratio 4πE/L² (≤ 1 always; =1 for a circle).
    """
    if L <= 0:
        raise ValueError("Perimeter must be positive.")
    ratio = 4 * PI * E / L**2
    return {
        "4pi*E": 4 * PI * E,
        "L^2": L**2,
        "ratio_4piE_over_L2": ratio,
        "inequality_satisfied": ratio <= 1.0 + 1e-9,
        "is_circle": abs(ratio - 1.0) < 1e-9,
    }


# ------ Theorem 1.4 – regular polygon optimality ----------------------------

def theorem1_4_regular_polygon_area(L: float, nu: int) -> float:
    """
    Theorem 1.4.  Among all convex polygons with ν sides and fixed perimeter L,
    the regular ν-gon has maximum area:
        E_max = L² / (4ν tan(π/ν))
    """
    return L**2 / (4 * nu * math.tan(PI / nu))


# ---------------------------------------------------------------------------
# 3.  Chapter 2 – Plane Transformations
# ---------------------------------------------------------------------------

class PlaneTransformation:
    """Abstract base for all plane transformations (§2.1)."""

    def apply(self, p: Point2D) -> Point2D:
        raise NotImplementedError

    def compose(self, other: "PlaneTransformation") -> "ComposedTransformation":
        """
        Composition g ◦ f: apply self first, then other.
        Associativity: h ◦ (g ◦ f) = (h ◦ g) ◦ f (§2.1).
        """
        return ComposedTransformation(self, other)

    def inverse(self) -> "PlaneTransformation":
        raise NotImplementedError


class ComposedTransformation(PlaneTransformation):
    """g ◦ f: apply f first, then g."""

    def __init__(self, f: PlaneTransformation, g: PlaneTransformation):
        self.f = f
        self.g = g

    def apply(self, p: Point2D) -> Point2D:
        return self.g.apply(self.f.apply(p))

    def inverse(self) -> "ComposedTransformation":
        return ComposedTransformation(self.g.inverse(), self.f.inverse())


class IdentityTransformation(PlaneTransformation):
    """Identity e: e(X) = X. The neutral element of composition (§2.1)."""

    def apply(self, p: Point2D) -> Point2D:
        return p

    def inverse(self) -> "IdentityTransformation":
        return IdentityTransformation()


# ------ Reflections (§2.2, Theorems 2.4, 2.5) --------------------------------

class Reflection(PlaneTransformation):
    """
    Reflection across line ax + by = c  (Theorem 2.4).
    f ◦ f = e  (Proposition 2.2): reflections are involutions.
    """

    def __init__(self, a: float, b: float, c: float):
        """Line: ax + by = c.  Normalise internally."""
        norm = math.hypot(a, b)
        self.a = a / norm
        self.b = b / norm
        self.c = c / norm

    @classmethod
    def from_two_points(cls, p1: Point2D, p2: Point2D) -> "Reflection":
        """Reflection across the line through p1 and p2."""
        dx, dy = p2.x - p1.x, p2.y - p1.y
        # Line: dy·x - dx·y = dy·p1.x - dx·p1.y
        return cls(dy, -dx, dy * p1.x - dx * p1.y)

    @classmethod
    def from_point_and_angle(cls, p: Point2D, angle_rad: float) -> "Reflection":
        """Reflection across line through p with direction angle_rad."""
        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)
        return cls.from_two_points(p, Point2D(p.x + dx, p.y + dy))

    def apply(self, p: Point2D) -> Point2D:
        d = self.a * p.x + self.b * p.y - self.c
        return Point2D(p.x - 2 * d * self.a, p.y - 2 * d * self.b)

    def inverse(self) -> "Reflection":
        return self  # f ◦ f = e


class PointSymmetry(PlaneTransformation):
    """
    Point symmetry (central symmetry) relative to O (§2.2).
    Theorem 2.6: composition of two orthogonal reflections = point symmetry.
    f ◦ f = e  (Proposition 2.2).
    """

    def __init__(self, center: Point2D):
        self.O = center

    def apply(self, p: Point2D) -> Point2D:
        return Point2D(2 * self.O.x - p.x, 2 * self.O.y - p.y)

    def inverse(self) -> "PointSymmetry":
        return self


# ------ Translations (§2.3, Theorems 2.8, 2.9, 2.10) -------------------------

class Translation(PlaneTransformation):
    """
    Translation by vector (dx, dy) – Theorem 2.8: every translation is an isometry.
    Theorem 2.9: composition of two translations is a translation.
    """

    def __init__(self, dx: float, dy: float):
        self.dx = dx
        self.dy = dy

    @classmethod
    def from_segment(cls, A: Point2D, B: Point2D) -> "Translation":
        """Translation along oriented segment AB."""
        return cls(B.x - A.x, B.y - A.y)

    def apply(self, p: Point2D) -> Point2D:
        return Point2D(p.x + self.dx, p.y + self.dy)

    def inverse(self) -> "Translation":
        return Translation(-self.dx, -self.dy)

    def compose_with_translation(self, other: "Translation") -> "Translation":
        """Theorem 2.9: sum of translation vectors."""
        return Translation(self.dx + other.dx, self.dy + other.dy)


# ------ Rotations (§2.4, Theorem 2.14, Proposition 2.6) ---------------------

class Rotation(PlaneTransformation):
    """
    Rotation about center O by angle φ (radians) – Theorem 2.14.
    Proposition 2.6: composition of two reflections = rotation by 2ω.
    """

    def __init__(self, center: Point2D, angle_rad: float):
        self.O = center
        self.phi = angle_rad

    def apply(self, p: Point2D) -> Point2D:
        cos_a = math.cos(self.phi)
        sin_a = math.sin(self.phi)
        dx = p.x - self.O.x
        dy = p.y - self.O.y
        return Point2D(
            self.O.x + dx * cos_a - dy * sin_a,
            self.O.y + dx * sin_a + dy * cos_a,
        )

    def inverse(self) -> "Rotation":
        return Rotation(self.O, -self.phi)

    def compose_rotations(self, other: "Rotation") -> PlaneTransformation:
        """
        Proposition 2.7.  Composition of two rotations with different centres.
        If φ + ψ ≠ 2kπ → rotation; otherwise → translation.
        """
        total_angle = self.phi + other.phi
        # Check if result is a translation
        if abs(total_angle % (2 * PI)) < 1e-10:
            # Theorem 2.10-style: result is a translation
            p_test = Point2D(0.0, 0.0)
            q = self.apply(p_test)
            r = other.apply(q)
            return Translation(r.x - p_test.x, r.y - p_test.y)
        # Otherwise find center of composite rotation numerically
        p_test = Point2D(0.0, 0.0)
        q = self.apply(p_test)
        r = other.apply(q)
        p_test2 = Point2D(1.0, 0.0)
        q2 = self.apply(p_test2)
        r2 = other.apply(q2)
        # Find fixed point of composition numerically via Newton iteration
        composed = ComposedTransformation(self, other)
        center = _find_fixed_point_2d(composed)
        return Rotation(center, total_angle)


def _find_fixed_point_2d(
    t: PlaneTransformation,
    x0: float = 0.0,
    y0: float = 0.0,
    iters: int = 200,
) -> Point2D:
    """Numerically locate fixed point of a 2-D transformation."""
    p = Point2D(x0, y0)
    for _ in range(iters):
        q = t.apply(p)
        p = Point2D((p.x + q.x) / 2, (p.y + q.y) / 2)
    return p


# ------ Theorem 2.16 – classification of plane isometries --------------------

def classify_isometry(t: PlaneTransformation) -> str:
    """
    Theorem 2.16.  Every plane isometry is one of:
    reflection | translation | rotation | glide reflection.
    Heuristic classification via effect on three reference points.
    """
    O  = Point2D(0, 0)
    e1 = Point2D(1, 0)
    e2 = Point2D(0, 1)
    O2  = t.apply(O)
    e12 = t.apply(e1)
    e22 = t.apply(e2)

    # Orientation: det of the Jacobian
    dx1, dy1 = e12.x - O2.x, e12.y - O2.y
    dx2, dy2 = e22.x - O2.x, e22.y - O2.y
    det = dx1 * dy2 - dy1 * dx2

    # Check if identity
    if O2.distance_to(O) < 1e-9 and e12.distance_to(e1) < 1e-9:
        return "identity"

    if det > 0:  # orientation preserving
        # Is translation?
        shift = O2 - O
        if abs((e12 - e1).x - shift.x) < 1e-9 and abs((e12 - e1).y - shift.y) < 1e-9:
            return "translation"
        return "rotation"
    else:  # orientation reversing
        # Fixed points?
        # Try to find fixed point
        p_test = Point2D(0, 0)
        p_img = t.apply(p_test)
        if p_test.distance_to(p_img) < 1e-9:
            return "reflection"
        # Check along midpoint iteration
        fp = _find_fixed_point_2d(t)
        if t.apply(fp).distance_to(fp) < 1e-6:
            return "reflection"
        return "glide_reflection"


# ------ Homotheties (§2.6, Theorems 2.17–2.19) --------------------------------

class Homothety(PlaneTransformation):
    """
    Homothety (dilatation) with center O and ratio κ (Theorem 2.17–2.19).
    Maps every line ε to a parallel line ε′.
    Preserves angles; multiplies distances by |κ|.
    """

    def __init__(self, center: Point2D, ratio: float):
        self.O = center
        self.kappa = ratio

    def apply(self, p: Point2D) -> Point2D:
        return Point2D(
            self.O.x + self.kappa * (p.x - self.O.x),
            self.O.y + self.kappa * (p.y - self.O.y),
        )

    def inverse(self) -> "Homothety":
        """Corollary 2.7: inverse has ratio 1/κ."""
        return Homothety(self.O, 1.0 / self.kappa)

    def compose_homotheties(self, other: "Homothety") -> PlaneTransformation:
        """
        Proposition 2.11 / Theorem 2.19.
        Same center → ratio κ·λ.
        Different centers and κ·λ ≠ 1 → homothety with ratio κ·λ on line OO′.
        κ·λ = 1 → translation.
        """
        combined_ratio = self.kappa * other.kappa
        if abs(combined_ratio - 1.0) < 1e-12:
            # Translation
            p0 = Point2D(0, 0)
            q0 = self.apply(p0)
            r0 = other.apply(q0)
            return Translation(r0.x, r0.y)
        # Find center numerically
        composed = ComposedTransformation(self, other)
        center = _find_fixed_point_2d(composed)
        return Homothety(center, combined_ratio)


# ------ Similarities (§2.7) ---------------------------------------------------

class Similarity(PlaneTransformation):
    """
    General direct similarity: composition of a homothety and a rotation.
    Maps circles to circles, preserves angles, multiplies distances by ratio k.
    Implemented via complex multiplication: f(z) = a·z + b  (a, b ∈ ℂ).
    """

    def __init__(self, a: complex, b: complex):
        """f(z) = a·z + b.  |a| = similarity ratio."""
        self.a = a
        self.b = b

    @classmethod
    def from_ratio_and_rotation(
        cls, center: Point2D, ratio: float, angle_rad: float
    ) -> "Similarity":
        O = complex(center.x, center.y)
        a = ratio * cmath.exp(1j * angle_rad)
        b = O - a * O
        return cls(a, b)

    @property
    def ratio(self) -> float:
        return abs(self.a)

    def apply(self, p: Point2D) -> Point2D:
        z = complex(p.x, p.y)
        w = self.a * z + self.b
        return Point2D(w.real, w.imag)

    def inverse(self) -> "Similarity":
        return Similarity(1 / self.a, -self.b / self.a)

    def compose(self, other: "Similarity") -> "Similarity":
        return Similarity(other.a * self.a, other.a * self.b + other.b)


# ------ Inversions (§2.8) -----------------------------------------------------

class Inversion(PlaneTransformation):
    """
    Inversion with center O and power k²:
        f(X) = X′  such that  OX · OX′ = k²  and X′ on ray OX.
    In complex notation: f(z) = k² / conj(z - O) + O.
    Maps circles/lines to circles/lines.
    """

    def __init__(self, center: Point2D, power: float):
        self.O = center
        self.k2 = power  # k² > 0

    def apply(self, p: Point2D) -> Point2D:
        dx = p.x - self.O.x
        dy = p.y - self.O.y
        r2 = dx**2 + dy**2
        if r2 < 1e-20:
            raise ValueError("Cannot invert the center of inversion.")
        scale = self.k2 / r2
        return Point2D(self.O.x + scale * dx, self.O.y + scale * dy)

    def inverse(self) -> "Inversion":
        return self  # Inversion is its own inverse


# ================================================================
# 4.  Chapter 3 – Axioms for Space & Basic 3-D Geometry
# ================================================================
# Axiom 
#   S1. Any two distinct points determine a unique line.
#   S2. Any three non-collinear points determine a unique plane.
#   S3. A line with two points in a plane lies entirely in the plane.
#   S4. Two distinct planes meet in a line or are disjoint (parallel).
# These are asserted as structural axioms; the engine enforces them via
# the class interfaces below.

@dataclass
class Line3D:
    """Parametric line: P(t) = point + t·direction."""
    point: Point3D
    direction: Point3D

    def point_at(self, t: float) -> Point3D:
        return self.point + self.direction * t

    def contains(self, p: Point3D, tol: float = 1e-9) -> bool:
        """S1/S3: check if p lies on the line."""
        cross = (p - self.point).cross(self.direction)
        return cross.norm() < tol

    @classmethod
    def from_two_points(cls, A: Point3D, B: Point3D) -> "Line3D":
        """S1: unique line through two distinct points."""
        d = B - A
        if d.norm() < 1e-12:
            raise ValueError("Points must be distinct (Axiom S1).")
        return cls(A, d)


@dataclass
class Plane3D:
    """Plane: n · (P - point) = 0,  where n is the normal vector."""
    point: Point3D
    normal: Point3D

    def contains(self, p: Point3D, tol: float = 1e-9) -> bool:
        return abs(self.normal.dot(p - self.point)) < tol

    def distance_to_point(self, p: Point3D) -> float:
        return abs(self.normal.dot(p - self.point)) / self.normal.norm()

    def is_parallel_to(self, other: "Plane3D", tol: float = 1e-9) -> bool:
        """S4: two planes are parallel if their normals are proportional."""
        cross = self.normal.cross(other.normal)
        return cross.norm() < tol

    def intersection_with_plane(self, other: "Plane3D") -> Optional[Line3D]:
        """S4: two non-parallel planes intersect in a line."""
        d = self.normal.cross(other.normal)
        if d.norm() < 1e-10:
            return None  # parallel or identical
        # Find a point on the intersection line
        A = self.normal
        B = other.normal
        n1n1 = A.dot(A)
        n2n2 = B.dot(B)
        n1n2 = A.dot(B)
        det = n1n1 * n2n2 - n1n2**2
        d1 = A.dot(self.point)
        d2 = B.dot(other.point)
        c1 = (d1 * n2n2 - d2 * n1n2) / det
        c2 = (d2 * n1n1 - d1 * n1n2) / det
        pt = Point3D(c1*A.x + c2*B.x, c1*A.y + c2*B.y, c1*A.z + c2*B.z)
        return Line3D(pt, d)

    @classmethod
    def from_three_points(cls, A: Point3D, B: Point3D, C: Point3D) -> "Plane3D":
        """S2: unique plane through three non-collinear points."""
        AB = B - A
        AC = C - A
        n = AB.cross(AC)
        if n.norm() < 1e-12:
            raise ValueError("Points must be non-collinear (Axiom S2).")
        return cls(A, n)


def angle_between_lines_3d(l1: Line3D, l2: Line3D) -> float:
    """Angle (radians) between two lines in space (§3.3)."""
    d1 = l1.direction
    d2 = l2.direction
    cos_a = abs(d1.dot(d2)) / (d1.norm() * d2.norm())
    return math.acos(min(cos_a, 1.0))


def angle_between_line_and_plane(line: Line3D, plane: Plane3D) -> float:
    """Angle (radians) between a line and a plane (§3.6)."""
    cos_angle = abs(line.direction.dot(plane.normal)) / (
        line.direction.norm() * plane.normal.norm()
    )
    return math.asin(min(cos_angle, 1.0))


def distance_between_skew_lines(l1: Line3D, l2: Line3D) -> float:
    """Distance between skew lines (§3.4)."""
    w = l1.point - l2.point
    d1 = l1.direction
    d2 = l2.direction
    cross = d1.cross(d2)
    denom = cross.norm()
    if denom < 1e-12:
        # Lines are parallel; fall back to point-to-line distance
        return w.cross(d1).norm() / d1.norm()
    return abs(w.dot(cross)) / denom


# ================================================================
# 5.  Chapter 4 & 5 – Solids: Areas and Volumes
## ================================================================

class Sphere:
    """
    Sphere of radius r.
    Area = 4πr²  (§5.2, Archimedes).
    Volume = (4/3)πr³  (§5.10).
    """

    def __init__(self, radius: float):
        self.r = radius

    def surface_area(self) -> float:
        return 4 * PI * self.r**2

    def volume(self) -> float:
        return (4 / 3) * PI * self.r**3

    def great_circle_circumference(self) -> float:
        return circle_circumference(self.r)


class Cylinder:
    """
    Right circular cylinder: radius r, height h.
    Lateral area = 2πrh; Total area = 2πr(r + h);  Volume = πr²h  (§4.8, §5.8).
    """

    def __init__(self, radius: float, height: float):
        self.r = radius
        self.h = height

    def lateral_area(self) -> float:
        return 2 * PI * self.r * self.h

    def total_area(self) -> float:
        return 2 * PI * self.r * (self.r + self.h)

    def volume(self) -> float:
        return PI * self.r**2 * self.h


class Cone:
    """
    Right circular cone: base radius r, height h.
    Slant height l = √(r² + h²).
    Lateral area = πrl; Total area = πr(r + l); Volume = (1/3)πr²h  (§4.9, §5.9).
    """

    def __init__(self, radius: float, height: float):
        self.r = radius
        self.h = height

    @property
    def slant_height(self) -> float:
        return math.hypot(self.r, self.h)

    def lateral_area(self) -> float:
        return PI * self.r * self.slant_height

    def total_area(self) -> float:
        return PI * self.r * (self.r + self.slant_height)

    def volume(self) -> float:
        return (1 / 3) * PI * self.r**2 * self.h

    def unfolding_sector_angle(self) -> float:
        """Central angle (radians) of the unfolded lateral surface (§4.10)."""
        return 2 * PI * self.r / self.slant_height


class Pyramid:
    """
    Regular pyramid: regular n-gon base with side a, height h.
    Base area, lateral area, volume (§4.3, §4.5, §5.7).
    """

    def __init__(self, n_sides: int, side: float, height: float):
        self.n = n_sides
        self.a = side
        self.h = height

    def base_area(self) -> float:
        """Area of regular n-gon base: E = (n·a²) / (4 tan(π/n))."""
        return (self.n * self.a**2) / (4 * math.tan(PI / self.n))

    def apothem(self) -> float:
        """Apothem of base polygon: a / (2 tan(π/n))."""
        return self.a / (2 * math.tan(PI / self.n))

    def slant_height(self) -> float:
        return math.hypot(self.apothem(), self.h)

    def lateral_area(self) -> float:
        """(1/2) · perimeter · slant height."""
        return 0.5 * self.n * self.a * self.slant_height()

    def total_area(self) -> float:
        return self.base_area() + self.lateral_area()

    def volume(self) -> float:
        """V = (1/3) · base_area · height  (§5.7)."""
        return (1 / 3) * self.base_area() * self.h


class Prism:
    """
    Right prism with regular n-gon base: side a, height h.
    Volume = base_area · h  (§5.6).
    """

    def __init__(self, n_sides: int, side: float, height: float):
        self.n = n_sides
        self.a = side
        self.h = height

    def base_area(self) -> float:
        return (self.n * self.a**2) / (4 * math.tan(PI / self.n))

    def lateral_area(self) -> float:
        return self.n * self.a * self.h

    def total_area(self) -> float:
        return 2 * self.base_area() + self.lateral_area()

    def volume(self) -> float:
        return self.base_area() * self.h


def euler_characteristic(V: int, E: int, F: int) -> int:
    """
    Euler characteristic χ = V - E + F  (§5.4).
    For any convex polyhedron: χ = 2  (Euler's theorem).
    """
    return V - E + F


def platonic_solids() -> dict:
    """
    §4.6 – Platonic solids: {name: (V, E, F, face_polygon)}.
    Euler characteristic = 2 for all.
    """
    return {
        "tetrahedron":    {"V": 4,  "E": 6,  "F": 4,  "face": 3},
        "cube":           {"V": 8,  "E": 12, "F": 6,  "face": 4},
        "octahedron":     {"V": 6,  "E": 12, "F": 8,  "face": 3},
        "dodecahedron":   {"V": 20, "E": 30, "F": 12, "face": 5},
        "icosahedron":    {"V": 12, "E": 30, "F": 20, "face": 3},
    }


# ================================================================
# 6.  Chapter 6 – Conic Sections
# ================================================================

class Parabola:
    """
    Standard parabola y² = 4ax  (§6.5).
    Focus F = (a, 0); Directrix x = -a.
    Eccentricity e = 1.
    """

    def __init__(self, a: float):
        self.a = a  # focal parameter

    @property
    def focus(self) -> Tuple[float, float]:
        return (self.a, 0.0)

    @property
    def directrix_x(self) -> float:
        return -self.a

    def point_at_t(self, t: float) -> Tuple[float, float]:
        """Parametric form: x = at², y = 2at."""
        return (self.a * t**2, 2 * self.a * t)

    def focal_distance(self, x: float) -> float:
        """Distance from point (x, y) on parabola to focus: x + a."""
        return x + self.a

    def eccentricity(self) -> float:
        return 1.0

    def tangent_slope_at_t(self, t: float) -> float:
        """Slope of tangent: dy/dx = 1/t  (t ≠ 0)."""
        if abs(t) < 1e-12:
            return float("inf")
        return 1.0 / t


class Ellipse:
    """
    Ellipse x²/a² + y²/b² = 1,  a > b > 0  (§6.6).
    c² = a² - b²;  Foci at (±c, 0);  Eccentricity e = c/a < 1.
    """

    def __init__(self, a: float, b: float):
        if a <= b:
            raise ValueError("For standard ellipse, a > b > 0.")
        self.a = a
        self.b = b

    @property
    def c(self) -> float:
        return math.sqrt(self.a**2 - self.b**2)

    @property
    def eccentricity(self) -> float:
        return self.c / self.a

    @property
    def foci(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return ((-self.c, 0.0), (self.c, 0.0))

    @property
    def semi_latus_rectum(self) -> float:
        return self.b**2 / self.a

    def area(self) -> float:
        return PI * self.a * self.b

    def perimeter_approx(self) -> float:
        """Ramanujan's approximation: π[3(a+b) - √((3a+b)(a+3b))]."""
        a, b = self.a, self.b
        return PI * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))

    def point_at_t(self, t: float) -> Tuple[float, float]:
        """Parametric: (a cos t, b sin t)."""
        return (self.a * math.cos(t), self.b * math.sin(t))

    def focal_radii(self, x: float, y: float) -> Tuple[float, float]:
        """
        Distances from point (x, y) on ellipse to the two foci.
        r1 + r2 = 2a  (defining property of ellipse, §6.6).
        """
        F1 = (-self.c, 0.0)
        F2 = (self.c, 0.0)
        r1 = math.hypot(x - F1[0], y - F1[1])
        r2 = math.hypot(x - F2[0], y - F2[1])
        return r1, r2

    def directrices_x(self) -> Tuple[float, float]:
        """x = ±a/e (§6.3)."""
        return (-self.a / self.eccentricity, self.a / self.eccentricity)


class Hyperbola:
    """
    Hyperbola x²/a² - y²/b² = 1  (§6.7).
    c² = a² + b²;  Foci at (±c, 0);  Eccentricity e = c/a > 1.
    Asymptotes: y = ±(b/a)x.
    """

    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b

    @property
    def c(self) -> float:
        return math.sqrt(self.a**2 + self.b**2)

    @property
    def eccentricity(self) -> float:
        return self.c / self.a

    @property
    def foci(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return ((-self.c, 0.0), (self.c, 0.0))

    @property
    def asymptote_slopes(self) -> Tuple[float, float]:
        return (self.b / self.a, -self.b / self.a)

    def focal_radii(self, x: float, y: float) -> Tuple[float, float]:
        """
        |r1 - r2| = 2a  (defining property of hyperbola, §6.7).
        """
        F1 = (-self.c, 0.0)
        F2 = (self.c, 0.0)
        r1 = math.hypot(x - F1[0], y - F1[1])
        r2 = math.hypot(x - F2[0], y - F2[1])
        return r1, r2

    def point_on_hyperbola(self, t: float) -> Tuple[float, float]:
        """Parametric (right branch): (a cosh t, b sinh t)."""
        return (self.a * math.cosh(t), self.b * math.sinh(t))

    def directrices_x(self) -> Tuple[float, float]:
        return (-self.a / self.eccentricity, self.a / self.eccentricity)


def conic_from_focus_directrix(
    focus: Tuple[float, float],
    directrix_x: float,
    eccentricity: float,
) -> Union[Parabola, Ellipse, Hyperbola]:
    """
    §6.3 – Unified focus-directrix definition of conics.
    e = 1  → parabola;  e < 1 → ellipse;  e > 1 → hyperbola.
    """
    if abs(eccentricity - 1.0) < 1e-9:
        # Parabola: a = distance from focus to directrix / 2
        a = abs(focus[0] - directrix_x) / 2
        return Parabola(a)
    # For ellipse/hyperbola, reconstruct a and b from focus and directrix
    # Using: directrix at x = a/e → a = e * |directrix_x|
    # and focus at (±c, 0) with c = a·e
    a = eccentricity * abs(directrix_x)
    c = eccentricity * a
    b2 = abs(a**2 - c**2)
    b = math.sqrt(b2)
    if eccentricity < 1:
        return Ellipse(a, b)
    else:
        return Hyperbola(a, b)


# ================================================================
# 7.  Chapter 7 – Transformations in Space
# ================================================================

class Reflection3D:
    """
    Reflection across a plane (§7.2).
    f ◦ f = identity.
    """

    def __init__(self, plane: Plane3D):
        self.plane = plane

    def apply(self, p: Point3D) -> Point3D:
        n = self.plane.normal
        d = n.dot(p - self.plane.point) / n.dot(n)
        return p - n * (2 * d)

    def inverse(self) -> "Reflection3D":
        return self


class Translation3D:
    """Translation in space by vector v (§7.3)."""

    def __init__(self, v: Point3D):
        self.v = v

    def apply(self, p: Point3D) -> Point3D:
        return p + self.v

    def inverse(self) -> "Translation3D":
        return Translation3D(Point3D(-self.v.x, -self.v.y, -self.v.z))


class Rotation3D:
    """
    Rotation in space about axis through origin with direction u by angle φ (§7.4).
    Uses Rodrigues' rotation formula.
    """

    def __init__(self, axis: Point3D, angle_rad: float):
        n = axis.norm()
        self.u = Point3D(axis.x / n, axis.y / n, axis.z / n)
        self.phi = angle_rad

    def apply(self, p: Point3D) -> Point3D:
        u = self.u
        cos_a = math.cos(self.phi)
        sin_a = math.sin(self.phi)
        dot = u.dot(p)
        cross = u.cross(p)
        return Point3D(
            p.x * cos_a + cross.x * sin_a + u.x * dot * (1 - cos_a),
            p.y * cos_a + cross.y * sin_a + u.y * dot * (1 - cos_a),
            p.z * cos_a + cross.z * sin_a + u.z * dot * (1 - cos_a),
        )

    def inverse(self) -> "Rotation3D":
        return Rotation3D(self.u, -self.phi)


class Homothety3D:
    """Homothety (dilatation) in space: center O, ratio κ (§7.6)."""

    def __init__(self, center: Point3D, ratio: float):
        self.O = center
        self.kappa = ratio

    def apply(self, p: Point3D) -> Point3D:
        return self.O + (p - self.O) * self.kappa

    def inverse(self) -> "Homothety3D":
        return Homothety3D(self.O, 1.0 / self.kappa)


# ================================================================
# 8.  Spherical geometry (§4.13, §4.14)
# ================================================================

def spherical_excess(alpha: float, beta: float, gamma: float) -> float:
    """
    Spherical excess E = α + β + γ − π  of a spherical triangle (§4.14).
    All angles in radians.  E > 0 always.
    """
    return alpha + beta + gamma - PI


def spherical_triangle_area(R: float, alpha: float, beta: float, gamma: float) -> float:
    """
    Area of spherical triangle on sphere of radius R:
        Area = R² · E  (Girard's theorem, §4.13).
    """
    return R**2 * spherical_excess(alpha, beta, gamma)


def spherical_lune_area(R: float, dihedral_angle: float) -> float:
    """
    Area of spherical lune (§4.13):  Area = 2R² · θ.
    """
    return 2 * R**2 * dihedral_angle


# ================================================================
# 9.  Utility – Theorem / Lemma verification helpers
# ================================================================

def verify_theorem1_1(rho: float = 5.0, n_sides: int = 100_000) -> dict:
    """
    Verify Theorem 1.1: circumference / diameter → π.
    """
    C = inscribed_polygon_perimeter(rho, n_sides)
    ratio = C / (2 * rho)
    return {
        "polygon_sides": n_sides,
        "circle_radius": rho,
        "inscribed_perimeter": C,
        "ratio_C_over_2rho": ratio,
        "pi": PI,
        "error": abs(ratio - PI),
    }


def verify_theorem1_2(rho: float = 3.0, n_sides: int = 100_000) -> dict:
    """
    Verify Theorem 1.2: inscribed polygon area → πρ².
    """
    E_polygon = inscribed_polygon_area(rho, n_sides)
    E_circle  = circle_area(rho)
    return {
        "polygon_sides": n_sides,
        "polygon_area": E_polygon,
        "circle_area": E_circle,
        "error": abs(E_polygon - E_circle),
    }


def verify_isoperimetric(L: float, E: float) -> dict:
    """Verify Theorem 1.3: 4πE ≤ L²."""
    return theorem1_3_isoperimetric(L, E)


def verify_euler_characteristic_platonic() -> dict:
    """Verify χ = 2 for all Platonic solids (§5.4)."""
    results = {}
    for name, data in platonic_solids().items():
        chi = euler_characteristic(data["V"], data["E"], data["F"])
        results[name] = {"chi": chi, "correct": chi == 2}
    return results
