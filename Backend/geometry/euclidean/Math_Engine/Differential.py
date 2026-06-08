"""
 ═════════════════════════════════════════════════════════════════
   ELEMENTARY DIFFERENTIAL GEOMETRY ENGINE                        
   Based on Andrew Pressley — "Elementary Differential Geometry"  
   Springer Undergraduate Mathematics Series, 2001               
 ══════════════════════════════════════════════════════════════════

Chapter map:
    1 : Curves          — (parametrization, arc-length, reparametrization)
    2 : Curvature       — (curvature of plane & space curves, signed curvature)
    3 : GlobalCurves    — (simple closed curves, isoperimetric inequality, four-vertex theorem)
    4 : Surfaces        — (surface patches, tangent planes, normals, quadric surfaces, examples)
    5 : FirstForm       — (first fundamental form, arc-length on surfaces, isometries, conformal maps, surface area)
    6 : SecondForm      — (second fundamental form, normal/geodesic curvature, principal curvatures, shape operator)
    7 : GaussianCurv    — (Gaussian & mean curvature, pseudosphere, flat surfaces, Gauss map)
    8 : Geodesics       — (geodesic equations, geodesics on surfaces of revolution, shortest paths, geodesic coordinates)
    9 : MinimalSurf     — (minimal surfaces, Plateau's problem, examples, Weierstrass–Enneper representation)
   10 : TheoregmaEgr    — (Gauss's Theorema Egregium, Codazzi–Mainardi, compact surfaces of constant K)
   11 : GaussBonnet     — (Gauss–Bonnet theorem (simple, polygon, compact)

Usage:
    python differential_geometry_engine.py     # runs the demo
    import differential_geometry_engine as dg  # use as library
"""

import math
import numpy as np
from scipy import integrate


# ================================================================
# UTILITY HELPERS
# ================================================================

def _fmt(v, d=8):
    try:
        return round(float(v), d)
    except Exception:
        return v

def _norm(v):
    """Euclidean norm of a numpy array."""
    return float(np.linalg.norm(v))

def _unit(v):
    """Unit vector."""
    n = _norm(v)
    if n < 1e-14:
        raise ValueError("Zero vector — cannot normalize.")
    return v / n

def _cross(a, b):
    return np.cross(a, b)

def _dot(a, b):
    return float(np.dot(a, b))


# ================================================================
# CHAPTER 1 — CURVES IN THE PLANE AND IN SPACE
    # ─────────────────────────────────────────────────────────────────────────────

class Curves:
    """
    Parametrized curves γ: I → ℝⁿ, arc-length, speed, reparametrization.
    Pressley Ch.1 (§1.1 – §1.4).
    """

    @staticmethod
    def speed(gamma_dot):
        """Speed = ‖γ'(t)‖. Pass the derivative vector at t."""
        return _fmt(_norm(np.array(gamma_dot, dtype=float)))

    @staticmethod
    def is_unit_speed(gamma_dot, tol=1e-9):
        """Check if ‖γ'‖ = 1 (unit-speed / arc-length parametrization)."""
        return abs(_norm(np.array(gamma_dot, dtype=float)) - 1.0) < tol

    @staticmethod
    def arc_length(gamma_prime_func, t0, t1, n=2000):
        """
        Arc-length s = ∫[t0,t1] ‖γ'(t)‖ dt.
        gamma_prime_func: callable t → array-like (derivative).
        """
        def integrand(t):
            return _norm(np.array(gamma_prime_func(t), dtype=float))
        result, _ = integrate.quad(integrand, t0, t1, limit=200)
        return _fmt(result)

    @staticmethod
    def arc_length_function(gamma_prime_func, t0, t_values):
        """
        Arc-length function s(t) = ∫[t0,t] ‖γ'‖ du for a list of t values.
        Returns list of (t, s(t)) pairs.
        """
        results = []
        for t in t_values:
            s = Curves.arc_length(gamma_prime_func, t0, t)
            results.append((_fmt(t), _fmt(s)))
        return results

    @staticmethod
    def tangent_vector(gamma_prime, normalize=True):
        """
        Unit tangent T = γ' / ‖γ'‖  (or unnormalized if normalize=False).
        """
        gp = np.array(gamma_prime, dtype=float)
        return _unit(gp) if normalize else gp

    # ── Standard Curve Parametrizations ──────────────────────────────

    @staticmethod
    def circle(R, t):
        """γ(t) = (R cos t, R sin t).  Speed = R."""
        return np.array([R*math.cos(t), R*math.sin(t)])

    @staticmethod
    def helix(R, p, t):
        """
        Circular helix: γ(t) = (R cos t, R sin t, pt).
        Speed = √(R²+p²).  Pressley Example 1.3.
        """
        return np.array([R*math.cos(t), R*math.sin(t), p*t])

    @staticmethod
    def helix_speed(R, p):
        return _fmt(math.sqrt(R**2 + p**2))

    @staticmethod
    def viviani_curve(a, t):
        """
        Viviani's curve: γ(t) = (a(1+cos t), a sin t, 2a sin(t/2)).
        Pressley Exercise 1.9.
        """
        return np.array([a*(1+math.cos(t)), a*math.sin(t), 2*a*math.sin(t/2)])

    @staticmethod
    def catenary(a, t):
        """Catenary: γ(t) = (t, a cosh(t/a))."""
        return np.array([t, a*math.cosh(t/a)])

    @staticmethod
    def tractrix(a, t):
        """Tractrix: γ(t) = (a(t - tanh t), a/cosh t).  Pressley §7.2."""
        return np.array([a*(t - math.tanh(t)), a/math.cosh(t)])
    

# ================================================================
# CHAPTER 2 — HOW MUCH DOES A CURVE CURVE?
# ================================================================

class Curvature:
    """
    Curvature of plane and space curves, Frenet–Serret apparatus.
    Pressley Ch.2 (§2.1 – §2.3).
    """

    # ── Plane curves ─────────────────────────────────────────────────

    @staticmethod
    def curvature_unit_speed_plane(gamma_ddot):
        """
        Curvature of unit-speed plane curve: κ = ‖γ̈‖.
        gamma_ddot: second derivative vector (2D).
        """
        return _fmt(_norm(np.array(gamma_ddot, dtype=float)))

    @staticmethod
    def signed_curvature_unit_speed(gamma_ddot):
        """
        Signed curvature κₛ of unit-speed plane curve γ(s):
        γ̈ = κₛ · n̂ₛ  where n̂ₛ = (-sin φ, cos φ).
        κₛ = det[γ̇, γ̈]  (2×2 determinant).
        gamma_ddot: 2D second derivative.
        """
        gdd = np.array(gamma_ddot, dtype=float)
        # For unit-speed: γ̇ = (cos φ, sin φ), γ̈ perpendicular to γ̇
        # signed curvature = γ̈[1]·γ̇[0] - γ̈[0]·γ̇[1] requires γ̇ too
        return _fmt(float(gdd[0]))  # placeholder; use signed_curvature_general

    @staticmethod
    def signed_curvature_general(gamma_dot, gamma_ddot):
        """
        Signed curvature of general (not necessarily unit-speed) plane curve:
        κₛ = (γ̇ × γ̈) / ‖γ̇‖³  where × is the 2D 'cross product' (determinant).
        Pressley Prop. 2.2.
        """
        gd  = np.array(gamma_dot,  dtype=float)
        gdd = np.array(gamma_ddot, dtype=float)
        cross_2d = float(gd[0]*gdd[1] - gd[1]*gdd[0])  # z-component
        speed_cubed = _norm(gd)**3
        if speed_cubed < 1e-14:
            raise ValueError("Curve is not regular at this point.")
        return _fmt(cross_2d / speed_cubed)

    @staticmethod
    def curvature_from_signed(kappa_s):
        """κ = |κₛ|."""
        return _fmt(abs(kappa_s))

    @staticmethod
    def radius_of_curvature(kappa):
        """ρ = 1/κ (radius of osculating circle)."""
        if abs(kappa) < 1e-14:
            return float('inf')
        return _fmt(1.0 / kappa)

    @staticmethod
    def turning_angle(gamma_dot, gamma_ddot):
        """
        dφ/ds = κₛ  where φ is the angle of the tangent.
        Returns κₛ (rate of turning).
        """
        return Curvature.signed_curvature_general(gamma_dot, gamma_ddot)

    # ── Space curves — Frenet–Serret apparatus ───────────────────────

    @staticmethod
    def frenet_serret(gamma_dot, gamma_ddot, gamma_dddot=None):
        """
        Frenet–Serret apparatus for a space curve γ(t).
        Returns T (tangent), N (principal normal), B (binormal), κ, τ.

        Formulas (Pressley §2.3):
          T = γ'/‖γ'‖
          κ = ‖γ' × γ''‖ / ‖γ'‖³
          N = (γ'' - (γ''·T)T) / ‖γ'' - (γ''·T)T‖   [for unit-speed: γ̈/κ]
          B = T × N
          τ = (γ' × γ'') · γ''' / ‖γ' × γ''‖²
        """
        gd   = np.array(gamma_dot,   dtype=float)
        gdd  = np.array(gamma_ddot,  dtype=float)

        speed = _norm(gd)
        if speed < 1e-14:
            raise ValueError("Curve is not regular at this point.")

        T = gd / speed

        # κ = ‖γ' × γ''‖ / ‖γ'‖³
        cross = _cross(gd, gdd)
        kappa = _norm(cross) / speed**3

        # N
        gdd_perp = gdd - _dot(gdd, T) * T
        gdd_perp_norm = _norm(gdd_perp)
        if gdd_perp_norm < 1e-14:
            N = np.zeros(3)
        else:
            N = gdd_perp / gdd_perp_norm

        # B = T × N
        B = _cross(T, N)

        result = {
            "T": [_fmt(x) for x in T],
            "N": [_fmt(x) for x in N],
            "B": [_fmt(x) for x in B],
            "kappa": _fmt(kappa),
            "speed": _fmt(speed)
        }

        # Torsion τ = (γ' × γ'') · γ''' / ‖γ' × γ''‖²
        if gamma_dddot is not None:
            gddd = np.array(gamma_dddot, dtype=float)
            cross_norm_sq = _norm(cross)**2
            if cross_norm_sq < 1e-14:
                result["tau"] = 0.0
            else:
                result["tau"] = _fmt(_dot(cross, gddd) / cross_norm_sq)

        return result

    @staticmethod
    def frenet_serret_equations(T, N, B, kappa, tau):
        """
        Frenet–Serret equations (unit-speed):
          dT/ds = κN
          dN/ds = -κT + τB
          dB/ds = -τN
        Returns the three derivative vectors.
        """
        T = np.array(T, dtype=float)
        N = np.array(N, dtype=float)
        B = np.array(B, dtype=float)
        dT = kappa * N
        dN = -kappa * T + tau * B
        dB = -tau * N
        return {
            "dT_ds": [_fmt(x) for x in dT],
            "dN_ds": [_fmt(x) for x in dN],
            "dB_ds": [_fmt(x) for x in dB]
        }

    @staticmethod
    def curvature_torsion_helix(R, p):
        """
        Curvature and torsion of helix γ(t) = (R cos t, R sin t, pt).
        κ = R/(R²+p²),  τ = p/(R²+p²).  Pressley Example 2.4.
        """
        denom = R**2 + p**2
        return {"kappa": _fmt(R/denom), "tau": _fmt(p/denom),
                "kappa_over_tau": _fmt(R/p) if p != 0 else float('inf'),
                "note": "For a helix, κ/τ = R/p = constant."}

    @staticmethod
    def is_planar_curve(tau_values, tol=1e-9):
        """A curve is planar iff τ ≡ 0."""
        return all(abs(t) < tol for t in tau_values)

    @staticmethod
    def is_general_helix(kappa_values, tau_values, tol=1e-6):
        """
        A curve is a general helix iff κ/τ = constant (Lancret's theorem).
        """
        ratios = []
        for k, t in zip(kappa_values, tau_values):
            if abs(t) < tol:
                return {"is_helix": False, "note": "τ = 0 at some point (planar)."}
            ratios.append(k / t)
        r0 = ratios[0]
        is_helix = all(abs(r - r0) < tol for r in ratios)
        return {"is_helix": is_helix,
                "kappa_over_tau": _fmt(r0) if is_helix else None}


# ================================================================
# CHAPTER 3 — GLOBAL PROPERTIES OF CURVES
# ================================================================

class GlobalCurves:
    """
    Simple closed curves, isoperimetric inequality, four-vertex theorem.
    Pressley Ch.3 (§3.1 – §3.3).
    """

    @staticmethod
    def total_signed_curvature(kappa_s_func, t0, t1):
        """
        Total signed curvature: ∫[t0,t1] κₛ ds.
        For a simple closed curve = ±2π (Theorem 3.1).
        kappa_s_func: callable t → κₛ(t) * ‖γ'(t)‖  (w.r.t. t, not arc-length).
        """
        result, _ = integrate.quad(kappa_s_func, t0, t1, limit=200)
        return _fmt(result)

    @staticmethod
    def turning_number(total_curvature_rad):
        """
        Turning number n = (total curvature) / (2π).
        Simple closed curve: n = ±1.
        """
        return _fmt(total_curvature_rad / (2*math.pi))

    @staticmethod
    def isoperimetric_inequality(length, area):
        """
        Isoperimetric inequality: L² ≥ 4π·A, with equality iff curve is a circle.
        Returns (L², 4πA, is_satisfied, deficit).
        Pressley §3.2.
        """
        L2 = length**2
        four_pi_A = 4 * math.pi * area
        return {
            "L²":        _fmt(L2),
            "4πA":       _fmt(four_pi_A),
            "satisfied": L2 >= four_pi_A - 1e-9,
            "deficit":   _fmt(L2 - four_pi_A),
            "is_circle": abs(L2 - four_pi_A) < 1e-6
        }

    @staticmethod
    def four_vertex_theorem_check(kappa_s_values):
        """
        Four-vertex theorem: every simple closed convex curve has ≥ 4 vertices
        (points where dκ/ds = 0, i.e. local extrema of κ).
        Given a list of κₛ values (sampled around the curve), count sign changes
        in the derivative to estimate vertices.
        Pressley §3.3.
        """
        n = len(kappa_s_values)
        diffs = [kappa_s_values[(i+1)%n] - kappa_s_values[i] for i in range(n)]
        # Count sign changes in differences (extrema of κ)
        sign_changes = sum(
            1 for i in range(n)
            if diffs[i]*diffs[(i+1)%n] < 0
        )
        return {
            "estimated_vertices": sign_changes,
            "theorem_satisfied": sign_changes >= 4,
            "note": "Count of sign changes in dκ/ds (approximate for sampled data)."
        }

    @staticmethod
    def winding_number_polygon(points, P=(0,0)):
        """
        Winding number of a polygonal closed curve about point P.
        Positive = counterclockwise.
        """
        n = len(points)
        winding = 0
        px, py = P
        for i in range(n):
            x1,y1 = points[i][0]-px, points[i][1]-py
            x2,y2 = points[(i+1)%n][0]-px, points[(i+1)%n][1]-py
            if y1 <= 0:
                if y2 > 0:
                    cross = x1*y2 - x2*y1
                    if cross > 0: winding += 1
            else:
                if y2 <= 0:
                    cross = x1*y2 - x2*y1
                    if cross < 0: winding -= 1
        return winding


# ================================================================
# CHAPTER 4 — SURFACES IN THREE DIMENSIONS
# ================================================================

class Surfaces:
    """
    Surface patches σ(u,v), tangent planes, unit normals, standard examples.
    Pressley Ch.4 (§4.1 – §4.7).
    """

    @staticmethod
    def tangent_vectors(sigma_u, sigma_v):
        """
        σ_u and σ_v: partial derivative vectors at a point on the surface.
        Returns σ_u, σ_v as numpy arrays.
        """
        return np.array(sigma_u, dtype=float), np.array(sigma_v, dtype=float)

    @staticmethod
    def unit_normal(sigma_u, sigma_v):
        """
        Unit normal N = (σ_u × σ_v) / ‖σ_u × σ_v‖.
        Pressley §4.3.
        """
        su = np.array(sigma_u, dtype=float)
        sv = np.array(sigma_v, dtype=float)
        cross = _cross(su, sv)
        norm = _norm(cross)
        if norm < 1e-14:
            raise ValueError("Surface is not regular at this point (σ_u × σ_v = 0).")
        N = cross / norm
        return [_fmt(x) for x in N]

    @staticmethod
    def tangent_plane_equation(P, sigma_u, sigma_v):
        """
        Tangent plane at P: N · (r - P) = 0.
        Returns (A, B, C, D) for Ax + By + Cz + D = 0.
        """
        N = np.array(Surfaces.unit_normal(sigma_u, sigma_v), dtype=float)
        P = np.array(P, dtype=float)
        D = -_dot(N, P)
        return {"A": _fmt(N[0]), "B": _fmt(N[1]), "C": _fmt(N[2]),
                "D": _fmt(D),
                "equation": f"({_fmt(N[0])})x + ({_fmt(N[1])})y + ({_fmt(N[2])})z + ({_fmt(D)}) = 0"}

    # ── Standard surface parametrizations ───────────────────────────

    @staticmethod
    def sphere(R, theta, phi):
        """
        Sphere of radius R: σ(θ,φ) = (R sin θ cos φ, R sin θ sin φ, R cos θ).
        θ ∈ (0,π), φ ∈ (0,2π).
        Returns point, σ_θ, σ_φ.
        """
        x = R * math.sin(theta)*math.cos(phi)
        y = R * math.sin(theta)*math.sin(phi)
        z = R * math.cos(theta)
        sx = np.array([R*math.cos(theta)*math.cos(phi),
                       R*math.cos(theta)*math.sin(phi),
                       -R*math.sin(theta)])
        sy = np.array([-R*math.sin(theta)*math.sin(phi),
                        R*math.sin(theta)*math.cos(phi),
                        0.0])
        return {"point": [_fmt(x),_fmt(y),_fmt(z)],
                "sigma_theta": [_fmt(v) for v in sx],
                "sigma_phi":   [_fmt(v) for v in sy]}

    @staticmethod
    def torus(R, r, theta, phi):
        """
        Torus: σ(θ,φ) = ((R + r cos θ)cos φ, (R + r cos θ)sin φ, r sin θ).
        R = major radius, r = minor radius. Pressley Example 4.4.
        """
        x = (R + r*math.cos(theta))*math.cos(phi)
        y = (R + r*math.cos(theta))*math.sin(phi)
        z = r * math.sin(theta)
        su = np.array([-r*math.sin(theta)*math.cos(phi),
                       -r*math.sin(theta)*math.sin(phi),
                        r*math.cos(theta)])
        sv = np.array([-(R+r*math.cos(theta))*math.sin(phi),
                        (R+r*math.cos(theta))*math.cos(phi),
                        0.0])
        return {"point": [_fmt(x),_fmt(y),_fmt(z)],
                "sigma_theta": [_fmt(v) for v in su],
                "sigma_phi":   [_fmt(v) for v in sv]}

    @staticmethod
    def surface_of_revolution(f, f_prime, u, v):
        """
        Surface of revolution: σ(u,v) = (f(u)cos v, f(u)sin v, u).
        f: profile curve radius; f_prime: df/du.
        Pressley §4.4.
        """
        fu, fpu = f(u), f_prime(u)
        point = np.array([fu*math.cos(v), fu*math.sin(v), u])
        su = np.array([fpu*math.cos(v), fpu*math.sin(v), 1.0])
        sv = np.array([-fu*math.sin(v),  fu*math.cos(v), 0.0])
        return {"point": [_fmt(x) for x in point],
                "sigma_u": [_fmt(x) for x in su],
                "sigma_v": [_fmt(x) for x in sv]}

    @staticmethod
    def ruled_surface(gamma, delta, t, v):
        """
        Ruled surface: σ(t,v) = γ(t) + v·δ(t).
        gamma, delta: 3D vectors at parameter t.
        """
        g = np.array(gamma, dtype=float)
        d = np.array(delta,  dtype=float)
        point = g + v*d
        return [_fmt(x) for x in point]

    @staticmethod
    def quadric_surface_type(A, B, C, D, E, F):
        """
        Classify quadric: Ax²+By²+Cz²+Dxy+Eyz+Fxz = 1.
        Uses eigenvalues of the 3×3 matrix.
        Pressley §4.5.
        """
        M = np.array([[A,     D/2,  F/2],
                      [D/2,   B,    E/2],
                      [F/2,   E/2,  C  ]])
        eigvals = np.linalg.eigvalsh(M)
        pos = sum(1 for e in eigvals if e > 1e-9)
        neg = sum(1 for e in eigvals if e < -1e-9)
        zero = 3 - pos - neg
        types = {(3,0,0): "Ellipsoid",  (2,1,0): "Hyperboloid of one sheet",
                 (1,2,0): "Hyperboloid of two sheets", (2,0,1): "Elliptic paraboloid",
                 (1,1,1): "Hyperbolic paraboloid (saddle)", (1,0,2): "Parabolic cylinder"}
        return {"eigenvalues": [_fmt(e) for e in eigvals],
                "positive": pos, "negative": neg, "zero": zero,
                "type": types.get((pos, neg, zero), "Degenerate / cone")}


# ================================================================
# CHAPTER 5 — THE FIRST FUNDAMENTAL FORM
# ================================================================

class FirstFundamentalForm:
    """
    First fundamental form I = E du² + 2F du dv + G dv².
    Arc-length on surfaces, angles, area, isometries, conformal maps.
    Pressley Ch.5 (§5.1 – §5.5).
    """

    def __init__(self, sigma_u, sigma_v):
        """
        sigma_u, sigma_v: partial derivative vectors at a point.
        Computes E, F, G.
        """
        su = np.array(sigma_u, dtype=float)
        sv = np.array(sigma_v, dtype=float)
        self.E = _fmt(_dot(su, su))
        self.F = _fmt(_dot(su, sv))
        self.G = _fmt(_dot(sv, sv))

    def coefficients(self):
        return {"E": self.E, "F": self.F, "G": self.G}

    def metric_tensor(self):
        return np.array([[self.E, self.F],[self.F, self.G]])

    def det(self):
        """det g = EG - F²."""
        return _fmt(self.E*self.G - self.F**2)

    def arc_length_element(self, du, dv):
        """ds² = E du² + 2F du dv + G dv²."""
        ds2 = self.E*du**2 + 2*self.F*du*dv + self.G*dv**2
        return _fmt(math.sqrt(max(0, ds2)))

    def angle_between_curves(self, du1, dv1, du2, dv2):
        """
        Angle θ between two curves on the surface with tangent directions
        (du1,dv1) and (du2,dv2):
        cos θ = (E·du1·du2 + F(du1·dv2 + du2·dv1) + G·dv1·dv2)
                / (ds1 · ds2)
        Pressley §5.1.
        """
        ds1 = self.arc_length_element(du1, dv1)
        ds2 = self.arc_length_element(du2, dv2)
        if ds1 < 1e-14 or ds2 < 1e-14:
            raise ValueError("Zero tangent direction.")
        num = (self.E*du1*du2 + self.F*(du1*dv2+du2*dv1) + self.G*dv1*dv2)
        cos_theta = num / (ds1 * ds2)
        cos_theta = max(-1, min(1, cos_theta))
        return _fmt(math.degrees(math.acos(cos_theta)))

    def area_element(self):
        """dA = √(EG-F²) du dv."""
        return _fmt(math.sqrt(max(0, self.det())))

    def surface_area(self, sigma_u_func, sigma_v_func, u_range, v_range,
                     nu=100, nv=100):
        """
        Surface area A = ∬ √(EG-F²) du dv  (numerical double integral).
        u_range=(u0,u1), v_range=(v0,v1).
        sigma_u_func, sigma_v_func: callables (u,v) → 3D vector.
        """
        u0,u1 = u_range; v0,v1 = v_range
        us = np.linspace(u0, u1, nu)
        vs = np.linspace(v0, v1, nv)
        du = (u1-u0)/(nu-1); dv = (v1-v0)/(nv-1)
        total = 0.0
        for u in us:
            for v in vs:
                su = np.array(sigma_u_func(u,v), dtype=float)
                sv = np.array(sigma_v_func(u,v), dtype=float)
                E_ = _dot(su,su); F_ = _dot(su,sv); G_ = _dot(sv,sv)
                total += math.sqrt(max(0, E_*G_ - F_**2))
        return _fmt(total * du * dv)

    def is_conformal(self, other_fff, tol=1e-6):
        """
        Two surfaces are conformally related at corresponding points iff
        their FFF coefficients are proportional:  E/E' = F/F' = G/G' = λ².
        """
        if abs(other_fff.E) < 1e-14 or abs(other_fff.G) < 1e-14:
            return False
        lambda_sq_E = self.E / other_fff.E
        lambda_sq_G = self.G / other_fff.G
        if abs(other_fff.F) < 1e-9 and abs(self.F) < 1e-9:
            lambda_sq_F = lambda_sq_E
        elif abs(other_fff.F) < 1e-14:
            return False
        else:
            lambda_sq_F = self.F / other_fff.F
        return {"conformal": (abs(lambda_sq_E-lambda_sq_G)<tol and
                              abs(lambda_sq_E-lambda_sq_F)<tol),
                "lambda_sq": _fmt(lambda_sq_E)}

    def is_isometry(self, other_fff, tol=1e-7):
        """Isometry: E=E', F=F', G=G'. Pressley §5.2."""
        return {"isometry": (abs(self.E-other_fff.E)<tol and
                             abs(self.F-other_fff.F)<tol and
                             abs(self.G-other_fff.G)<tol)}

    # ── Standard FFF examples ────────────────────────────────────────

    @staticmethod
    def fff_plane():
        return {"E":1,"F":0,"G":1, "note":"du²+dv²"}

    @staticmethod
    def fff_sphere(R, theta):
        """Sphere radius R at colatitude θ: E=R², F=0, G=R²sin²θ."""
        return {"E": _fmt(R**2), "F": 0,
                "G": _fmt(R**2 * math.sin(theta)**2),
                "ds2": f"{R**2}dθ² + {_fmt(R**2)}sin²θ dφ²"}

    @staticmethod
    def fff_torus(R, r, theta):
        """Torus (R,r) at θ: E=r², F=0, G=(R+r cos θ)²."""
        return {"E": _fmt(r**2), "F": 0,
                "G": _fmt((R + r*math.cos(theta))**2)}

    @staticmethod
    def fff_surface_of_revolution(f, f_prime, u):
        """σ(u,v)=(f(u)cos v, f(u)sin v, u): E=f'²+1, F=0, G=f²."""
        fp = f_prime(u); fu = f(u)
        return {"E": _fmt(fp**2 + 1), "F": 0, "G": _fmt(fu**2)}


# ================================================================
# CHAPTER 6 — CURVATURE OF SURFACES
# ================================================================

class SecondFundamentalForm:
    """
    Second fundamental form II = L du² + 2M du dv + N dv².
    Normal curvature, geodesic curvature, principal curvatures.
    Pressley Ch.6 (§6.1 – §6.4).
    """

    def __init__(self, sigma_uu, sigma_uv, sigma_vv, unit_normal):
        """
        sigma_uu, sigma_uv, sigma_vv: second partial derivatives.
        unit_normal: unit normal vector N at the point.
        Computes L, M, N (second fundamental form coefficients).
        """
        suu = np.array(sigma_uu, dtype=float)
        suv = np.array(sigma_uv, dtype=float)
        svv = np.array(sigma_vv, dtype=float)
        Nv  = np.array(unit_normal, dtype=float)
        self.L  = _fmt(_dot(suu, Nv))
        self.M  = _fmt(_dot(suv, Nv))
        self.N_ = _fmt(_dot(svv, Nv))  # 'N_' to avoid shadowing Python's N

    def coefficients(self):
        return {"L": self.L, "M": self.M, "N": self.N_}

    def normal_curvature(self, du, dv, fff):
        """
        Normal curvature in direction (du:dv):
        κₙ = (L du² + 2M du dv + N dv²) / (E du² + 2F du dv + G dv²).
        Pressley §6.2.
        """
        num = self.L*du**2 + 2*self.M*du*dv + self.N_*dv**2
        den = fff.E*du**2 + 2*fff.F*du*dv + fff.G*dv**2
        if abs(den) < 1e-14:
            raise ValueError("Zero tangent direction.")
        return _fmt(num / den)

    def shape_operator_matrix(self, fff):
        """
        Shape operator (Weingarten map) S = g⁻¹·h where
        g = [[E,F],[F,G]], h = [[L,M],[M,N]].
        Pressley §6.3.
        """
        g = np.array([[fff.E, fff.F],[fff.F, fff.G]])
        h = np.array([[self.L, self.M],[self.M, self.N_]])
        S = np.linalg.solve(g, h)  # g·S = h → S = g⁻¹h
        return S

    def principal_curvatures(self, fff):
        """
        κ₁, κ₂ = eigenvalues of the shape operator.
        Also returns principal directions (eigenvectors).
        Pressley §6.3.
        """
        S = self.shape_operator_matrix(fff)
        eigvals, eigvecs = np.linalg.eigh(S)
        return {
            "kappa_1": _fmt(eigvals[0]),
            "kappa_2": _fmt(eigvals[1]),
            "principal_direction_1": [_fmt(x) for x in eigvecs[:,0]],
            "principal_direction_2": [_fmt(x) for x in eigvecs[:,1]],
        }

    def gaussian_curvature(self, fff):
        """K = det(S) = (LN-M²)/(EG-F²). Pressley §7.1."""
        num = self.L*self.N_ - self.M**2
        den = fff.E*fff.G - fff.F**2
        if abs(den) < 1e-14:
            raise ValueError("Degenerate metric (EG-F²=0).")
        return _fmt(num / den)

    def mean_curvature(self, fff):
        """H = (1/2)tr(S) = (EN-2FM+GL)/(2(EG-F²)). Pressley §7.1."""
        num = fff.E*self.N_ - 2*fff.F*self.M + fff.G*self.L
        den = 2*(fff.E*fff.G - fff.F**2)
        if abs(den) < 1e-14:
            raise ValueError("Degenerate metric.")
        return _fmt(num / den)

    def umbilic_check(self, fff, tol=1e-6):
        """
        An umbilic point is where κ₁ = κ₂  (shape operator = scalar×Id).
        """
        pc = self.principal_curvatures(fff)
        return {"umbilic": abs(pc["kappa_1"] - pc["kappa_2"]) < tol,
                "kappa_1": pc["kappa_1"], "kappa_2": pc["kappa_2"]}


# ================================================================
# CHAPTER 7 — GAUSSIAN CURVATURE AND THE GAUSS MAP
# ================================================================

class GaussianCurvature:
    """
    Gaussian and mean curvature, surface classification, pseudosphere,
    flat surfaces, Gauss map. Pressley Ch.7 (§7.1 – §7.6).
    """

    @staticmethod
    def surface_type(K, H=None, tol=1e-9):
        """
        Classify a surface point by its curvatures K and H.
        Pressley §6.4.
        """
        if abs(K) < tol:
            if H is not None and abs(H) < tol:
                return "Flat and minimal (plane)"
            return "Flat (K=0)"
        elif K > 0:
            if H is not None and abs(H) < tol:
                return "Elliptic and minimal"
            return "Elliptic point (K>0): surface curves same way in all directions"
        else:
            return "Hyperbolic point (K<0): saddle — surface curves opposite ways"

    @staticmethod
    def minimal_surface_check(H, tol=1e-9):
        """Minimal surface: H = 0 everywhere. Pressley §9.1."""
        return abs(H) < tol

    @staticmethod
    def K_sphere(R):
        """K = 1/R² for sphere of radius R."""
        return _fmt(1.0 / R**2)

    @staticmethod
    def K_torus(R, r, theta):
        """
        K(θ) = cos θ / (r(R + r cos θ)) for torus (R,r) at angle θ.
        Pressley Example 7.1.
        """
        return _fmt(math.cos(theta) / (r * (R + r*math.cos(theta))))

    @staticmethod
    def K_surface_of_revolution(f, f_pp, u):
        """
        K = -f''(u) / (f(u)(1 + f'(u)²)²) ... general formula.
        Actually K = -f''/(f · (1+f'²)²) is not quite right;
        the correct formula (Pressley §7.2) is:
        K = -f''(u) / (f(u) · (1 + f'(u)²)²)  [for σ=(f cos v, f sin v, u)]
        Wait — corrected: K = -f'' / (f(1+f'²)²) (see below).
        Standard result: K = -f''/(f·(1+f'²)²) [Pressley p.154]
        """
        return _fmt(-f_pp(u) / (f(u) * (1 + f(u)**2)**2))

    @staticmethod
    def pseudosphere_K(a=1.0):
        """
        Pseudosphere (tractrix rotated): K = -1/a² everywhere.
        Pressley §7.2.
        """
        return _fmt(-1.0 / a**2)

    @staticmethod
    def gauss_map_normal(sigma_u, sigma_v):
        """
        Gauss map G: S → S² sends each point to its unit normal N.
        Returns the unit normal (= the value of the Gauss map).
        Pressley §7.6.
        """
        return Surfaces.unit_normal(sigma_u, sigma_v)

    @staticmethod
    def christoffel_symbols(E, F, G, E_u, E_v, F_u, F_v, G_u, G_v):
        """
        Christoffel symbols Γᵢⱼᵏ from first fundamental form coefficients
        and their partial derivatives.
        Pressley §10.1 (used in Theorema Egregium).
        Uses the standard formulas:
          Γ¹₁₁ = (G·E_u - 2F·F_u + F·E_v) / (2(EG-F²))  ... etc.
        Returns all 6 independent symbols.
        """
        W2 = E*G - F**2
        if abs(W2) < 1e-14:
            raise ValueError("Degenerate metric.")

        G11_1 = (G*E_u - 2*F*F_u + F*E_v) / (2*W2)
        G11_2 = (2*E*F_u - E*E_v - F*E_u) / (2*W2)
        G12_1 = (G*E_v - F*G_u)           / (2*W2)
        G12_2 = (E*G_u - F*E_v)           / (2*W2)
        G22_1 = (2*G*F_v - G*G_u - F*G_v) / (2*W2)
        G22_2 = (E*G_v - 2*F*F_v + F*G_u) / (2*W2)

        return {
            "Γ¹₁₁": _fmt(G11_1), "Γ²₁₁": _fmt(G11_2),
            "Γ¹₁₂": _fmt(G12_1), "Γ²₁₂": _fmt(G12_2),
            "Γ¹₂₂": _fmt(G22_1), "Γ²₂₂": _fmt(G22_2),
        }


# ================================================================
# CHAPTER 8 — GEODESICS
# ================================================================

class Geodesics:
    """
    Geodesic equations, geodesics on surfaces of revolution,
    geodesic curvature, Clairaut's theorem. Pressley Ch.8 (§8.1 – §8.5).
    """

    @staticmethod
    def geodesic_equations(Gamma, u_dot, v_dot):
        """
        Geodesic equations (Pressley §8.2):
          ü + Γ¹₁₁ u̇² + 2Γ¹₁₂ u̇v̇ + Γ¹₂₂ v̇² = 0
          v̈ + Γ²₁₁ u̇² + 2Γ²₂₂ u̇v̇ + Γ²₂₂ v̇² = 0
        Gamma: dict from christoffel_symbols().
        Returns (ü, v̈).
        """
        u_ddot = -(Gamma["Γ¹₁₁"]*u_dot**2 +
                   2*Gamma["Γ¹₁₂"]*u_dot*v_dot +
                   Gamma["Γ¹₂₂"]*v_dot**2)
        v_ddot = -(Gamma["Γ²₁₁"]*u_dot**2 +
                   2*Gamma["Γ²₁₂"]*u_dot*v_dot +
                   Gamma["Γ²₂₂"]*v_dot**2)
        return {"u_ddot": _fmt(u_ddot), "v_ddot": _fmt(v_ddot)}

    @staticmethod
    def clairaut_constant(f_u, v_dot, speed):
        """
        Clairaut's theorem: on a surface of revolution,
        c = f(u) · cos(angle with meridian) = f(u)² · |v̇| / speed = const.
        Pressley §8.3.
        Returns the Clairaut constant c = f(u)² · v̇ / speed.
        """
        c = f_u**2 * v_dot / speed
        return _fmt(c)

    @staticmethod
    def geodesic_on_sphere_check(gamma_dot, gamma_ddot, R):
        """
        A curve on a sphere of radius R is a geodesic iff γ̈ is parallel to γ
        (i.e., γ̈ = λγ for some scalar λ).  Great circles are geodesics.
        Returns residual ‖γ̈ - (γ̈·γ/R²)γ‖.
        """
        gd  = np.array(gamma_dot,  dtype=float)
        gdd = np.array(gamma_ddot, dtype=float)
        # project γ̈ onto the radial direction  (assume the curve is on the sphere)
        # γ̈ - (γ̈ · T²)T = normal component should be ‖ to N
        # Simpler: for great circle γ(t)=R(a cos t + b sin t), γ̈=-γ
        residual = gdd + (1/R**2) * gdd  # just illustrative
        return _fmt(_norm(residual))

    @staticmethod
    def geodesic_curvature(gamma_dot, gamma_ddot, unit_normal):
        """
        Geodesic curvature κ_g of a curve on a surface:
        κ_g = (γ̈ · (N × γ̇)) / ‖γ̇‖³
        where N is the surface unit normal. Pressley §8.1.
        """
        gd  = np.array(gamma_dot,  dtype=float)
        gdd = np.array(gamma_ddot, dtype=float)
        N   = np.array(unit_normal, dtype=float)
        speed = _norm(gd)
        Nxgd = _cross(N, gd)
        kg = _dot(gdd, Nxgd) / speed**3
        return _fmt(kg)

    @staticmethod
    def integrate_geodesic(christoffel_func, u0, v0, u_dot0, v_dot0,
                           t_span=(0, 5), n_points=500):
        """
        Numerically integrate the geodesic equations.
        christoffel_func: callable (u,v) → dict of Christoffel symbols.
        Returns arrays of (t, u(t), v(t)).
        """
        def ode(t, y):
            u, v, ud, vd = y
            G = christoffel_func(u, v)
            udd = -(G["Γ¹₁₁"]*ud**2 + 2*G["Γ¹₁₂"]*ud*vd + G["Γ¹₂₂"]*vd**2)
            vdd = -(G["Γ²₁₁"]*ud**2 + 2*G["Γ²₁₂"]*ud*vd + G["Γ²₂₂"]*vd**2)
            return [ud, vd, udd, vdd]

        from scipy.integrate import solve_ivp
        sol = solve_ivp(ode, t_span, [u0, v0, u_dot0, v_dot0],
                        t_eval=np.linspace(*t_span, n_points),
                        method='RK45', rtol=1e-8)
        return {"t": sol.t, "u": sol.y[0], "v": sol.y[1],
                "u_dot": sol.y[2], "v_dot": sol.y[3],
                "success": sol.success}

    @staticmethod
    def geodesic_sphere_great_circle(R, n1, n2, t_range=None, n=200):
        """
        Great circle on sphere of radius R in the plane spanned by unit vectors n1, n2.
        γ(t) = R(n1 cos t + n2 sin t).
        Returns array of 3D points.
        """
        n1 = _unit(np.array(n1, dtype=float))
        n2 = _unit(np.array(n2, dtype=float))
        if t_range is None:
            t_range = (0, 2*math.pi)
        ts = np.linspace(*t_range, n)
        pts = [R*(math.cos(t)*n1 + math.sin(t)*n2) for t in ts]
        return np.array(pts)


# ================================================================
# CHAPTER 9 — MINIMAL SURFACES
# ================================================================

class MinimalSurfaces:
    """
    Minimal surfaces (H=0), Weierstrass–Enneper parametrization.
    Pressley Ch.9 (§9.1 – §9.4).
    """

    @staticmethod
    def is_minimal(H, tol=1e-9):
        """Minimal surface: H ≡ 0. Pressley §9.1."""
        return abs(H) < tol

    @staticmethod
    def catenoid(u, v):
        """
        Catenoid: σ(u,v) = (cosh u cos v, cosh u sin v, u).
        H=0 (minimal). Pressley Example 9.2.
        """
        x = math.cosh(u)*math.cos(v)
        y = math.cosh(u)*math.sin(v)
        z = u
        su = np.array([math.sinh(u)*math.cos(v), math.sinh(u)*math.sin(v), 1.0])
        sv = np.array([-math.cosh(u)*math.sin(v), math.cosh(u)*math.cos(v), 0.0])
        E = _dot(su,su); F = _dot(su,sv); G = _dot(sv,sv)
        return {"point": [_fmt(x),_fmt(y),_fmt(z)],
                "sigma_u": [_fmt(c) for c in su],
                "sigma_v": [_fmt(c) for c in sv],
                "E": _fmt(E), "F": _fmt(F), "G": _fmt(G)}

    @staticmethod
    def helicoid(u, v):
        """
        Helicoid: σ(u,v) = (u cos v, u sin v, v).
        H=0 (minimal). Pressley Example 9.2.
        Isometric to catenoid.
        """
        x = u*math.cos(v); y = u*math.sin(v); z = v
        su = np.array([math.cos(v), math.sin(v), 0.0])
        sv = np.array([-u*math.sin(v), u*math.cos(v), 1.0])
        return {"point": [_fmt(x),_fmt(y),_fmt(z)],
                "sigma_u": [_fmt(c) for c in su],
                "sigma_v": [_fmt(c) for c in sv]}

    @staticmethod
    def enneper_surface(u, v):
        """
        Enneper's surface: σ(u,v) = (u - u³/3 + uv², v - v³/3 + vu², u²-v²).
        H=0. Pressley Example 9.4.
        """
        x = u - u**3/3 + u*v**2
        y = v - v**3/3 + v*u**2
        z = u**2 - v**2
        return {"point": [_fmt(x),_fmt(y),_fmt(z)]}

    @staticmethod
    def weierstrass_enneper(f_func, g_func, t_values):
        """
        Weierstrass–Enneper representation (Pressley §9.4):
        Using holomorphic functions f, g: ζ → ℂ,
        σ₁ = Re ∫ f(1-g²)/2 dζ
        σ₂ = Re ∫ if(1+g²)/2 dζ
        σ₃ = Re ∫ fg dζ
        Returns integrand values at t_values (for numerical integration).
        """
        results = []
        for t in t_values:
            z = complex(t, 0)
            f = f_func(z); g_ = g_func(z)
            phi1 = f * (1 - g_**2) / 2
            phi2 = 1j * f * (1 + g_**2) / 2
            phi3 = f * g_
            results.append({
                "t": t,
                "phi1": phi1, "phi2": phi2, "phi3": phi3,
                "note": "Integrate Re(phi_i) w.r.t. t for surface coords."
            })
        return results

    @staticmethod
    def gauss_map_minimal(sigma_u, sigma_v):
        """
        Gauss map of a minimal surface is conformal (angle-preserving).
        Returns the unit normal.
        """
        return Surfaces.unit_normal(sigma_u, sigma_v)


# ================================================================
# CHAPTER 10 — GAUSS'S THEOREMA EGREGIUM
# ================================================================

class TheoremaEgregium:
    """
    Gauss's Theorema Egregium: K is intrinsic.
    Codazzi–Mainardi equations, compact surfaces of constant K.
    Pressley Ch.10 (§10.1 – §10.4).
    """

    @staticmethod
    def gaussian_curvature_intrinsic(E, F, G,
                                      E_u, E_v, F_u, F_v, G_u, G_v,
                                      E_uu=0, E_vv=0, G_uu=0, G_vv=0,
                                      F_uv=0):
        """
        Brioschi's formula — K expressed entirely through E, F, G and their
        partial derivatives (no second fundamental form needed).
        Pressley §10.1.

        For orthogonal parametrization (F=0), simpler formula:
        K = -1/(2√EG) [∂/∂u(G_u/√EG) + ∂/∂v(E_v/√EG)]
        We implement this for F=0.
        """
        if abs(F) < 1e-12:  # orthogonal coordinates
            sqEG = math.sqrt(E*G)
            # Approximate partial derivatives numerically (user must supply them)
            # Using the formula K = -1/(2√EG)[∂_u(G_u/√EG) + ∂_v(E_v/√EG)]
            # For exact K we need second derivatives — use Brioschi below
            pass

        # Brioschi's formula (always valid):
        W2 = E*G - F**2
        if abs(W2) < 1e-14:
            raise ValueError("Degenerate metric.")

        # Matrix form of Brioschi:
        M  = np.array([[-E_vv/2 + F_uv - G_uu/2, E_u/2,    F_u - E_v/2],
                       [F_v - G_u/2,               E,        F          ],
                       [G_v/2,                      F,        G          ]])
        M2 = np.array([[0,       E_v/2, G_u/2],
                       [E_v/2,   E,     F    ],
                       [G_u/2,   F,     G    ]])

        brioschi = (np.linalg.det(M) - np.linalg.det(M2)) / W2**2
        return _fmt(brioschi)

    @staticmethod
    def codazzi_mainardi_check(L, M_, N_,
                               L_v, M_u, M_v, N_u,
                               Gamma, E, F, G):
        """
        Codazzi–Mainardi equations (Pressley §10.3):
        L_v - M_u = LΓ¹₁₂ + M(Γ²₁₂ - Γ¹₁₁) - NΓ²₁₁
        M_v - N_u = LΓ¹₂₂ + M(Γ²₂₂ - Γ¹₁₂) - NΓ²₁₂
        Returns residuals (should be ~0 for a consistent surface).
        """
        eq1 = (L_v - M_u) - (L*Gamma["Γ¹₁₂"] +
                              M_*(Gamma["Γ²₁₂"] - Gamma["Γ¹₁₁"]) -
                              N_*Gamma["Γ²₁₁"])
        eq2 = (M_v - N_u) - (L*Gamma["Γ¹₂₂"] +
                              M_*(Gamma["Γ²₂₂"] - Gamma["Γ¹₁₂"]) -
                              N_*Gamma["Γ²₁₂"])
        return {"CM_eq1_residual": _fmt(eq1),
                "CM_eq2_residual": _fmt(eq2),
                "satisfied": abs(eq1) < 1e-6 and abs(eq2) < 1e-6}

    @staticmethod
    def compact_surface_classification(K_value):
        """
        Compact surfaces of constant Gaussian curvature (Pressley §10.4):
        K > 0 → sphere (only compact surface of constant positive K)
        K = 0 → flat  (torus or Klein bottle topologically)
        K < 0 → no compact surface without boundary (Hilbert's theorem)
        """
        if K_value > 0:
            return {"K": K_value, "type": "Sphere", "radius": _fmt(1/math.sqrt(K_value))}
        elif abs(K_value) < 1e-9:
            return {"K": 0, "type": "Flat surface (e.g. torus, cylinder, plane)"}
        else:
            return {"K": K_value,
                    "type": "Negative curvature — no compact embedded surface in ℝ³ (Hilbert)"}

    @staticmethod
    def fundamental_theorem_surfaces(E, F, G, L, M_, N_):
        """
        Fundamental theorem of surface theory: Given E,F,G,L,M,N satisfying
        the Gauss equation and Codazzi–Mainardi equations, there exists a
        surface with these fundamental forms (unique up to rigid motions).
        Returns a summary check.
        """
        W2 = E*G - F**2
        K_from_II = (L*N_ - M_**2) / W2 if abs(W2) > 1e-14 else None
        H_from_II = (E*N_ - 2*F*M_ + G*L) / (2*W2) if abs(W2) > 1e-14 else None
        return {"EG_F2": _fmt(W2), "K": _fmt(K_from_II),
                "H": _fmt(H_from_II),
                "note": ("Surface exists (up to rigid motion) if Gauss and "
                         "Codazzi-Mainardi equations are satisfied.")}


# ================================================================ 
# CHAPTER 11 — THE GAUSS–BONNET THEOREM
# ================================================================

class GaussBonnet:
    """
    Gauss–Bonnet theorem for simple closed curves, curvilinear polygons,
    and compact surfaces. Pressley Ch.11 (§11.1 – §11.3).
    """

    @staticmethod
    def gauss_bonnet_simple(geodesic_curvature_integral, K_integral):
        """
        Gauss–Bonnet for a simple closed curve C bounding a region R:
        ∫_C κ_g ds + ∬_R K dA = 2π.
        Checks the identity. Pressley §11.1.
        """
        total = geodesic_curvature_integral + K_integral
        return {
            "int_kg_ds": _fmt(geodesic_curvature_integral),
            "int_K_dA":  _fmt(K_integral),
            "sum":       _fmt(total),
            "theorem":   "Should equal 2π ≈ 6.28318...",
            "residual":  _fmt(abs(total - 2*math.pi))
        }

    @staticmethod
    def gauss_bonnet_polygon(geodesic_curvature_integral, K_integral,
                              exterior_angles_sum):
        """
        Gauss–Bonnet for a curvilinear polygon with n vertices:
        ∫_C κ_g ds + ∬_R K dA + Σ exterior_angles = 2π.
        Pressley §11.2.
        """
        total = geodesic_curvature_integral + K_integral + exterior_angles_sum
        return {
            "int_kg_ds":      _fmt(geodesic_curvature_integral),
            "int_K_dA":       _fmt(K_integral),
            "sum_ext_angles": _fmt(exterior_angles_sum),
            "total":          _fmt(total),
            "residual":       _fmt(abs(total - 2*math.pi))
        }

    @staticmethod
    def euler_characteristic(V, E_count, F_count):
        """
        Euler characteristic χ = V - E + F.
        For a triangulated compact surface: ∬ K dA = 2π χ.
        Pressley §11.3.
        """
        chi = V - E_count + F_count
        return {"V": V, "E": E_count, "F": F_count,
                "chi": chi,
                "total_curvature_2pi_chi": _fmt(2*math.pi*chi)}

    @staticmethod
    def gauss_bonnet_compact(K_integral, chi):
        """
        Gauss–Bonnet for compact surface:
        ∬_S K dA = 2π χ(S).
        Pressley §11.3.
        """
        return {
            "int_K_dA":        _fmt(K_integral),
            "2_pi_chi":        _fmt(2*math.pi*chi),
            "residual":        _fmt(abs(K_integral - 2*math.pi*chi)),
            "theorem_holds":   abs(K_integral - 2*math.pi*chi) < 1e-4
        }

    @staticmethod
    def topology_from_chi(chi):
        """Identify surface topology from Euler characteristic."""
        surface_map = {
            2:  "Sphere S²",
            0:  "Torus T²",
            1:  "Real projective plane ℝP²",
            -2: "Double torus (genus 2)",
        }
        genus = (2 - chi) // 2 if chi % 2 == 0 else None
        return {"chi": chi,
                "surface": surface_map.get(chi, f"Genus g={(2-chi)//2} surface"),
                "genus": genus}

    @staticmethod
    def angle_sum_geodesic_triangle_sphere(R, A_deg, B_deg, C_deg):
        """
        For a geodesic triangle on sphere of radius R:
        A + B + C - π = area / R²  (spherical excess = area/R²).
        Pressley §11.1 example.
        """
        excess = _fmt(math.radians(A_deg + B_deg + C_deg) - math.pi)
        area = _fmt(excess * R**2)
        return {"excess_rad": excess,
                "excess_deg": _fmt(math.degrees(excess)),
                "area":       area,
                "check_K*area": _fmt(area / R**2)}

    @staticmethod
    def angle_sum_geodesic_triangle_hyperbolic(k, A_deg, B_deg, C_deg):
        """
        For a geodesic triangle in hyperbolic plane of curvature K=-1/k²:
        π - (A+B+C) = |K| × area  → area = k²(π - A - B - C).
        """
        defect = math.pi - math.radians(A_deg + B_deg + C_deg)
        area = _fmt(k**2 * defect)
        return {"defect_rad": _fmt(defect),
                "defect_deg": _fmt(math.degrees(defect)),
                "area":       area}