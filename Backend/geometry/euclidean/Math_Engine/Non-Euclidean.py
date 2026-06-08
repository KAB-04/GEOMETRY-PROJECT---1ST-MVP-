"""
══════════════════════════════════════════════════════════════
        NON-EUCLIDEAN GEOMETRY ENGINE
        Based on H. S. M. Coxeter — Non-Euclidean Geometry
        Fifth Edition (University of Toronto Press)
══════════════════════════════════════════════════════════════

Contents:
   1  : GeometryType          (elliptic / hyperbolic selector & constants)
   2  : ProjectiveBase        (cross-ratio, harmonic sets, perspectivity)
   3  : AbsolutePolarity      (conjugacy, perpendicularity via polarity)
   4  : EllipticLine          (distance, angle, cross-ratio; §5.7)
   5  : HyperbolicLine        (distance via cross-ratio; §8.1, §10.31)
   6  : AngleOfParallelism    (Lobatschewsky's Π(c); §1.4)
   7  : EllipticTrigonometry  (sine / cosine rules, right triangles; §12.7)
   8  : HyperbolicTrigonometry(sinh / cosh rules, right triangles; §12.9)
   9  : EllipticTriangle      (angle-sum, defect/excess, area; §13.3)
   10 : HyperbolicTriangle    (angle-sum, defect, area; §13.4)
   11 : NonEuclideanCircle    (proper circle, horocycle, equidistant curve; §11.1)
   12 : EllipticTransform     (reflection, rotation, congruent map; §6.2–6.4)
   13 : HyperbolicTransform   (rotation, parallel displacement, translation,glide-reflection; §10.3)
   14 : PoincareModel         (Poincaré disc: distance, geodesic; §14.8)
   15 : KleinModel            (Klein disc: distance, perpendicularity; §8.1)
   16 : SphericalTrigonometry (spherical geometry = elliptic; §12.7 note)

Usage:
  python NonEuclidean.py              
  import NonEuclidean as ne           
"""

import math
import cmath


# ================================================================
# UTILITIES  (same conventions as Analytical.py)
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

def _clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))


# ================================================================
# CHAPTER 1 / SELECTOR — GEOMETRY TYPE
# ================================================================

class GeometryType:
    """
    Identifies and stores the geometry in use: 'elliptic' or 'hyperbolic'.

    In Klein's unified treatment (§1.7):
      • Elliptic  — absolute polarity is a UNIFORM (elliptic) polarity;
                    no real Absolute conic; every two lines meet.
      • Hyperbolic — absolute polarity determines a REAL conic (the
                    Absolute); lines inside the conic are ordinary lines.
      • k         — curvature radius (default 1).  Making k → ∞ gives
                    Euclidean geometry as a limiting case (§1.3, §12.7).
    """
    ELLIPTIC   = "elliptic"
    HYPERBOLIC = "hyperbolic"

    def __init__(self, kind="hyperbolic", k=1.0):
        if kind not in (self.ELLIPTIC, self.HYPERBOLIC):
            raise ValueError("kind must be 'elliptic' or 'hyperbolic'.")
        self.kind = kind
        self.k    = float(k)       # curvature radius

    def is_elliptic(self):
        return self.kind == self.ELLIPTIC

    def is_hyperbolic(self):
        return self.kind == self.HYPERBOLIC

    def info(self):
        return {
            "geometry"        : self.kind,
            "curvature_radius": self.k,
            "parallel_lines"  : "none (every two lines meet)" if self.is_elliptic()
                                 else "two parallels through any exterior point",
            "angle_sum_triangle": "> π" if self.is_elliptic() else "< π",
        }


# ================================================================
# CHAPTER 2 — REAL PROJECTIVE GEOMETRY: CROSS-RATIO & HARMONIC SETS
# ================================================================

class ProjectiveBase:
    """
    Fundamental projective tools used to define distances and angles
    in both non-Euclidean geometries (Chapters II–IV of Coxeter).

    Cross-ratio {AB, CD} = (AC/CB) / (AD/DB)   [§4.3]
    Harmonic relation H(AB, CD): {AB, CD} = −1  [§2.4]
    """

    @staticmethod
    def cross_ratio(A, B, C, D):
        """
        Cross-ratio {AB, CD} of four collinear points given as real numbers
        (or complex numbers for the projective line).
        {AB, CD} = (A−C)(B−D) / ((A−D)(B−C))
        """
        num = (A - C) * (B - D)
        den = (A - D) * (B - C)
        if abs(den) < 1e-15:
            return float('inf')
        return _fmt(num / den)

    @staticmethod
    def is_harmonic(A, B, C, D, tol=1e-9):
        """
        Check H(AB; CD): {AB, CD} = −1  (§2.4).
        C and D are harmonic conjugates with respect to A and B.
        """
        cr = ProjectiveBase.cross_ratio(A, B, C, D)
        return abs(cr + 1) < tol

    @staticmethod
    def harmonic_conjugate(A, B, C):
        """
        Given A, B, C on a projective line, find D such that H(AB; CD).
        Formula: D = (2AC − BC − AB·C/(A+B)) ... simplified:
        D = (A·B·(-2) + C·(A+B)) / (C - (A+B)/2) — standard formula:
        D such that {AB,CD} = -1:
        D = A + (A−B)*(A−C) / ((A−C) − (B−C))
        """
        num = A * B - C * (A + B - C)
        den = A + B - 2 * C
        if abs(den) < 1e-15:
            return float('inf')
        return _fmt(num / den)

    @staticmethod
    def perspectivity_check(range1, range2):
        """
        Check whether two ranges are in perspective (all cross-ratios equal).
        range1, range2 are lists of 4 collinear points each.
        Returns True if the ranges are projectively related.
        """
        cr1 = ProjectiveBase.cross_ratio(*range1)
        cr2 = ProjectiveBase.cross_ratio(*range2)
        return abs(cr1 - cr2) < 1e-9


# ================================================================
# CHAPTER 3 — ABSOLUTE POLARITY  (§3.2, §3.8, §5.1, §6.1, §8.1)
# ================================================================

class AbsolutePolarity:
    """
    The absolute polarity encodes the metric structure of the geometry.

    Elliptic  (§5.1):  uniform polarity — no real self-conjugate points.
    Hyperbolic (§8.1): the Absolute is a real conic x²+y²−z²=0  (unit circle
                       in the Klein/Poincaré models).

    In homogeneous coordinates (x0, x1, x2) the polarity is represented by
    the matrix C with C[μν] = c_μν.

    Default canonical forms:
      Elliptic  : C = diag(1, 1, 1)   → (xx) = x0²+x1²+x2² > 0  always
      Hyperbolic: C = diag(1, 1, −1)  → Absolute is x0²+x1²=x2²
    """

    def __init__(self, geometry="hyperbolic"):
        self.geometry = geometry
        if geometry == "elliptic":
            # Elliptic canonical form §5.1
            self.C = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        else:
            # Hyperbolic canonical form §8.1  (unit-circle Absolute)
            self.C = [[1, 0, 0], [0, 1, 0], [0, 0, -1]]

    def inner_product(self, x, y):
        """(xy) = Σ c_μν x_μ y_ν  (§12.1)."""
        total = 0.0
        for mu in range(3):
            for nu in range(3):
                total += self.C[mu][nu] * x[mu] * y[nu]
        return total

    def norm_sq(self, x):
        """(xx) = (x, x)."""
        return self.inner_product(x, x)

    def are_conjugate(self, x, y, tol=1e-9):
        """
        Two points (x) and (y) are conjugate in the polarity iff (xy)=0. (§3.2)
        For the absolute polarity, conjugate = perpendicular.
        """
        return abs(self.inner_product(x, y)) < tol

    def are_perpendicular(self, x, y, tol=1e-9):
        """
        Points (or lines) are perpendicular iff they are conjugate in the
        absolute polarity (§6.2, §10.1).
        """
        return self.are_conjugate(x, y, tol)

    def polar_of_point(self, x):
        """
        The absolute polar of point (x) is the line [X] with
        X_ν = Σ c_μν x_μ.  (§3.2, §12.11)
        """
        X = [0.0, 0.0, 0.0]
        for nu in range(3):
            for mu in range(3):
                X[nu] += self.C[mu][nu] * x[mu]
        return tuple(_fmt(v) for v in X)

    def is_on_absolute(self, x, tol=1e-9):
        """
        Point (x) lies on the Absolute conic iff (xx) = 0.
        In hyperbolic geometry these are the 'points at infinity' (§8.1).
        """
        return abs(self.norm_sq(x)) < tol

    def is_ordinary_point(self, x):
        """
        In hyperbolic geometry, an ordinary (interior) point satisfies (xx) > 0.
        In elliptic geometry, every point is ordinary.
        """
        val = self.norm_sq(x)
        if self.geometry == "elliptic":
            return val > 0
        else:
            return val > 0


# ================================================================
# CHAPTER 4 / 5  — DISTANCE ON A LINE  (§5.7, §8.1, §10.31)
# ================================================================

class EllipticLine:
    """
    Elliptic metric on a projective line.  Distance is defined via
    cross-ratio with the (imaginary) absolute points (§5.7).

    For two homogeneous points (x) and (y) on the elliptic line,
    the distance AB = arc cos [(xy) / √((xx)(yy))]   (§12.15)

    Angles between lines follow the dual formula with [X] and [Y].
    """

    @staticmethod
    def distance(x, y, polarity=None):
        """
        Elliptic distance between points x=(x0,x1,x2) and y=(y0,y1,y2).
        Uses §12.15 (canonical polarity C = I).
        For 2-D homogeneous points.
        """
        if polarity is None:
            polarity = AbsolutePolarity("elliptic")
        xy  = polarity.inner_product(x, y)
        xx  = polarity.norm_sq(x)
        yy  = polarity.norm_sq(y)
        val = _clamp(xy / math.sqrt(xx * yy))
        return _fmt(math.acos(val))

    @staticmethod
    def distance_deg(x, y, polarity=None):
        """Distance in degrees."""
        return _fmt(_deg(EllipticLine.distance(x, y, polarity)))

    @staticmethod
    def angle_between_lines(X, Y, polarity=None):
        """
        Angle between lines [X] and [Y] in the elliptic plane.
        §12.13:  angle = arc cos [(XY)/√((XX)(YY))]  (using dual polarity).
        """
        if polarity is None:
            polarity = AbsolutePolarity("elliptic")
        XY  = polarity.inner_product(X, Y)
        XX  = polarity.norm_sq(X)
        YY  = polarity.norm_sq(Y)
        val = _clamp(XY / math.sqrt(abs(XX * YY)))
        return _fmt(math.acos(val))

    @staticmethod
    def distance_cross_ratio(A, B, M, N):
        """
        Distance via cross-ratio (§5.7):  AB = ½|log{AB,MN}|  (elliptic uses
        imaginary absolute points, so in practice use the arc cos formula).
        For the real line with specified 'circular points' M, N:
        AB = ½ |log {AB, MN}|.
        """
        cr = ProjectiveBase.cross_ratio(A, B, M, N)
        if cr <= 0:
            return float('inf')
        return _fmt(0.5 * abs(math.log(cr)))


class HyperbolicLine:
    """
    Hyperbolic (Lobatschewsky) metric on a projective line.  §8.1, §10.31.

    The Absolute on the line consists of two real points M, N.
    Distance: AB = ½ |log {AB, MN}|  (choosing the factor ½ so the unit
    agrees with Lobatschewsky's; §10.31).

    For homogeneous points (x), (y) with the canonical polarity
    C = diag(1,1,−1):
    cosh(AB) = |(xy)| / √((xx)(yy))   (§12.15)
    """

    @staticmethod
    def distance(x, y, polarity=None):
        """
        Hyperbolic distance between ordinary points x=(x0,x1,x2) and
        y=(y0,y1,y2) (homogeneous, with x2 > 0 by convention).
        §12.15: d = arg cosh [(xy)/√((xx)(yy))].
        """
        if polarity is None:
            polarity = AbsolutePolarity("hyperbolic")
        xy  = abs(polarity.inner_product(x, y))
        xx  = polarity.norm_sq(x)
        yy  = polarity.norm_sq(y)
        if xx <= 0 or yy <= 0:
            raise ValueError("Both points must be ordinary (inside the Absolute).")
        val = _clamp(xy / math.sqrt(xx * yy), lo=1.0, hi=float('inf'))
        return _fmt(math.acosh(max(1.0, val)))

    @staticmethod
    def angle_between_lines(X, Y, polarity=None):
        """
        Angle between two ordinary lines [X] and [Y] in hyperbolic geometry.
        §12.13: angle = arc cos (−|[XY]| / √([XX][YY]))
        (sign convention: [XX] < 0 for ordinary lines).
        """
        if polarity is None:
            polarity = AbsolutePolarity("hyperbolic")
        XY  = polarity.inner_product(X, Y)
        XX  = polarity.norm_sq(X)
        YY  = polarity.norm_sq(Y)
        val = _clamp(abs(XY) / math.sqrt(abs(XX * YY)))
        return _fmt(math.acos(val))

    @staticmethod
    def distance_cross_ratio(A, B, M, N):
        """
        Hyperbolic distance via cross-ratio §10.31:
        AB = ½ |log {AB, MN}|,
        where M, N are the two (real) points where the line meets the Absolute.
        """
        cr = ProjectiveBase.cross_ratio(A, B, M, N)
        if cr <= 0:
            return float('inf')
        return _fmt(0.5 * abs(math.log(cr)))

    @staticmethod
    def ultra_parallel_distance(X, Y, polarity=None):
        """
        Distance between two ultra-parallel lines [X] and [Y].
        §12.16 / §10.72:  d = arg cosh [|[XY]| / √([XX][YY])].
        """
        if polarity is None:
            polarity = AbsolutePolarity("hyperbolic")
        XY = polarity.inner_product(X, Y)
        XX = polarity.norm_sq(X)
        YY = polarity.norm_sq(Y)
        val = _clamp(abs(XY) / math.sqrt(abs(XX * YY)), lo=1.0, hi=float('inf'))
        return _fmt(math.acosh(max(1.0, val)))


# ================================================================
# CHAPTER 5 — ANGLE OF PARALLELISM  (§1.4, §10.6)
# ================================================================

class AngleOfParallelism:
    """
    Lobatschewsky's angle of parallelism Π(c).

    If AB is perpendicular to a line q and c = |AB|, then the two
    parallels from A to q make an angle Π(c) with AB, where
    (using unit curvature radius k = 1):

        Π(c) = 2 arc tan(e^{−c})
             = arc cot(sinh c)
             = arc cos(tanh c)       §1.4

    Properties:
        Π(0) = π/2,  Π(∞) = 0,   and  sin Π(c) · cosh c = 1.
    """

    @staticmethod
    def angle(c, k=1.0):
        """
        Angle of parallelism Π(c) in radians for perpendicular distance c.
        k = curvature radius (default 1).
        """
        if c < 0:
            raise ValueError("Distance c must be non-negative.")
        c_scaled = c / k
        return _fmt(2 * math.atan(math.exp(-c_scaled)))

    @staticmethod
    def angle_deg(c, k=1.0):
        """Π(c) in degrees."""
        return _fmt(_deg(AngleOfParallelism.angle(c, k)))

    @staticmethod
    def from_angle(Pi_rad):
        """
        Given Π(c), recover the distance c.
        c = − ln(tan(Π/2)) = ln(cot(Π/2)).
        """
        t = math.tan(Pi_rad / 2)
        if t <= 0:
            raise ValueError("Π(c) must be in (0, π/2).")
        return _fmt(-math.log(t))

    @staticmethod
    def check_relation(c, k=1.0):
        """
        Verify sin Π(c) · cosh(c/k) = 1  (Lobatschewsky's identity §1.4).
        """
        Pi = AngleOfParallelism.angle(c, k)
        lhs = math.sin(Pi) * math.cosh(c / k)
        return {"Pi_rad": _fmt(Pi), "Pi_deg": _fmt(_deg(Pi)),
                "sin_Pi_cosh_c": _fmt(lhs),
                "identity_holds": abs(lhs - 1) < 1e-9}

    @staticmethod
    def equivalent_forms(c):
        """Return all three equivalent forms of Π(c)."""
        c = float(c)
        a1 = 2 * math.atan(math.exp(-c))
        a2 = math.atan(1.0 / math.sinh(c)) if c > 0 else math.pi / 2
        a3 = math.acos(math.tanh(c)) if c > 0 else math.pi / 2
        return {"2*arctan(e^-c)": _fmt(a1),
                "arccot(sinh c)" : _fmt(a2),
                "arccos(tanh c)" : _fmt(a3),
                "all_equal"      : abs(a1 - a2) < 1e-9 and abs(a2 - a3) < 1e-9}


# ================================================================
# CHAPTER 7 — ELLIPTIC TRIGONOMETRY  (§12.7)
# ================================================================

class EllipticTrigonometry:
    """
    Trigonometry of a triangle in the elliptic plane (k = 1).
    Formulae are identical to spherical trigonometry (§12.7 note).

    Triangle ABC with sides a, b, c opposite angles A, B, C.
    All sides and angles are measured in radians.

    Key formulae (§12.73 – 12.79):
      Sine rule:    sin a / sin A = sin b / sin B = sin c / sin C
      Cosine rule I (side→angle):  cos c = cos a cos b + sin a sin b cos C    [§12.74 rearranged]
      Cosine rule II (angle→side): cos C = −cos A cos B + sin A sin B cos c   [§12.75]
    """

    @staticmethod
    def _validate(sides_angles):
        for v in sides_angles:
            if not (0 < v < math.pi):
                raise ValueError(f"All sides and angles must be in (0, π); got {v}.")

    # ---- General triangle ----

    @staticmethod
    def cosine_rule_side(a, b, C):
        """
        §12.74: cos c = cos a cos b + sin a sin b cos C.
        Given two sides a, b and included angle C, find side c.
        """
        val = _clamp(math.cos(a)*math.cos(b) + math.sin(a)*math.sin(b)*math.cos(C))
        return _fmt(math.acos(val))

    @staticmethod
    def cosine_rule_angle(A, B, c):
        """
        §12.75: cos C = −cos A cos B + sin A sin B cos c.
        Given two angles A, B and included side c, find angle C.
        """
        val = _clamp(-math.cos(A)*math.cos(B) + math.sin(A)*math.sin(B)*math.cos(c))
        return _fmt(math.acos(val))

    @staticmethod
    def sine_rule(a, A, b=None, B=None, c=None, C=None):
        """
        §12.73: sin a / sin A = sin b / sin B = sin c / sin C.
        Provide any two pairs; returns the common ratio and any unknown.
        """
        ratio = math.sin(a) / math.sin(A)
        result = {"ratio": _fmt(ratio)}
        if b is not None and B is None:
            result["B"] = _fmt(math.asin(_clamp(math.sin(b) / ratio)))
        if B is not None and b is None:
            result["b"] = _fmt(math.asin(_clamp(ratio * math.sin(B))))
        return result

    @staticmethod
    def solve_triangle(a=None, b=None, c=None, A=None, B=None, C=None):
        """
        Solve a general elliptic triangle given any three independent parts.
        Uses §12.74 and §12.75 iteratively.
        Returns dict with all six parts (sides and angles).
        """
        known = {k: v for k, v in
                 [("a", a), ("b", b), ("c", c), ("A", A), ("B", B), ("C", C)]
                 if v is not None}
        T = dict(known)

        def _law_cos_side(s1, s2, ang):
            v = _clamp(math.cos(s1)*math.cos(s2) + math.sin(s1)*math.sin(s2)*math.cos(ang))
            return math.acos(v)

        def _law_cos_ang(a1, a2, s):
            v = _clamp(-math.cos(a1)*math.cos(a2) + math.sin(a1)*math.sin(a2)*math.cos(s))
            return math.acos(v)

        # Two sides + included angle  →  third side
        for s1, s2, ang, s3 in [("a","b","C","c"), ("a","c","B","b"), ("b","c","A","a")]:
            if s1 in T and s2 in T and ang in T and s3 not in T:
                T[s3] = _law_cos_side(T[s1], T[s2], T[ang])

        # Two angles + included side  →  third angle
        for a1, a2, s, a3 in [("A","B","c","C"), ("A","C","b","B"), ("B","C","a","A")]:
            if a1 in T and a2 in T and s in T and a3 not in T:
                T[a3] = _law_cos_ang(T[a1], T[a2], T[s])

        # Sine rule to fill in the rest
        # build list of known (side, angle) pairs
        pairs = [(T[s], T[a]) for s, a in [("a","A"),("b","B"),("c","C")]
                 if s in T and a in T]
        if pairs:
            ratio = math.sin(pairs[0][0]) / math.sin(pairs[0][1])
            for s, a in [("a","A"),("b","B"),("c","C")]:
                if s in T and a not in T:
                    T[a] = math.asin(_clamp(math.sin(T[s]) / ratio))
                elif a in T and s not in T:
                    T[s] = math.asin(_clamp(ratio * math.sin(T[a])))

        return {k: _fmt(v) for k, v in T.items()}

    # ---- Right triangle (C = π/2) ----

    @staticmethod
    def right_triangle(a=None, b=None, c=None, A=None, B=None):
        """
        Solve a right-angled triangle (C = π/2) using Napier's rules (§12.76–12.79).

        Right-angle formulae (C = π/2):
          sin a = sin c · sin A         [§12.76]
          sin b = sin c · sin B         [§12.76]
          cos c = cos a · cos b         [§12.77] (= cot A · cot B)
          cos A = cos a · sin B         [§12.78]
          cos B = cos b · sin A         [§12.78]
          tan a = tan c · cos B         [§12.79]
          tan b = tan c · cos A         [§12.79]
          tan a = sin b · tan A         [§12.79]
          tan b = sin a · tan B         [§12.79]
        """
        T = {k: v for k, v in [("a",a),("b",b),("c",c),("A",A),("B",B)] if v is not None}
        T["C"] = math.pi / 2

        max_iter = 10
        for _ in range(max_iter):
            prev_len = len(T)

            if "c" in T and "A" in T and "a" not in T:
                T["a"] = math.asin(_clamp(math.sin(T["c"]) * math.sin(T["A"])))
            if "c" in T and "B" in T and "b" not in T:
                T["b"] = math.asin(_clamp(math.sin(T["c"]) * math.sin(T["B"])))
            if "a" in T and "b" in T and "c" not in T:
                T["c"] = math.acos(_clamp(math.cos(T["a"]) * math.cos(T["b"])))
            if "a" in T and "B" in T and "A" not in T:
                T["A"] = math.acos(_clamp(math.cos(T["a"]) * math.sin(T["B"])))
                T["A"] = math.pi / 2 - math.asin(_clamp(math.cos(T["a"]) * math.sin(T["B"])))
                T["A"] = math.acos(_clamp(math.cos(T["a"]) * math.sin(T["B"])))
            if "b" in T and "A" in T and "B" not in T:
                T["B"] = math.acos(_clamp(math.cos(T["b"]) * math.sin(T["A"])))
            if "c" in T and "a" in T and "A" not in T:
                v = math.sin(T["a"]) / math.sin(T["c"])
                T["A"] = math.asin(_clamp(v))
            if "c" in T and "b" in T and "B" not in T:
                v = math.sin(T["b"]) / math.sin(T["c"])
                T["B"] = math.asin(_clamp(v))
            if "a" in T and "A" in T and "b" not in T and "B" in T:
                T["b"] = math.asin(_clamp(math.tan(T["a"]) / math.tan(T["A"])))
            if "A" in T and "B" in T and "c" not in T:
                T["c"] = math.acos(_clamp(1 / (math.tan(T["A"]) * math.tan(T["B"]))))

            if len(T) == prev_len:
                break

        return {k: _fmt(v) for k, v in T.items()}


# ================================================================
# CHAPTER 8 — HYPERBOLIC TRIGONOMETRY  (§12.9)
# ================================================================

class HyperbolicTrigonometry:
    """
    Trigonometry of a triangle in the hyperbolic plane (k = 1).

    Triangle ABC with sides a, b, c opposite angles A, B, C.
    Angles in radians; sides are hyperbolic lengths.

    Key formulae discovered by Lobatschewsky (§12.9):
      §12.93  Sine rule:     sinh a / sin A = sinh b / sin B = sinh c / sin C
      §12.94  Cosine rule I: cosh c = cosh a cosh b − sinh a sinh b cos C
      §12.95  Cosine rule II: cos C = −cos A cos B + sin A sin B cosh c

    Right-triangle formulae (C = π/2): §12.96–12.99
      §12.96  sinh a = sinh c · sin A
      §12.97  cosh c = cosh a · cosh b
      §12.98  cos A  = cosh a · sin B
      §12.99  tan A  = tanh a / sinh b  (= sin B · tan A  etc.)
    """

    @staticmethod
    def cosine_rule_side(a, b, C):
        """
        §12.94: cosh c = cosh a cosh b − sinh a sinh b cos C.
        Given two sides and included angle, find the third side.
        """
        val = math.cosh(a)*math.cosh(b) - math.sinh(a)*math.sinh(b)*math.cos(C)
        return _fmt(math.acosh(max(1.0, val)))

    @staticmethod
    def cosine_rule_angle(A, B, c):
        """
        §12.95: cos C = −cos A cos B + sin A sin B cosh c.
        Given two angles and included side, find the third angle.
        """
        val = _clamp(-math.cos(A)*math.cos(B) + math.sin(A)*math.sin(B)*math.cosh(c))
        return _fmt(math.acos(val))

    @staticmethod
    def sine_rule(a, A, b=None, B=None, c=None, C=None):
        """
        §12.93: sinh a / sin A = sinh b / sin B = sinh c / sin C.
        """
        ratio = math.sinh(a) / math.sin(A)
        result = {"ratio": _fmt(ratio)}
        if b is not None and B is None:
            result["B"] = _fmt(math.asin(_clamp(math.sinh(b) / ratio)))
        if B is not None and b is None:
            result["b"] = _fmt(math.asinh(ratio * math.sin(B)))
        return result

    @staticmethod
    def solve_triangle(a=None, b=None, c=None, A=None, B=None, C=None):
        """
        Solve a general hyperbolic triangle given any three parts.
        """
        T = {k: v for k, v in
             [("a",a),("b",b),("c",c),("A",A),("B",B),("C",C)]
             if v is not None}

        def _cos_s(s1, s2, ang):
            v = math.cosh(s1)*math.cosh(s2) - math.sinh(s1)*math.sinh(s2)*math.cos(ang)
            return math.acosh(max(1.0, v))

        def _cos_a(a1, a2, s):
            v = _clamp(-math.cos(a1)*math.cos(a2) + math.sin(a1)*math.sin(a2)*math.cosh(s))
            return math.acos(v)

        for s1, s2, ang, s3 in [("a","b","C","c"),("a","c","B","b"),("b","c","A","a")]:
            if s1 in T and s2 in T and ang in T and s3 not in T:
                T[s3] = _cos_s(T[s1], T[s2], T[ang])

        for a1, a2, s, a3 in [("A","B","c","C"),("A","C","b","B"),("B","C","a","A")]:
            if a1 in T and a2 in T and s in T and a3 not in T:
                T[a3] = _cos_a(T[a1], T[a2], T[s])

        pairs = [(T[s], T[a]) for s, a in [("a","A"),("b","B"),("c","C")]
                 if s in T and a in T]
        if pairs:
            ratio = math.sinh(pairs[0][0]) / math.sin(pairs[0][1])
            for s, a in [("a","A"),("b","B"),("c","C")]:
                if s in T and a not in T:
                    T[a] = math.asin(_clamp(math.sinh(T[s]) / ratio))
                elif a in T and s not in T:
                    v = ratio * math.sin(T[a])
                    T[s] = math.asinh(v)

        return {k: _fmt(v) for k, v in T.items()}

    @staticmethod
    def right_triangle(a=None, b=None, c=None, A=None, B=None):
        """
        Solve a right-angled hyperbolic triangle (C = π/2) using §12.96–12.99.

          sinh a = sinh c · sin A         [§12.96]
          cosh c = cosh a · cosh b        [§12.97]
          cos  A = cosh a · sin B         [§12.98]
          tan  A = tanh a / sinh b        [§12.99]
        """
        T = {k: v for k, v in [("a",a),("b",b),("c",c),("A",A),("B",B)] if v is not None}
        T["C"] = math.pi / 2

        for _ in range(10):
            prev = len(T)
            if "c" in T and "A" in T and "a" not in T:
                T["a"] = math.asinh(math.sinh(T["c"]) * math.sin(T["A"]))
            if "c" in T and "B" in T and "b" not in T:
                T["b"] = math.asinh(math.sinh(T["c"]) * math.sin(T["B"]))
            if "a" in T and "b" in T and "c" not in T:
                T["c"] = math.acosh(max(1.0, math.cosh(T["a"]) * math.cosh(T["b"])))
            if "a" in T and "B" in T and "A" not in T:
                T["A"] = math.acos(_clamp(math.cosh(T["a"]) * math.sin(T["B"])))
            if "b" in T and "A" in T and "B" not in T:
                T["B"] = math.acos(_clamp(math.cosh(T["b"]) * math.sin(T["A"])))
            if "a" in T and "b" in T and "A" not in T:
                T["A"] = math.atan(math.tanh(T["a"]) / math.sinh(T["b"]))
            if "a" in T and "b" in T and "B" not in T:
                T["B"] = math.atan(math.tanh(T["b"]) / math.sinh(T["a"]))
            if "a" in T and "A" in T and "c" not in T:
                v = math.sinh(T["a"]) / math.sin(T["A"])
                T["c"] = math.asinh(v)
            if len(T) == prev:
                break

        return {k: _fmt(v) for k, v in T.items()}


# ================================================================
# CHAPTER 9 — ELLIPTIC TRIANGLE  (§13.3, §12.7)
# ================================================================

class EllipticTriangle:
    """
    Properties and area of a triangle in the elliptic plane.

    §13.3:  Area = A + B + C − π   (angular excess)
    §13.31: A + B + C > π          (always)
    §12.73: Sine rule, §12.74–12.75: Cosine rules (see EllipticTrigonometry).
    """

    def __init__(self, a, b, c, A, B, C):
        """
        a, b, c — sides (radians); A, B, C — opposite angles (radians).
        """
        self.a, self.b, self.c = a, b, c
        self.A, self.B, self.C = A, B, C

    def angle_sum(self):
        return _fmt(self.A + self.B + self.C)

    def angular_excess(self):
        """
        The angular excess E = A + B + C − π > 0.  (§13.31)
        """
        return _fmt(self.A + self.B + self.C - math.pi)

    def area(self):
        """
        §13.32: Area = A + B + C − π  (for unit curvature radius k=1).
        For general k: Area = k² (A + B + C − π).
        """
        return _fmt(self.angular_excess())

    def area_k(self, k=1.0):
        """Area with curvature radius k."""
        return _fmt(k**2 * self.angular_excess())

    def check_sine_rule(self):
        """Verify the elliptic sine rule §12.73."""
        r_a = math.sin(self.a) / math.sin(self.A) if math.sin(self.A) != 0 else float('inf')
        r_b = math.sin(self.b) / math.sin(self.B) if math.sin(self.B) != 0 else float('inf')
        r_c = math.sin(self.c) / math.sin(self.C) if math.sin(self.C) != 0 else float('inf')
        return {"sin_a/sin_A": _fmt(r_a), "sin_b/sin_B": _fmt(r_b),
                "sin_c/sin_C": _fmt(r_c), "rule_holds": abs(r_a - r_b) < 1e-6}

    def incircle_radius(self, s=None):
        """
        §12.81: tan r = sin(s − a) tan(A/2)
        s = semiperimeter = (a+b+c)/2.
        """
        if s is None:
            s = (self.a + self.b + self.c) / 2
        r = math.atan(math.sin(s - self.a) * math.tan(self.A / 2))
        return _fmt(r)

    def circumradius(self, s=None, S=None):
        """
        §12.83: cot R = cos(S − A) cot(a/2)
        S = (A+B+C)/2.
        """
        if S is None:
            S = (self.A + self.B + self.C) / 2
        R = math.atan(1.0 / (math.cos(S - self.A) * (1.0 / math.tan(self.a / 2))))
        return _fmt(R)

    def full_info(self):
        s = (self.a + self.b + self.c) / 2
        S = (self.A + self.B + self.C) / 2
        return {
            "sides (rad)"     : (self.a, self.b, self.c),
            "angles (rad)"    : (self.A, self.B, self.C),
            "angle_sum"       : self.angle_sum(),
            "angular_excess"  : self.angular_excess(),
            "area (k=1)"      : self.area(),
            "sine_rule"       : self.check_sine_rule(),
            "inradius"        : self.incircle_radius(s),
            "circumradius"    : self.circumradius(s, S),
        }


# ================================================================
# CHAPTER 10 — HYPERBOLIC TRIANGLE  (§13.4, §12.9)
# ================================================================

class HyperbolicTriangle:
    """
    Properties and area of a triangle in the hyperbolic plane.

    §13.44: Area = π − A − B − C  (angular defect)
    §13.31: A + B + C < π          (always)
    """

    def __init__(self, a, b, c, A, B, C):
        self.a, self.b, self.c = a, b, c
        self.A, self.B, self.C = A, B, C

    def angle_sum(self):
        return _fmt(self.A + self.B + self.C)

    def angular_defect(self):
        """
        The angular defect δ = π − (A + B + C) > 0.  (Gauss–Lambert; §1.3, §13.44)
        """
        return _fmt(math.pi - (self.A + self.B + self.C))

    def area(self):
        """
        §13.44: Area = π − A − B − C  (for unit curvature radius k = 1).
        For general k: Area = k² (π − A − B − C).
        """
        return _fmt(self.angular_defect())

    def area_k(self, k=1.0):
        return _fmt(k**2 * self.angular_defect())

    def check_sine_rule(self):
        """Verify the hyperbolic sine rule §12.93: sinh a / sin A = ..."""
        r_a = math.sinh(self.a) / math.sin(self.A) if math.sin(self.A) != 0 else float('inf')
        r_b = math.sinh(self.b) / math.sin(self.B) if math.sin(self.B) != 0 else float('inf')
        r_c = math.sinh(self.c) / math.sin(self.C) if math.sin(self.C) != 0 else float('inf')
        return {"sinh_a/sin_A": _fmt(r_a), "sinh_b/sin_B": _fmt(r_b),
                "sinh_c/sin_C": _fmt(r_c), "rule_holds": abs(r_a - r_b) < 1e-6}

    def incircle_radius(self):
        """
        §12.9 radii: tanh r = sinh(s − a) tan(A/2)
        """
        s = (self.a + self.b + self.c) / 2
        r = math.atanh(math.tanh(math.sinh(s - self.a)) *
                       math.tan(self.A / 2))  # uses tanh(·) form
        # correct form:
        val = math.sinh(s - self.a) * math.tan(self.A / 2)
        r = math.atanh(min(0.9999999, val))
        return _fmt(r)

    def circumradius(self):
        """
        §12.9: coth R = cos(S − A) coth(a/2).
        S = (A+B+C)/2.
        """
        S = (self.A + self.B + self.C) / 2
        R = 1.0 / math.atanh(1.0 / (math.cos(S - self.A) / math.tanh(self.a / 2)))
        # Simpler: tanh R = 2 * Gamma^{-1/2} * cos S  (§12.9)
        return _fmt(abs(R))

    def is_asymptotic_vertex(self, vertex='A', tol=1e-9):
        """
        A vertex is asymptotic (at infinity on the Absolute) if the
        opposite side is 'infinite', i.e., the corresponding angle = 0.
        §13.4.
        """
        angle = {'A': self.A, 'B': self.B, 'C': self.C}[vertex]
        return abs(angle) < tol

    def full_info(self):
        return {
            "sides"           : (self.a, self.b, self.c),
            "angles (rad)"    : (self.A, self.B, self.C),
            "angle_sum"       : self.angle_sum(),
            "angular_defect"  : self.angular_defect(),
            "area (k=1)"      : self.area(),
            "sine_rule"       : self.check_sine_rule(),
            "asymptotic"      : {v: self.is_asymptotic_vertex(v)
                                 for v in ("A","B","C")},
        }


# ================================================================
# CHAPTER 11 — NON-EUCLIDEAN CIRCLE  (§11.1)
# ================================================================

class NonEuclideanCircle:
    """
    Three types of 'circle' in hyperbolic geometry (§11.1):
      1. Proper circle  — ordinary centre, constant radius R.
      2. Horocycle      — centre at infinity, 'radius' = ∞.
      3. Equidistant curve — ultra-infinite centre, constant distance D from axis.

    In elliptic geometry there is only a proper circle.

    Formulae (§11.1, §12.24):
      Proper circle (elliptic):    cos²R = g'/(zz)
      Proper circle (hyperbolic):  cosh²R = g'/(zz)
      Equidistant curve:           sinh²D = −g/[ZZ]

    Circumference and area (from Lobatschewsky / Taurinus §1.3):
      Elliptic  circumference: 2π k sin(R/k)
      Elliptic  area:          2π k² (1 − cos(R/k))
      Hyperbolic circumference: 2π k sinh(R/k)
      Hyperbolic area:          2π k² (cosh(R/k) − 1)
    """

    def __init__(self, geometry="hyperbolic", k=1.0):
        self.geometry = geometry
        self.k = k

    def circumference(self, R):
        """Circumference of a proper circle of radius R (§1.3)."""
        if self.geometry == "elliptic":
            return _fmt(2 * math.pi * self.k * math.sin(R / self.k))
        else:
            return _fmt(2 * math.pi * self.k * math.sinh(R / self.k))

    def area(self, R):
        """Area of a proper circle of radius R (§1.3)."""
        if self.geometry == "elliptic":
            return _fmt(2 * math.pi * self.k**2 * (1 - math.cos(R / self.k)))
        else:
            return _fmt(2 * math.pi * self.k**2 * (math.cosh(R / self.k) - 1))

    def classify(self, centre_type):
        """
        Classify the circle by the nature of its centre (§11.1).
        centre_type: 'ordinary', 'at_infinity', 'ultra_infinite'
        """
        names = {
            "ordinary"     : "Proper circle (constant radius R from centre)",
            "at_infinity"  : "Horocycle (centre at infinity; 'cycle')",
            "ultra_infinite": "Equidistant curve (constant distance D from axis)",
        }
        return names.get(centre_type, "Unknown circle type")

    def euclidean_limit(self, R):
        """
        As k → ∞, both geometries approach Euclidean geometry.
        Verify: circumference → 2πR, area → πR².
        """
        large_k = 1e6
        if self.geometry == "elliptic":
            C = 2 * math.pi * large_k * math.sin(R / large_k)
            A = 2 * math.pi * large_k**2 * (1 - math.cos(R / large_k))
        else:
            C = 2 * math.pi * large_k * math.sinh(R / large_k)
            A = 2 * math.pi * large_k**2 * (math.cosh(R / large_k) - 1)
        return {"circumference_approx": _fmt(C),
                "circumference_euclid": _fmt(2 * math.pi * R),
                "area_approx"         : _fmt(A),
                "area_euclid"         : _fmt(math.pi * R**2)}


# ================================================================
# CHAPTER 12 — ELLIPTIC CONGRUENT TRANSFORMATIONS  (§6.2–6.6)
# ================================================================

class EllipticTransform:
    """
    Congruent transformations of the elliptic plane (§6.2–6.6).
    Every congruent transformation is a rotation (§6.1 after Euler).

    A rotation through angle 2θ about centre P is the product of
    reflections in two lines through P that make angle θ.
    A translation does NOT exist as such in elliptic geometry;
    instead, every displacement is a rotation.

    Using unit quaternions (§6.8) for 3-D elliptic rotations.
    Here we work with 2-D elliptic transformations.
    """

    @staticmethod
    def reflection_in_line(point, line_normal):
        """
        Reflect point P = (x, y) in a line through the origin with unit normal n.
        (In elliptic geometry, a 'reflection' is also a rotation of π; §6.2.)
        point: (x, y)  line_normal: (nx, ny)  (unit vector ⊥ to line)
        Formula: P' = P − 2(P·n)n
        """
        x, y = point
        nx, ny = line_normal
        dot = x * nx + y * ny
        x_ref = x - 2 * dot * nx
        y_ref = y - 2 * dot * ny
        return (_fmt(x_ref), _fmt(y_ref))

    @staticmethod
    def rotation_2d(point, angle_rad):
        """
        Rotation of point (x, y) through angle θ in the elliptic plane
        (same formula as Euclidean rotation about origin; §6.3).
        """
        x, y = point
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return (_fmt(c * x - s * y), _fmt(s * x + c * y))

    @staticmethod
    def product_of_two_reflections(P, angle1_deg, angle2_deg):
        """
        Product of reflections in two lines through origin at angles α₁, α₂.
        The result is a rotation through 2(α₂ − α₁). (§6.3)
        """
        rotation_angle = 2 * _rad(angle2_deg - angle1_deg)
        return EllipticTransform.rotation_2d(P, rotation_angle)

    @staticmethod
    def is_involution(angle_rad, tol=1e-9):
        """
        A rotation of angle π is a half-turn (involution / point-reflection). §6.2.
        """
        return abs((angle_rad % (2 * math.pi)) - math.pi) < tol

    @staticmethod
    def clifford_parallel_displacement(P, shift):
        """
        Clifford parallels (§7.2): in elliptic 3-space, lines can be 'parallel'
        (equidistant) without being coplanar — called Clifford parallels.
        This simulates a left Clifford displacement by shift angle.
        """
        # In the elliptic plane, two lines are 'Clifford parallels' if they
        # belong to the same family of generators of a ruled quadric (§7.5).
        # A left Clifford displacement is a screw motion along the axis.
        # Represented here as rotation + translation on the 3-sphere.
        x, y = P
        r = math.sqrt(x**2 + y**2)
        if r < 1e-15:
            return P
        theta = math.atan2(y, x) + shift
        return (_fmt(r * math.cos(theta)), _fmt(r * math.sin(theta)))


# ================================================================
# CHAPTER 13 — HYPERBOLIC CONGRUENT TRANSFORMATIONS  (§10.3)
# ================================================================

class HyperbolicTransform:
    """
    Congruent transformations of the hyperbolic plane (§10.3).

    Four types (§10.3):
      (i)   Rotation            — product of reflections in two intersecting lines
      (ii)  Parallel displacement — product of reflections in two parallel lines
      (iii) Translation         — product of reflections in two ultra-parallel lines
      (iv)  Glide-reflection    — translation composed with a reflection

    All transformations preserve the Absolute conic x² + y² = 1.
    We use the hyperboloid model: points are (x, y, z) with x²+y²−z²=−1, z>0.
    In the Klein / Poincaré disc, the group is the Möbius group.
    """

    @staticmethod
    def rotation(P, angle_rad, centre=(0.0, 0.0)):
        """
        Rotation in the hyperbolic plane about an ordinary centre.
        In the Poincaré model, rotate the complex number representation.
        P and centre are (x, y) coordinates in the Poincaré disc.
        """
        cx, cy = centre
        # translate centre to origin, rotate, translate back
        x, y = P[0] - cx, P[1] - cy
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        x2 = c * x - s * y
        y2 = s * x + c * y
        return (_fmt(x2 + cx), _fmt(y2 + cy))

    @staticmethod
    def poincare_translation(P, t):
        """
        Hyperbolic translation along the x-axis by hyperbolic distance t. (§10.3)
        In the Poincaré disc, this is the Möbius map:
            w ↦ (w + tanh(t/2)) / (1 + tanh(t/2)·w*)
        for a real translation parameter.
        P = (x, y) as a point in the unit disc.
        """
        w = complex(P[0], P[1])
        a = math.tanh(t / 2)
        w2 = (w + a) / (1 + a * w.conjugate())
        return (_fmt(w2.real), _fmt(w2.imag))

    @staticmethod
    def translation_type(line1_type, line2_type):
        """
        Classify the transformation that is the product of reflections in
        two lines (§10.3):
          Both intersecting  → Rotation
          Both parallel      → Parallel displacement
          Both ultra-parallel → Translation
        """
        key = (line1_type, line2_type)
        table = {
            ("intersecting", "intersecting") : "Rotation",
            ("parallel"    , "parallel"    ) : "Parallel displacement",
            ("ultra_parallel","ultra_parallel"): "Translation (glide if plus reflection)",
        }
        return table.get(key, "Unknown — check line types")

    @staticmethod
    def glide_reflection(P, translation_dist, axis_angle_rad=0.0):
        """
        Glide-reflection (§10.3 / §15.1): translation along axis followed by
        reflection in the axis.  Axis is taken as the x-axis here (angle 0).
        P = (x, y) in the Poincaré disc.
        """
        # First: translate along axis
        P2 = HyperbolicTransform.poincare_translation(P, translation_dist)
        # Then: reflect in the axis (flip y)
        return (P2[0], _fmt(-P2[1]))

    @staticmethod
    def hjelmslev_midpoint(A, Ap):
        """
        §15.1 — Hjelmslev's Theorem: If X↦X' is any congruent mapping of one
        line to another, the mid-points of segments XX' are collinear.
        Returns the mid-point of segment AA' in the Poincaré disc model.
        """
        # Mid-point in Poincaré disc using the hyperbolic midpoint formula
        a = complex(A[0], A[1])
        b = complex(Ap[0], Ap[1])
        # Translate A to origin, find midpoint, translate back
        # Möbius map: φ takes A → 0
        def mobius_to_origin(z, w):
            return (z - w) / (1 - w.conjugate() * z)

        a0 = mobius_to_origin(b, a)  # B in coordinates where A is origin
        # Hyperbolic midpoint = point at half the hyperbolic distance
        d_half = abs(a0) / (1 + math.sqrt(1 - abs(a0)**2)) * 0
        # Correct: midpoint of geodesic from 0 to z in Poincaré disc = z * tanh(d/2) / tanh(d)
        d = 2 * math.atanh(abs(a0))
        if d < 1e-15:
            mid0 = complex(0, 0)
        else:
            mid0 = a0 / abs(a0) * math.tanh(d / 2)
        # Translate back
        mid = mobius_to_origin(mid0, -a)
        return (_fmt(mid.real), _fmt(mid.imag))


# ================================================================
# CHAPTER 14 — POINCARÉ DISC MODEL  (§14.8)
# ================================================================

class PoincareModel:
    """
    Poincaré's conformal model of the hyperbolic plane (§14.8).

    Points: interior of the unit disc, |z| < 1.
    Geodesics: arcs of circles orthogonal to the unit circle, plus diameters.
    Distance: d(z, w) = 2 arc tanh |z − w| / |1 − z̄w|
              (or d = arg cosh(1 + 2|z−w|²/((1−|z|²)(1−|w|²))))

    The model is conformal — angles between curves are true angles.
    """

    @staticmethod
    def distance(P1, P2):
        """
        Hyperbolic distance between two Poincaré disc points P1, P2 ∈ unit disc.
        §14.8:  d = 2 arc tanh |P1 − P2| / |1 − P̄₁ P₂|
        """
        z1 = complex(P1[0], P1[1])
        z2 = complex(P2[0], P2[1])
        num = abs(z1 - z2)
        den = abs(1 - z1.conjugate() * z2)
        if den < 1e-15:
            return float('inf')
        ratio = num / den
        ratio = min(ratio, 1 - 1e-15)
        return _fmt(2 * math.atanh(ratio))

    @staticmethod
    def midpoint(P1, P2):
        """Hyperbolic midpoint of P1 and P2 in the Poincaré disc."""
        d = PoincareModel.distance(P1, P2)
        z1 = complex(P1[0], P1[1])
        z2 = complex(P2[0], P2[1])
        # Translate P1 to origin
        w = (z2 - z1) / (1 - z1.conjugate() * z2)
        # Midpoint at half distance in direction of w
        d2 = abs(w)
        if d2 < 1e-15:
            return P1
        mid_w = w / d2 * math.tanh(math.atanh(d2) / 2)
        # Translate back
        mid = (mid_w + z1) / (1 + z1.conjugate() * mid_w)
        return (_fmt(mid.real), _fmt(mid.imag))

    @staticmethod
    def geodesic_centre_radius(P1, P2):
        """
        For two non-antipodal points in the Poincaré disc, the geodesic is an
        arc of a circle.  Returns (centre, radius) of that circle in the
        Euclidean plane, or 'diameter' if the geodesic passes through the origin.
        """
        z1 = complex(P1[0], P1[1])
        z2 = complex(P2[0], P2[1])
        # If both points lie on a diameter through the origin, geodesic = line
        cross = z1.real * z2.imag - z1.imag * z2.real
        if abs(cross) < 1e-9:
            return {"type": "diameter (Euclidean straight line through origin)"}
        # Inversion: find circle through z1, z2 orthogonal to unit circle
        # Centre on the intersection of perpendicular bisectors
        # For z on unit circle, its inverse is 1/z̄; the orthogonal circle passes
        # through z1, 1/z̄₁, z2, 1/z̄₂.
        w1 = 1 / z1.conjugate()
        w2 = 1 / z2.conjugate()
        # Three points: z1, z2, w1 → circumcircle
        ax, ay = z1.real, z1.imag
        bx, by = z2.real, z2.imag
        cx, cy = w1.real, w1.imag
        D  = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
        if abs(D) < 1e-15:
            return {"type": "degenerate"}
        ux = ((ax**2+ay**2)*(by-cy) + (bx**2+by**2)*(cy-ay) + (cx**2+cy**2)*(ay-by)) / D
        uy = ((ax**2+ay**2)*(cx-bx) + (bx**2+by**2)*(ax-cx) + (cx**2+cy**2)*(bx-ax)) / D
        r  = math.sqrt((ax-ux)**2 + (ay-uy)**2)
        return {"centre": (_fmt(ux), _fmt(uy)), "radius": _fmt(r)}

    @staticmethod
    def angle_of_parallelism(c):
        """
        Poincaré model verification of Π(c) = 2 arc tan(e^{−c}). §1.4
        """
        return AngleOfParallelism.angle(c)

    @staticmethod
    def is_inside_disc(P, tol=1e-9):
        """Check that P is a valid Poincaré disc point (|P| < 1)."""
        return P[0]**2 + P[1]**2 < 1 - tol


# ================================================================
# CHAPTER 15 — KLEIN (PROJECTIVE) DISC MODEL  (§8.1)
# ================================================================

class KleinModel:
    """
    Klein's projective (non-conformal) model of the hyperbolic plane (§8.1).

    Points: interior of the unit disc.
    Geodesics: Euclidean chords of the disc.
    Distance: d(A, B) = ½ |log {AB, MN}|  (cross-ratio with the boundary
              points M, N where the chord through A and B meets the Absolute).
    Angles: NOT Euclidean — must be computed via the polarity.

    Relationship to Poincaré model: the two models are related by the map
    z_Klein = 2 z_Poincaré / (1 + |z_Poincaré|²).   (§14.7)
    """

    @staticmethod
    def distance(A, B):
        """
        Hyperbolic distance in the Klein model between interior points A and B.
        §10.31: d = ½ |log {AB, MN}|, where M, N are on the unit circle.

        We parametrize the line through A and B, find where it hits the circle.
        """
        ax, ay = A
        bx, by = B
        dx, dy = bx - ax, by - ay
        mag = math.sqrt(dx**2 + dy**2)
        if mag < 1e-15:
            return 0.0
        # Line: (ax + t·dx, ay + t·dy), hits unit circle when
        # (ax+t·dx)² + (ay+t·dy)² = 1
        # t²(dx²+dy²) + 2t(ax·dx+ay·dy) + (ax²+ay²−1) = 0
        a_ = dx**2 + dy**2
        b_ = 2 * (ax * dx + ay * dy)
        c_ = ax**2 + ay**2 - 1
        disc = b_**2 - 4 * a_ * c_
        if disc < 0:
            raise ValueError("Points are outside or on the Absolute.")
        sq = math.sqrt(disc)
        t1 = (-b_ - sq) / (2 * a_)
        t2 = (-b_ + sq) / (2 * a_)
        M = (ax + t1 * dx, ay + t1 * dy)
        N = (ax + t2 * dx, ay + t2 * dy)
        # Parametric values for A and B: tA = 0, tB = 1 (we normalise)
        # Use the 1-D cross-ratio of parameters: {0, 1, t1, t2}  (t-values on line)
        # Cross-ratio {AB, MN} in parameter t:  t_A=0, t_B=1, t_M=t1, t_N=t2
        cr = ProjectiveBase.cross_ratio(0.0, 1.0, t1, t2)
        if cr <= 0:
            return float('inf')
        return _fmt(0.5 * abs(math.log(cr)))

    @staticmethod
    def poincare_to_klein(P):
        """
        Convert Poincaré disc point to Klein disc point. §14.7.
        z_K = 2 z_P / (1 + |z_P|²)
        """
        x, y = P
        r2 = x**2 + y**2
        denom = 1 + r2
        return (_fmt(2 * x / denom), _fmt(2 * y / denom))

    @staticmethod
    def klein_to_poincare(P):
        """
        Convert Klein disc point to Poincaré disc point.
        z_P = z_K / (1 + √(1 − |z_K|²))
        """
        x, y = P
        r2 = x**2 + y**2
        denom = 1 + math.sqrt(max(0.0, 1 - r2))
        return (_fmt(x / denom), _fmt(y / denom))

    @staticmethod
    def are_perpendicular_klein(X, Y):
        """
        Two chords (lines) in the Klein model are perpendicular iff they are
        conjugate with respect to the Absolute (unit circle). §10.1.
        X = (A, B) and Y = (C, D) are endpoints on the unit circle.
        Conjugate chords: each chord passes through the pole of the other.
        """
        # Pole of chord AB in the unit conic x²+y²=1:
        # Use AbsolutePolarity with the hyperbolic canonical form.
        return {"note": "Perpendicularity in Klein model requires pole-polar check "
                         "with respect to the Absolute (unit conic). Use "
                         "AbsolutePolarity.are_conjugate() with the line coordinates."}


# ================================================================
# CHAPTER 16 — SPHERICAL TRIGONOMETRY  (= Elliptic, §12.7 note)
# ================================================================

class SphericalTrigonometry:
    """
    Spherical geometry is identical to elliptic geometry (§12.7 note,
    §6.1).  This class provides the standard spherical-trig formulae as
    a convenient alias.

    Triangle on a unit sphere with sides a, b, c (arc lengths in radians)
    and opposite angles A, B, C.
    """

    @staticmethod
    def cosine_rule(a, b, C):
        """cos c = cos a cos b + sin a sin b cos C  (standard spherical cosine rule)."""
        return EllipticTrigonometry.cosine_rule_side(a, b, C)

    @staticmethod
    def cosine_rule_angles(A, B, c):
        """cos C = −cos A cos B + sin A sin B cos c."""
        return EllipticTrigonometry.cosine_rule_angle(A, B, c)

    @staticmethod
    def sine_rule(a, A, b=None, B=None):
        """sin a / sin A = sin b / sin B."""
        return EllipticTrigonometry.sine_rule(a, A, b=b, B=B)

    @staticmethod
    def excess(A, B, C):
        """Spherical excess E = A + B + C − π (equals area on unit sphere)."""
        return _fmt(A + B + C - math.pi)

    @staticmethod
    def area(A, B, C, R=1.0):
        """Area = R² (A + B + C − π)."""
        return _fmt(R**2 * SphericalTrigonometry.excess(A, B, C))

    @staticmethod
    def haversine_distance(lat1_deg, lon1_deg, lat2_deg, lon2_deg, R=6371.0):
        """
        Great-circle distance between two points on a sphere of radius R
        (default: Earth radius 6371 km) using the haversine formula.
        (Spherical / elliptic geometry applied to navigation.)
        """
        phi1, phi2 = _rad(lat1_deg), _rad(lat2_deg)
        dphi       = _rad(lat2_deg - lat1_deg)
        dlam       = _rad(lon2_deg - lon1_deg)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
        return _fmt(2 * R * math.asin(math.sqrt(a)))
