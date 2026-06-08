"""
 ═════════════════════════════════════════════════════════════════
    TOPOLOGY OF SURFACES ENGINE                                                                              ║
 ═════════════════════════════════════════════════════════════════

Chapter map:
    1 : Overview — (topological equivalence, deformation, key ideas)

    2 : PointSetRn — (open/closed sets, interior/frontier/closure, compactness, connectedness in ℝⁿ)

    3 : PointSetTopology — (abstract topological spaces, continuity, separation axioms, product & quotient spaces)

    4 : Surfaces — (CW complexes, triangulations, classification of compact surfaces, surfaces with boundary)

    5 : EulerChar — (Euler characteristic, graphs/trees, surfaces, map-colouring problems)

    6 : Homology — (chain groups, boundary operator, cycles, boundaries, homology groups, Betti numbers)

    7 : CellularFns — (cellular functions, induced homomorphisms, covering spaces, degree of a map)

    8 : HomologyInv — (invariance of homology, simplicial approximation)

    9 : Homotopy — (homotopy equivalence, deformation retracts, fundamental group π₁)

    10 : Miscellany — (applications (Brouwer, Borsuk-Ulam, ham sandwich), Jordan curve theorem, 3-manifolds)

    11 : TopoCalculus — (vector fields in ℝⁿ, differentiable manifolds, vector fields on manifolds, integration, degree)

App   : Groups            — (group theory appendix: abelian groups, free groups, presentations, quotient groups)
Usage:
    python topology_of_surfaces_engine.py      
    import topology_of_surfaces_engine as ts   
"""

import math
import itertools
from collections import defaultdict, deque
from fractions import Fraction


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _sign(x):
    if x > 0: return 1
    if x < 0: return -1
    return 0

def _gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a

def _lcm(a, b):
    return abs(a * b) // _gcd(a, b)

def _mod_reduce(n, m):
    """Reduce integer n modulo m (0 if m==0 means ℤ)."""
    if m == 0:
        return n
    return n % m


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 1 — INTRODUCTION TO TOPOLOGY
# ─────────────────────────────────────────────────────────────────────────────

class Overview:
    """
    Key ideas and catalogue of surfaces. Kinsey Ch.1 §1.1.
    """

    SURFACES_CATALOGUE = {
        "Sphere S²":            {"genus": 0, "orientable": True,  "chi": 2,  "boundary": False},
        "Torus T²":             {"genus": 1, "orientable": True,  "chi": 0,  "boundary": False},
        "Double torus g=2":     {"genus": 2, "orientable": True,  "chi": -2, "boundary": False},
        "g-holed torus":        {"genus": "g","orientable": True,  "chi": "2-2g","boundary": False},
        "Projective plane ℝP²": {"genus": 1, "orientable": False, "chi": 1,  "boundary": False},
        "Klein bottle K":       {"genus": 2, "orientable": False, "chi": 0,  "boundary": False},
        "Disk D²":              {"genus": 0, "orientable": True,  "chi": 1,  "boundary": True},
        "Annulus":              {"genus": 1, "orientable": True,  "chi": 0,  "boundary": True},
        "Möbius band":          {"genus": 1, "orientable": False, "chi": 0,  "boundary": True},
    }

    TOPOLOGICAL_INVARIANTS = [
        "Euler characteristic χ",
        "Orientability (orientable / non-orientable)",
        "Number of boundary components",
        "Genus g (number of handles / crosscaps)",
        "Homology groups H₀, H₁, H₂, ...",
        "Fundamental group π₁",
        "Betti numbers β₀, β₁, β₂, ...",
    ]

    @classmethod
    def surface_info(cls, name):
        return cls.SURFACES_CATALOGUE.get(name, "Surface not in catalogue.")

    @classmethod
    def topological_equivalence_note(cls):
        return {
            "definition": ("Two spaces X and Y are topologically equivalent "
                           "(homeomorphic) if there is a bicontinuous bijection f: X → Y."),
            "intuition":  ("Deformations that are allowed: stretching, bending, twisting. "
                           "NOT allowed: cutting, tearing, gluing new points."),
            "key_theorem": ("Classification of compact surfaces: every compact surface "
                            "is homeomorphic to exactly one of: Sⁿ_g (orientable, genus g) "
                            "or N_k (non-orientable, k crosscaps). Kinsey §4.4.")
        }


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 2 — POINT-SET TOPOLOGY IN ℝⁿ
# ─────────────────────────────────────────────────────────────────────────────

class PointSetRn:
    """
    Open/closed sets, neighbourhoods, interior, closure, frontier, boundary,
    compactness, connectedness in ℝⁿ.  Kinsey Ch.2 §2.1–§2.6.
    """

    @staticmethod
    def open_ball(centre, radius, point):
        """Check if point is in the open ball B(centre, radius) in ℝⁿ."""
        dist = math.sqrt(sum((p - c)**2 for p, c in zip(point, centre)))
        return {"in_ball": dist < radius, "distance": round(dist, 10)}

    @staticmethod
    def is_interior_point_box(point, a, b):
        """
        Is 'point' an interior point of the open box (a, b)^n?
        Each coordinate must satisfy aᵢ < xᵢ < bᵢ.
        """
        return all(a < x < b for x in point)

    @staticmethod
    def closure_interval(a, b, closed_left=True, closed_right=True):
        """
        Closure of an interval in ℝ: closure of (a,b), [a,b), (a,b], [a,b] is [a,b].
        """
        return {"closure": f"[{a}, {b}]",
                "interior": f"({a}, {b})",
                "frontier": f"{{{a}, {b}}}"}

    @staticmethod
    def is_compact_box(a, b, closed=True):
        """
        In ℝⁿ: [a,b]ⁿ is compact (closed & bounded). (a,b)ⁿ is not.
        Heine-Borel: compact ↔ closed and bounded in ℝⁿ.
        """
        return {"compact": closed,
                "reason": "Closed and bounded ↔ compact in ℝⁿ (Heine-Borel)"}

    @staticmethod
    def connected_check_interval(a, b):
        """
        An interval [a,b] (or (a,b)) in ℝ is connected. ℝⁿ is connected.
        A set with a gap (e.g. [0,1] ∪ [2,3]) is not.
        """
        return {"connected": True,
                "reason": "Intervals are connected in ℝ (intermediate value theorem)."}

    @staticmethod
    def path_connected(space_description):
        """
        A path-connected space is connected. Converse fails in general.
        Kinsey §2.5.
        """
        examples = {
            "ℝⁿ":        True,
            "Sⁿ":        True,
            "torus":     True,
            "letters_X": True,
            "letters_C": True,
            "letters_S": True,
            "two_circles_apart": False,
        }
        return {"path_connected": examples.get(space_description, "Unknown"),
                "note": "Path-connected ⟹ connected, but not conversely."}

    @staticmethod
    def continuous_function_check(f_description, domain, codomain):
        """
        A function f: X→Y is continuous iff the preimage of every open set is open.
        Returns the topological definition.
        """
        return {
            "definition": ("f: X→Y is continuous iff for every open U ⊆ Y, "
                           "f⁻¹(U) is open in X."),
            "equivalent": ("f is continuous at x iff: for every ε>0 there exists δ>0 "
                           "such that d(x,y)<δ ⟹ d(f(x),f(y))<ε (in metric spaces)."),
            "homeomorphism": ("f is a homeomorphism if it is bijective, continuous, "
                              "and has a continuous inverse.")
        }

    @staticmethod
    def winding_number_vector_field_2d(path_points):
        """
        Winding number (index) of a closed path in ℝ² about the origin.
        Uses the signed angle sum: n = (total angle change) / (2π).
        path_points: list of (x,y) points forming a closed loop.
        """
        n = len(path_points)
        total_angle = 0.0
        for i in range(n):
            x1, y1 = path_points[i]
            x2, y2 = path_points[(i + 1) % n]
            angle = math.atan2(y2, x2) - math.atan2(y1, x1)
            # normalise to (-π, π]
            while angle > math.pi:  angle -= 2*math.pi
            while angle <= -math.pi: angle += 2*math.pi
            total_angle += angle
        winding = total_angle / (2 * math.pi)
        return {"winding_number": round(winding), "raw": round(total_angle, 8)}


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 3 — POINT-SET TOPOLOGY (ABSTRACT)
# ─────────────────────────────────────────────────────────────────────────────

class PointSetTopology:
    """
    Abstract topological spaces, separation axioms, product and quotient topologies.
    Kinsey Ch.3 §3.1–§3.5.
    """

    @staticmethod
    def is_topology(X, open_sets):
        """
        Verify that a collection of subsets forms a topology on X.
        Conditions (Kinsey §3.1):
          (T1) ∅ and X are in the collection.
          (T2) Arbitrary unions of open sets are open.
          (T3) Finite intersections of open sets are open.
        X: frozenset of elements; open_sets: list of frozensets.
        """
        X = frozenset(X)
        ops = [frozenset(s) for s in open_sets]

        t1 = (frozenset() in ops) and (X in ops)

        # Check finite intersections of all pairs
        t3 = True
        for a, b in itertools.combinations(ops, 2):
            inter = a & b
            if inter not in ops:
                t3 = False
                break

        # Check unions (just pairs for finite check)
        t2 = True
        for a, b in itertools.combinations(ops, 2):
            union = a | b
            if union not in ops:
                t2 = False
                break

        return {"is_topology": t1 and t2 and t3,
                "T1_empty_and_X": t1, "T2_unions": t2, "T3_intersections": t3}

    @staticmethod
    def separation_axioms(space_type):
        """
        Classification by separation axioms. Kinsey §3.3.
        """
        axioms = {
            "T0 (Kolmogorov)":  "For any two points, at least one has a neighbourhood not containing the other.",
            "T1 (Fréchet)":     "For any two points, each has a neighbourhood not containing the other. Points are closed.",
            "T2 (Hausdorff)":   "Any two distinct points have disjoint neighbourhoods. Most spaces in practice.",
            "T3 (Regular)":     "T1 + closed set and outside point can be separated by open sets.",
            "T4 (Normal)":      "T1 + any two disjoint closed sets have disjoint open neighbourhoods (Urysohn).",
        }
        return axioms.get(space_type, {k: v for k, v in axioms.items()})

    @staticmethod
    def product_topology(X_basis, Y_basis):
        """
        Product topology on X × Y: basis = {U × V : U open in X, V open in Y}.
        Returns sample basis elements. Kinsey §3.4.
        """
        basis = [(u, v) for u in X_basis for v in Y_basis]
        return {
            "basis_elements": basis[:10],
            "note": ("The product topology is the coarsest topology making "
                     "both projections π_X and π_Y continuous.")
        }

    @staticmethod
    def quotient_space(X, equivalence_classes):
        """
        Quotient space X/~ where ~ is the equivalence relation given by
        the partition (list of equivalence classes).
        Returns the equivalence class representative for each point.
        Kinsey §3.5.
        """
        point_to_class = {}
        for cls_idx, cls in enumerate(equivalence_classes):
            for pt in cls:
                point_to_class[pt] = cls_idx
        return {
            "num_classes":         len(equivalence_classes),
            "point_to_class":      point_to_class,
            "quotient_elements":   list(range(len(equivalence_classes))),
            "note": ("The quotient topology: U ⊆ X/~ is open iff "
                     "q⁻¹(U) is open in X, where q is the quotient map.")
        }

    @staticmethod
    def cone(X_points):
        """
        Cone CX = (X × [0,1]) / (X × {1}).
        All points at level 1 are identified to the apex.
        Returns the apex and a description.
        """
        return {
            "apex": "* (all of X×{1} collapsed)",
            "levels": "X×{t} for 0 ≤ t < 1",
            "note": "CX is contractible for any X."
        }

    @staticmethod
    def suspension(X_description):
        """
        Suspension SX = (X × [-1,1]) / (X×{-1} ~ n, X×{1} ~ s).
        Kinsey §3.5 example.
        """
        suspensions = {
            "S⁰": "S¹ (circle)",
            "S¹": "S² (sphere)",
            "S²": "S³",
            "Sⁿ": "Sⁿ⁺¹",
        }
        return {
            "suspension_of": X_description,
            "result": suspensions.get(X_description, f"S({X_description})"),
            "note": "Suspension adds two cone points (north and south poles)."
        }


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 4 — SURFACES
# ─────────────────────────────────────────────────────────────────────────────

class Surfaces:
    """
    CW complexes, triangulations, classification of compact surfaces,
    surfaces with boundary. Kinsey Ch.4 §4.1–§4.5.
    """

    @staticmethod
    def cw_complex_skeleton(cells_by_dimension):
        """
        CW complex: cells_by_dimension = {0: n0, 1: n1, 2: n2, ...}
        where nk = number of k-cells.
        Kinsey §4.1.
        Returns skeleton info and Euler characteristic.
        """
        chi = sum((-1)**k * n for k, n in cells_by_dimension.items())
        return {
            "cells": cells_by_dimension,
            "euler_characteristic": chi,
            "k_skeletons": {k: f"Union of all cells of dimension ≤ {k}" 
                            for k in cells_by_dimension}
        }

    @staticmethod
    def triangulation_check(V, E, F, surface="closed"):
        """
        Check a triangulation of a surface:
        - Every edge belongs to exactly 2 triangles (closed surface).
        - Every vertex neighbourhood is a disc (closed).
        Kinsey §4.3.
        Returns Euler characteristic and basic checks.
        """
        chi = V - E + F
        edge_face_ratio = 3 * F  # each face has 3 edges, each edge shared by 2
        # For a closed triangulated surface: 3F = 2E
        t1 = (3 * F == 2 * E) if surface == "closed" else True
        return {
            "V": V, "E": E, "F": F,
            "chi": chi,
            "3F=2E_check": t1,
            "note": "3F = 2E must hold for a closed triangulated surface."
        }

    @staticmethod
    def classify_surface(chi, orientable, boundary_components=0):
        """
        Classification theorem for compact surfaces (Kinsey §4.4):
        Orientable:     S_g with χ = 2 − 2g (g handles)
        Non-orientable: N_k with χ = 2 − k  (k crosscaps)
        Boundary:       reduces χ by b (b boundary circles, each a copy of S¹).
        """
        if boundary_components > 0:
            chi_closed = chi + boundary_components
        else:
            chi_closed = chi

        if orientable:
            g = (2 - chi_closed) // 2
            if (2 - chi_closed) % 2 != 0:
                return {"error": "χ not of form 2-2g for orientable surface."}
            names = {0: "Sphere S²", 1: "Torus T²", 2: "Double torus"}
            name = names.get(g, f"Orientable surface of genus {g}")
            return {
                "surface": name,
                "genus": g,
                "orientable": True,
                "chi": chi,
                "boundary_components": boundary_components,
                "standard_form": f"S_{g}" if g > 0 else "S²"
            }
        else:
            k = 2 - chi_closed
            if k < 1:
                return {"error": "Non-orientable surface needs k ≥ 1 crosscaps."}
            names = {1: "Projective plane ℝP²", 2: "Klein bottle K",
                     3: "N₃ (connected sum ℝP²#T²)"}
            return {
                "surface": names.get(k, f"Non-orientable surface with {k} crosscaps"),
                "crosscaps": k,
                "orientable": False,
                "chi": chi,
                "boundary_components": boundary_components,
                "standard_form": f"N_{k}"
            }

    @staticmethod
    def connected_sum(surface1, surface2):
        """
        Connected sum S₁ # S₂:
        χ(S₁ # S₂) = χ(S₁) + χ(S₂) − 2.
        Orientability: orientable iff both are orientable (with exceptions for RP²).
        Kinsey §4.4.
        """
        chi1 = surface1.get("chi", 0)
        chi2 = surface2.get("chi", 0)
        chi_sum = chi1 + chi2 - 2
        orientable = surface1.get("orientable", True) and surface2.get("orientable", True)
        result = classify_surface_chi(chi_sum, orientable)
        return {
            "chi": chi_sum,
            "orientable": orientable,
            "surface": result,
            "formula": "χ(S₁ # S₂) = χ(S₁) + χ(S₂) − 2"
        }

    @staticmethod
    def polygon_word_to_surface(word):
        """
        Identify the surface given by its polygon identification word.
        Kinsey §4.4 polygon representations:
          "aa⁻¹"     → sphere S²
          "aba⁻¹b⁻¹" → torus T²
          "abab⁻¹"   → Klein bottle K
          "aa"       → projective plane ℝP²
          "aabb"     → Klein bottle K
        """
        polygon_table = {
            "aa^-1":     {"surface": "Sphere S²",          "chi": 2,  "orientable": True},
            "aba^-1b^-1":{"surface": "Torus T²",           "chi": 0,  "orientable": True},
            "abab^-1":   {"surface": "Klein bottle K",      "chi": 0,  "orientable": False},
            "aa":        {"surface": "Projective plane ℝP²","chi": 1,  "orientable": False},
            "aabb":      {"surface": "Klein bottle K",      "chi": 0,  "orientable": False},
            "abcabc":    {"surface": "Non-orientable N₃",   "chi": -1, "orientable": False},
        }
        return polygon_table.get(word,
            {"note": f"Word '{word}' — reduce to standard form using handle/crosscap moves."})

    @staticmethod
    def euler_char_from_word(word_length, num_pairs_identified):
        """
        For a 2n-gon with identifications:
        V − E + F:  F=1 (the polygon), E = n (after identification),
        V = 1 to n depending on identifications.
        Returns χ = 2 − E + F if we can infer V.
        This is an approximation — exact V requires explicit identification.
        """
        n = word_length // 2
        F = 1
        E = n
        return {"F": F, "E": E,
                "chi_formula": "V - E + F = V - " + str(E) + " + 1",
                "note": "Compute V explicitly from vertex identifications."}


def classify_surface_chi(chi, orientable):
    return Surfaces.classify_surface(chi, orientable)


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 5 — THE EULER CHARACTERISTIC
# ─────────────────────────────────────────────────────────────────────────────

class EulerCharacteristic:
    """
    Euler characteristic χ = V − E + F, graphs, trees, surfaces,
    map-colouring. Kinsey Ch.5 §5.1–§5.5.
    """

    @staticmethod
    def euler_characteristic(V, E, F):
        """χ = V − E + F. Kinsey §5.3."""
        return {"V": V, "E": E, "F": F, "chi": V - E + F}

    @staticmethod
    def euler_char_surface_genus(g, orientable=True):
        """
        χ = 2 − 2g (orientable genus-g surface).
        χ = 2 − k  (non-orientable, k crosscaps).
        """
        if orientable:
            chi = 2 - 2*g
            return {"genus": g, "chi": chi, "orientable": True}
        else:
            chi = 2 - g  # here g = k = number of crosscaps
            return {"crosscaps": g, "chi": chi, "orientable": False}

    # ── Graphs and Trees ─────────────────────────────────────────────

    @staticmethod
    def is_tree(V, E, connected=True):
        """
        A connected graph is a tree iff V − E = 1 (χ = 1) iff no cycles.
        Kinsey §5.2.
        """
        chi = V - E
        return {
            "is_tree": (chi == 1 and connected),
            "chi": chi,
            "V": V, "E": E,
            "note": "Tree ↔ connected + acyclic ↔ χ(graph) = 1."
        }

    @staticmethod
    def spanning_tree_loops(V, E):
        """
        Number of independent loops = E − V + 1 (for a connected graph).
        = number of edges removed to get a spanning tree.
        Kinsey §5.2.
        """
        loops = E - V + 1
        return {"independent_loops": max(0, loops),
                "spanning_tree_edges": V - 1,
                "extra_edges": max(0, loops)}

    @staticmethod
    def graph_from_adjacency(adj):
        """
        Build graph data from an adjacency list (dict: vertex → list of neighbours).
        Returns V, E, connected, χ.
        adj: {0: [1,2], 1: [0,3], ...}
        """
        V = len(adj)
        # Count edges (undirected: each counted once)
        E = sum(len(nbrs) for nbrs in adj.values()) // 2
        # BFS to check connectivity
        if V == 0:
            return {"V": 0, "E": 0, "connected": True, "chi": 0}
        visited = set()
        queue = deque([next(iter(adj))])
        while queue:
            v = queue.popleft()
            if v in visited:
                continue
            visited.add(v)
            for u in adj[v]:
                if u not in visited:
                    queue.append(u)
        connected = (len(visited) == V)
        chi = V - E
        return {"V": V, "E": E, "connected": connected,
                "chi": chi, "is_tree": (chi == 1 and connected)}

    @staticmethod
    def four_colour_theorem_note():
        return {
            "theorem": ("Every planar map can be coloured with at most 4 colours "
                        "such that no two adjacent regions share the same colour."),
            "proved": "Appel & Haken, 1976 (computer-assisted proof).",
            "heawood_bound": ("For a surface of Euler characteristic χ ≤ 1, "
                              "the chromatic number ≤ ⌊(7 + √(49 − 24χ)) / 2⌋.")
        }

    @staticmethod
    def heawood_number(chi):
        """
        Heawood's map-colouring bound: H(χ) = ⌊(7 + √(49−24χ)) / 2⌋.
        Kinsey §5.5.
        Valid for χ ≤ 1 (not sphere).
        """
        if chi > 1:
            return {"note": "Sphere: 4-colour theorem applies, not Heawood.", "H": 4}
        disc = 49 - 24*chi
        H = int((7 + math.sqrt(disc)) / 2)
        return {"chi": chi, "heawood_number": H,
                "meaning": f"At most {H} colours needed to colour a map on this surface."}

    @staticmethod
    def planar_graph_check(V, E, F):
        """
        A planar graph satisfies Euler's formula V−E+F=2 (connected).
        Also: for simple planar graphs, E ≤ 3V−6.
        Kinsey §5.3.
        """
        euler_ok = (V - E + F == 2)
        edge_bound_ok = (E <= 3*V - 6) if V >= 3 else True
        return {
            "V": V, "E": E, "F": F,
            "chi": V-E+F,
            "euler_formula_ok": euler_ok,
            "edge_bound_ok": edge_bound_ok,
            "planar_necessary": euler_ok and edge_bound_ok
        }


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 6 — HOMOLOGY
# ─────────────────────────────────────────────────────────────────────────────

class Homology:
    """
    Chain groups Cₖ, boundary operator ∂, cycles Zₖ, boundaries Bₖ,
    homology groups Hₖ = Zₖ/Bₖ, Betti numbers.
    Kinsey Ch.6 §6.1–§6.4.
    """

    @staticmethod
    def simplex_boundary(vertices):
        """
        Boundary of the simplex ⟨v₀, v₁, ..., vₙ⟩:
        ∂⟨v₀,...,vₙ⟩ = Σᵢ (−1)ⁱ ⟨v₀,...,v̂ᵢ,...,vₙ⟩
        vertices: list of vertex labels.
        Returns list of (sign, face) pairs.
        Kinsey §6.1 Definition 6.5.
        """
        n = len(vertices)
        if n == 1:
            return []  # boundary of a vertex = 0
        faces = []
        for i in range(n):
            sign = (-1)**i
            face = vertices[:i] + vertices[i+1:]
            faces.append((sign, face))
        return faces

    @staticmethod
    def boundary_of_chain(chain):
        """
        Boundary of a chain: dict {simplex_tuple: coefficient}.
        Returns boundary chain as dict.
        Kinsey §6.1 Definition 6.7.
        """
        result = defaultdict(int)
        for simplex, coeff in chain.items():
            verts = list(simplex)
            for sign, face in Homology.simplex_boundary(verts):
                result[tuple(face)] += coeff * sign
        # Remove zero coefficients
        return {k: v for k, v in result.items() if v != 0}

    @staticmethod
    def is_cycle(chain):
        """∂(C) = 0. Kinsey §6.2."""
        boundary = Homology.boundary_of_chain(chain)
        return len(boundary) == 0

    @staticmethod
    def is_boundary(chain, higher_chain):
        """
        C is a boundary if C = ∂(D) for some chain D.
        Check: does ∂(higher_chain) == chain?
        """
        bd = Homology.boundary_of_chain(higher_chain)
        return bd == dict(chain)

    @staticmethod
    def boundary_operator_matrix(simplices_k, simplices_k1):
        """
        Build the boundary operator matrix ∂ₖ: Cₖ → Cₖ₋₁ as an integer matrix.
        simplices_k:  ordered list of k-simplices (as tuples of vertices).
        simplices_k1: ordered list of (k-1)-simplices.
        Returns matrix M where M[i][j] = coefficient of simplices_k1[i] in ∂(simplices_k[j]).
        """
        n_rows = len(simplices_k1)
        n_cols = len(simplices_k)
        M = [[0]*n_cols for _ in range(n_rows)]
        idx_k1 = {s: i for i, s in enumerate(simplices_k1)}
        for j, sigma in enumerate(simplices_k):
            for sign, face in Homology.simplex_boundary(list(sigma)):
                face_t = tuple(face)
                if face_t in idx_k1:
                    M[idx_k1[face_t]][j] += sign
        return M

    @staticmethod
    def smith_normal_form(M):
        """
        Smith Normal Form of an integer matrix M (simplified version).
        Returns diagonal entries (invariant factors) for rank/homology computation.
        For exact computation we use integer row/column operations.
        """
        if not M or not M[0]:
            return {"rank": 0, "invariant_factors": [], "torsion": []}
        import numpy as np
        mat = np.array(M, dtype=int)
        # Use SVD for rank estimation (exact SNF needs integer arithmetic)
        _, s, _ = np.linalg.svd(mat.astype(float))
        rank = int(np.sum(s > 1e-9))
        return {"rank": rank, "note": "Use exact integer SNF for torsion coefficients.",
                "singular_values": [round(x, 6) for x in s[:rank+2]]}

    @staticmethod
    def homology_groups_surfaces(surface_name):
        """
        Homology groups of standard surfaces. Kinsey §6.2–§6.3.
        Returns H₀, H₁, H₂.
        """
        table = {
            "S²":    {"H0": "ℤ", "H1": "0",      "H2": "ℤ",
                      "chi": 2,  "betti": [1,0,1]},
            "T²":    {"H0": "ℤ", "H1": "ℤ⊕ℤ",   "H2": "ℤ",
                      "chi": 0,  "betti": [1,2,1]},
            "ℝP²":   {"H0": "ℤ", "H1": "ℤ/2ℤ",  "H2": "0",
                      "chi": 1,  "betti": [1,0,0]},
            "K":     {"H0": "ℤ", "H1": "ℤ⊕ℤ/2ℤ","H2": "0",
                      "chi": 0,  "betti": [1,1,0]},
            "g-torus":{"H0":"ℤ", "H1": "ℤ^{2g}", "H2": "ℤ",
                      "chi": "2-2g", "betti": [1,"2g",1]},
            "S¹":    {"H0": "ℤ", "H1": "ℤ",      "H2": "0",
                      "chi": 0,  "betti": [1,1,0]},
            "D²":    {"H0": "ℤ", "H1": "0",       "H2": "0",
                      "chi": 1,  "betti": [1,0,0]},
            "Möbius":{"H0": "ℤ", "H1": "ℤ",       "H2": "0",
                      "chi": 0,  "betti": [1,1,0]},
        }
        return table.get(surface_name,
            {"note": f"Surface '{surface_name}' not in table. Compute from triangulation."})

    @staticmethod
    def betti_numbers(H_groups_list):
        """
        Betti numbers βₖ = rank of Hₖ (free part).
        H_groups_list: list of strings like ["ℤ", "ℤ⊕ℤ", "ℤ/2ℤ", "0"]
        """
        def rank(h):
            if h == "0" or h == "": return 0
            count = h.count("ℤ") - h.count("ℤ/")
            return max(0, count)
        betti = [rank(h) for h in H_groups_list]
        chi = sum((-1)**k * b for k, b in enumerate(betti))
        return {"betti_numbers": betti, "chi_from_betti": chi}

    @staticmethod
    def euler_char_from_betti(betti_numbers):
        """χ = Σ (−1)ᵏ βₖ  (Euler–Poincaré formula). Kinsey §6.4."""
        chi = sum((-1)**k * b for k, b in enumerate(betti_numbers))
        return {"betti_numbers": betti_numbers, "chi": chi,
                "formula": "χ = β₀ − β₁ + β₂ − β₃ + ..."}

    @staticmethod
    def mayer_vietoris_note():
        return {
            "theorem": ("Mayer-Vietoris sequence: if X = A ∪ B (open), then there is "
                        "a long exact sequence: "
                        "... → Hₙ(A∩B) → Hₙ(A)⊕Hₙ(B) → Hₙ(X) → Hₙ₋₁(A∩B) → ..."),
            "use": "Compute homology of X by decomposing into simpler pieces A and B.",
        }


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 7 — CELLULAR FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

class CellularFunctions:
    """
    Cellular (simplicial) maps, induced homomorphisms on homology,
    covering spaces, degree of a map. Kinsey Ch.7 §7.1–§7.4.
    """

    @staticmethod
    def induced_homomorphism(vertex_map, chain):
        """
        Cellular function f: K → L induces f_* on chains.
        vertex_map: dict {vertex_in_K: vertex_in_L}.
        chain: dict {simplex_tuple: coefficient} in K.
        Returns the image chain in L.
        Kinsey §7.1.
        """
        result = defaultdict(int)
        for simplex, coeff in chain.items():
            image = tuple(vertex_map.get(v, v) for v in simplex)
            # If any two vertices map to same: degenerate → 0
            if len(set(image)) < len(image):
                continue
            result[image] += coeff
        return dict(result)

    @staticmethod
    def degree_of_map_circle(total_winding):
        """
        Degree of a map f: S¹ → S¹:
        deg(f) = total winding number.
        H₁(S¹) = ℤ; f_*([generator]) = deg(f)·[generator].
        Kinsey §7.1.
        """
        return {"degree": total_winding,
                "H1_induced": f"f_*: ℤ → ℤ, 1 ↦ {total_winding}",
                "note": "deg=1: homeomorphism; deg=0: null-homotopic; deg=-1: reflection."}

    @staticmethod
    def degree_of_map_sphere(n, antipodal=False, reflection=False):
        """
        Key degrees on Sⁿ:
        - Identity: deg = 1
        - Antipodal map x ↦ -x: deg = (-1)^{n+1}
        - Reflection in one coordinate: deg = -1
        Kinsey §7.1, §11.4.
        """
        if antipodal:
            deg = (-1)**(n+1)
            return {"degree": deg, "map": "antipodal",
                    "note": f"Antipodal map on S^{n} has degree (-1)^{n+1} = {deg}"}
        if reflection:
            return {"degree": -1, "map": "reflection",
                    "note": "Any reflection has degree -1."}
        return {"degree": 1, "map": "identity"}

    @staticmethod
    def covering_space_info(base_space, n_sheets):
        """
        n-sheeted covering space p: X̃ → X.
        Key facts: χ(X̃) = n · χ(X).
        H₁(X̃) related to H₁(X) via the covering.
        Kinsey §7.4.
        """
        return {
            "base": base_space,
            "sheets": n_sheets,
            "chi_relation": f"χ(cover) = {n_sheets} · χ(base)",
            "examples": {
                "ℝ → S¹":        "Universal cover of S¹, infinite sheets.",
                "S² → ℝP²":      "2-sheeted cover of ℝP².",
                "S¹ →ⁿ S¹":      f"{n_sheets}-sheeted cover (z ↦ zⁿ).",
                "T² → Klein K":  "2-sheeted orientable cover of the Klein bottle.",
            }
        }

    @staticmethod
    def lefschetz_fixed_point(betti_numbers, trace_on_homology):
        """
        Lefschetz fixed-point theorem:
        L(f) = Σ (-1)^k tr(f_*: H_k → H_k).
        If L(f) ≠ 0, then f has a fixed point.
        Kinsey §7.2 / related.
        trace_on_homology: list of traces tr(f_* on H_k) for k=0,1,...
        """
        L = sum((-1)**k * t for k, t in enumerate(trace_on_homology))
        return {
            "lefschetz_number": L,
            "has_fixed_point": (L != 0),
            "note": "L(f)≠0 guarantees a fixed point; L(f)=0 does not rule one out."
        }


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 8 — INVARIANCE OF HOMOLOGY
# ─────────────────────────────────────────────────────────────────────────────

class HomologyInvariance:
    """
    Topological invariance of homology groups, Simplicial Approximation Theorem.
    Kinsey Ch.8 §8.1–§8.2.
    """

    @staticmethod
    def invariance_statement():
        return {
            "theorem": ("Topological invariance of homology (Kinsey §8.1): "
                        "If X and Y are homeomorphic, then Hₖ(X) ≅ Hₖ(Y) for all k."),
            "consequence": ("Homology groups are topological invariants. "
                            "Different homology groups ⟹ non-homeomorphic spaces."),
            "stronger": ("Homotopy invariance: if f: X→Y is a homotopy equivalence, "
                         "then f_*: Hₖ(X) → Hₖ(Y) is an isomorphism for all k.")
        }

    @staticmethod
    def simplicial_approximation_theorem():
        return {
            "theorem": ("Simplicial Approximation Theorem (Kinsey §8.2): "
                        "Given a continuous map f: |K| → |L| between polyhedra, "
                        "there exists a subdivision K' of K and a simplicial map "
                        "g: K' → L that is homotopic to f."),
            "use": ("Reduces questions about continuous maps to combinatorial "
                    "(simplicial) ones, enabling algebraic computation.")
        }

    @staticmethod
    def excision_theorem():
        return {
            "theorem": ("Excision: if Z ⊆ A ⊆ X and cl(Z) ⊆ int(A), then "
                        "Hₙ(X-Z, A-Z) ≅ Hₙ(X, A) for all n."),
            "use": "Key tool for computing relative homology."
        }

    @staticmethod
    def long_exact_sequence_pair(A_in_X):
        """
        Long exact sequence of a pair (X, A):
        ... → Hₙ(A) →ⁱ* Hₙ(X) →ʲ* Hₙ(X,A) →∂ Hₙ₋₁(A) → ...
        """
        return {
            "sequence": ("... → Hₙ(A) → Hₙ(X) → Hₙ(X,A) → Hₙ₋₁(A) → "
                         "Hₙ₋₁(X) → Hₙ₋₁(X,A) → ..."),
            "A_in_X": A_in_X,
            "note": "Exact: image of each map = kernel of the next."
        }


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 9 — HOMOTOPY
# ─────────────────────────────────────────────────────────────────────────────

class Homotopy:
    """
    Homotopy equivalence, contractibility, fundamental group π₁.
    Kinsey Ch.9 §9.1–§9.2.
    """

    @staticmethod
    def homotopy_equivalence_note():
        return {
            "definition": ("f: X→Y and g: Y→X are homotopy inverses if "
                           "g∘f ~ 1_X and f∘g ~ 1_Y. Then X and Y are homotopy equivalent."),
            "weaker_than": "Homeomorphism ⟹ homotopy equivalence, but not conversely.",
            "examples": [
                "ℝⁿ ~ * (contractible)",
                "S¹ ~ annulus ~ punctured plane",
                "S² is not homotopy equivalent to T²",
                "Any convex subset of ℝⁿ is contractible",
            ]
        }

    @staticmethod
    def is_contractible(space):
        """
        A space is contractible if it is homotopy equivalent to a point.
        H₀ = ℤ, Hₖ = 0 for k > 0.
        Kinsey §9.1.
        """
        contractible_spaces = {
            "ℝⁿ": True, "Dⁿ": True, "cone": True,
            "S¹": False, "S²": False, "T²": False, "ℝP²": False,
            "point": True, "interval": True,
        }
        return {"space": space,
                "contractible": contractible_spaces.get(space, "Unknown"),
                "homology": "H₀=ℤ, Hₖ=0 for k>0" if contractible_spaces.get(space) else "Non-trivial."}

    @staticmethod
    def fundamental_group(space):
        """
        Fundamental group π₁(X, x₀). Kinsey §9.2.
        """
        pi1_table = {
            "S¹":       "ℤ",
            "T²":       "ℤ × ℤ",
            "S²":       "0 (trivial)",
            "ℝP²":      "ℤ/2ℤ",
            "Klein K":  "⟨a,b | abab⁻¹ = 1⟩",
            "ℝⁿ":       "0 (trivial)",
            "Sⁿ n≥2":   "0 (trivial)",
            "figure 8": "ℤ * ℤ (free group on 2 generators)",
            "wedge S¹ S¹": "ℤ * ℤ",
            "g-torus":  "⟨a₁,b₁,...,aₘ,bₘ | [a₁,b₁]···[aₘ,bₘ]=1⟩",
            "ℝP²#ℝP²":  "⟨a,b | a²b²=1⟩ (Klein bottle)",
        }
        return {"space": space,
                "pi1": pi1_table.get(space, "Not in table — use van Kampen's theorem."),
                "note": "π₁ = 0 means simply connected."}

    @staticmethod
    def van_kampen_theorem(pi1_A, pi1_B, pi1_A_intersect_B):
        """
        van Kampen's theorem: if X = A ∪ B with A, B, A∩B path-connected,
        π₁(X) = π₁(A) *_{π₁(A∩B)} π₁(B)   (amalgamated free product).
        Kinsey §9.2.
        """
        return {
            "theorem": ("π₁(X) ≅ π₁(A) *_{π₁(A∩B)} π₁(B) = "
                        "free product of π₁(A) and π₁(B) modulo "
                        "the relations from π₁(A∩B)"),
            "pi1_A": pi1_A,
            "pi1_B": pi1_B,
            "pi1_intersection": pi1_A_intersect_B,
            "example": ("S¹ ∨ S¹: A=top S¹, B=bottom S¹, A∩B=point. "
                        "π₁ = ℤ * ℤ (free group on 2 generators).")
        }

    @staticmethod
    def deformation_retract(Y, X_subspace):
        """
        X is a deformation retract of Y if there is r: Y→X with
        r∘i ~ 1_Y where i: X↪Y.
        Consequence: H*(X) ≅ H*(Y), π₁(X) ≅ π₁(Y).
        Kinsey §9.1.
        """
        return {
            "Y": Y, "retract_X": X_subspace,
            "consequence": f"H*(Y) ≅ H*({X_subspace}), π₁(Y) ≅ π₁({X_subspace})",
            "examples": {
                "ℝⁿ → point": "ℝⁿ contracts to origin.",
                "Cylinder → S¹": "S¹ × [0,1] deformation retracts to S¹ × {0}.",
                "Möbius → S¹": "Möbius band deformation retracts to its core circle.",
                "punctured ℝ² → S¹": "ℝ²\\{0} deformation retracts to unit circle.",
            }
        }


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 10 — MISCELLANY
# ─────────────────────────────────────────────────────────────────────────────

class Miscellany:
    """
    Topological applications: Brouwer, Borsuk-Ulam, ham sandwich,
    Jordan curve theorem, 3-manifolds. Kinsey Ch.10 §10.1–§10.3.
    """

    @staticmethod
    def brouwer_fixed_point(n=2):
        """
        Brouwer Fixed Point Theorem: every continuous f: Dⁿ → Dⁿ has a fixed point.
        Kinsey §10.1.
        """
        return {
            "theorem": f"Every continuous f: D^{n} → D^{n} has a fixed point.",
            "proof_idea": ("Assume no fixed point → construct retraction r: D^n → S^{n-1}, "
                           "but H_{n-1}(D^n)=0 while H_{n-1}(S^{n-1})=ℤ — contradiction."),
            "consequence": ("Every continuous map of a closed disc to itself "
                            "must fix at least one point.")
        }

    @staticmethod
    def borsuk_ulam(n=2):
        """
        Borsuk-Ulam Theorem: for every continuous f: Sⁿ → ℝⁿ,
        there exists x with f(x) = f(-x).
        Kinsey §10.1.
        """
        return {
            "theorem": (f"For every continuous f: S^{n} → ℝ^{n}, "
                        f"∃x ∈ S^{n} such that f(x) = f(-x)."),
            "n=2_application": ("On the earth's surface, there always exist "
                                "two antipodal points with the same temperature and pressure."),
            "ham_sandwich": ("Ham sandwich theorem: any n bounded measurable sets in ℝⁿ "
                             "can be simultaneously bisected by a single hyperplane. "
                             "Follows from Borsuk-Ulam.")
        }

    @staticmethod
    def jordan_curve_theorem():
        """
        Jordan Curve Theorem. Kinsey §10.2.
        """
        return {
            "theorem": ("Every simple closed curve (Jordan curve) C in ℝ² (or S²) "
                        "divides the plane into exactly two connected regions: "
                        "a bounded interior and an unbounded exterior."),
            "higher_dim": ("Jordan-Brouwer separation: Sⁿ⁻¹ ⊂ Sⁿ divides Sⁿ into "
                           "exactly 2 connected components."),
            "difficulty": ("The theorem is obvious geometrically but surprisingly hard "
                           "to prove rigorously; Kinsey proves it using homology §10.2.")
        }

    @staticmethod
    def three_manifolds_overview():
        """
        3-manifolds — brief overview. Kinsey §10.3.
        """
        return {
            "closed_3_manifolds": [
                "S³ (3-sphere): simply connected, H₁=0",
                "T³ = S¹×S¹×S¹ (3-torus): H₁ = ℤ³",
                "ℝP³ (real projective 3-space): π₁ = ℤ/2ℤ",
                "Lens spaces L(p,q): π₁ = ℤ/pℤ",
                "Poincaré homology sphere: π₁ ≠ 0 but H₁ = 0",
            ],
            "Poincare_conjecture": ("Every simply connected closed 3-manifold is "
                                    "homeomorphic to S³. Proved by Perelman 2002–2003."),
            "geometrization": ("Thurston's geometrization conjecture (proved by Perelman): "
                               "every closed 3-manifold can be cut along tori into pieces "
                               "admitting one of 8 geometric structures.")
        }

    @staticmethod
    def euler_char_3_manifold(V, E, F, T):
        """
        Euler characteristic of a 3-manifold triangulation:
        χ = V − E + F − T  (T = number of tetrahedra).
        For closed 3-manifolds, χ = 0 always.
        """
        chi = V - E + F - T
        return {"V": V, "E": E, "F": F, "T": T, "chi": chi,
                "note": "χ = 0 for all closed odd-dimensional manifolds."}


# ─────────────────────────────────────────────────────────────────────────────
# CHAPTER 11 — TOPOLOGY AND CALCULUS
# ─────────────────────────────────────────────────────────────────────────────

class TopoCalculus:
    """
    Vector fields in ℝⁿ, differentiable manifolds, integration,
    degree of smooth maps. Kinsey Ch.11 §11.1–§11.4.
    """

    @staticmethod
    def index_of_zero_2d(jacobian_at_zero):
        """
        Index (winding number) of a vector field v at an isolated zero.
        For a linear vector field v(x) = Ax near 0: index = sign(det A).
        Kinsey §11.1.
        jacobian_at_zero: 2×2 matrix [[a,b],[c,d]].
        """
        a, b = jacobian_at_zero[0]
        c, d = jacobian_at_zero[1]
        det = a*d - b*c
        index = 1 if det > 0 else (-1 if det < 0 else 0)
        return {"determinant": round(det, 10), "index": index,
                "note": ("Index = +1 if orientation-preserving (det>0), "
                         "-1 if reversing (det<0).")}

    @staticmethod
    def poincare_hopf_theorem(indices):
        """
        Poincaré–Hopf theorem: for a vector field on a compact surface with
        isolated zeros, Σ indices = χ(surface).
        Kinsey §11.3.
        indices: list of indices at each zero.
        """
        total = sum(indices)
        return {
            "sum_of_indices": total,
            "chi_surface_must_be": total,
            "theorem": ("Σ index(zeroᵢ) = χ(M) for any vector field "
                        "with isolated zeros on compact M."),
            "corollary": ("S² has χ=2, so every vector field on S² must "
                          "have zeros summing to 2 — you cannot comb a sphere! "
                          "(hairy ball theorem)")
        }

    @staticmethod
    def hairy_ball_theorem(n):
        """
        Hairy Ball Theorem: Sⁿ has a nowhere-zero vector field iff n is odd.
        Kinsey §11.3.
        """
        has_nonzero = (n % 2 == 1)
        return {
            "sphere": f"S^{n}",
            "nowhere_zero_field_exists": has_nonzero,
            "reason": (f"χ(S^{n}) = 1+(-1)^{n} = "
                       f"{1 + (-1)**n}. Poincaré-Hopf: if no zeros, sum=0=χ. "
                       f"{'χ=0 ✓' if (1+(-1)**n)==0 else 'χ≠0 ✗ — no nowhere-zero field.'}"),
        }

    @staticmethod
    def differential_form_degree(k, n):
        """
        A differential k-form on an n-manifold:
        Ω^k(M) has dimension C(n,k).
        Kinsey §11.4.
        """
        from math import comb
        dim = comb(n, k)
        return {
            "k_form_on_n_manifold": f"Ω^{k}(M^{n})",
            "dimension": dim,
            "examples": {
                "0-form": "smooth function",
                "1-form": "linear combination of dxᵢ",
                "n-form": "f dx₁∧dx₂∧...∧dxₙ (volume form)",
            }
        }

    @staticmethod
    def stokes_theorem_note():
        return {
            "theorem": ("∫_M dω = ∫_{∂M} ω  for a (k-1)-form ω on a k-manifold M."),
            "special_cases": {
                "Fundamental theorem of calculus": "∫_[a,b] df = f(b) - f(a)",
                "Green's theorem": "∬_D (∂Q/∂x − ∂P/∂y) dA = ∮_∂D (P dx + Q dy)",
                "Gauss divergence theorem": "∭_V div F dV = ∬_{∂V} F · dA",
                "Classical Stokes": "∬_Σ (∇×F)·dA = ∮_{∂Σ} F·dr",
            }
        }

    @staticmethod
    def degree_smooth_map(preimage_signs):
        """
        Degree of a smooth map f: M → N between compact n-manifolds of same dimension.
        For a regular value y, deg(f) = Σ sign(det Df_x) over preimages x of y.
        Kinsey §11.4.
        preimage_signs: list of +1 or -1 for each preimage point.
        """
        deg = sum(preimage_signs)
        return {"degree": deg, "preimage_signs": preimage_signs,
                "note": ("Degree is independent of the choice of regular value y. "
                         "deg(f) equals the induced map on top homology: f_*[M]= deg·[N].")}

    @staticmethod
    def manifold_examples():
        """
        Standard examples of smooth manifolds. Kinsey §11.2.
        """
        return {
            "Sⁿ":           "n-sphere: {x ∈ ℝⁿ⁺¹ : |x| = 1}",
            "T^n":          "n-torus: S¹ × ... × S¹ (n factors)",
            "GL(n,ℝ)":      "Invertible n×n matrices: open subset of ℝⁿ²",
            "SO(n)":        "Special orthogonal group: dim = n(n-1)/2",
            "Grassmannian": "G(k,n): k-planes in ℝⁿ; dim = k(n-k)",
            "ℝPⁿ":          "Real projective n-space: Sⁿ/antipodal; dim = n",
            "CPⁿ":          "Complex projective n-space; dim = 2n",
        }


# ─────────────────────────────────────────────────────────────────────────────
# APPENDIX — GROUPS
# ─────────────────────────────────────────────────────────────────────────────

class Groups:
    """
    Group theory: abelian groups, free groups, presentations, quotient groups.
    Kinsey Appendix §App.1–§App.6.
    """

    @staticmethod
    def classify_finitely_generated_abelian(invariant_factors):
        """
        Classification of finitely generated abelian groups:
        G ≅ ℤ^r ⊕ ℤ/n₁ℤ ⊕ ... ⊕ ℤ/nₖℤ  where n₁|n₂|...|nₖ.
        invariant_factors: list of integers n₁, ..., nₖ (torsion) + r=rank (free part).
        """
        return {
            "group_description": (
                "ℤ^r ⊕ " + " ⊕ ".join(f"ℤ/{n}ℤ" for n in invariant_factors)
                if invariant_factors else "ℤ^r (free)"
            ),
            "rank_free_part": "r",
            "torsion_part": invariant_factors,
            "note": "invariant_factors[i] | invariant_factors[i+1] (divisibility condition)"
        }

    @staticmethod
    def free_group(generators):
        """
        Free group on a set of generators. F_n = free group on n generators.
        """
        n = len(generators)
        return {
            "generators": generators,
            "rank": n,
            "name": f"F_{n}" if n > 0 else "{1}",
            "note": ("Every group is a quotient of a free group. "
                     "F₁ ≅ ℤ, F_n for n≥2 is non-abelian.")
        }

    @staticmethod
    def group_presentation(generators, relations):
        """
        Group presentation ⟨generators | relations⟩.
        Returns the presentation string and abelianization.
        """
        gens_str = ", ".join(generators)
        rels_str = ", ".join(relations)
        return {
            "presentation": f"⟨{gens_str} | {rels_str}⟩",
            "generators": generators,
            "relations": relations,
            "abelianization": ("Quotient by commutator subgroup: "
                               "set all [g,h]=1 and reduce.")
        }

    @staticmethod
    def abelianization(group_presentation_str, extra_relations=None):
        """
        Abelianization: add commutator relations [a,b]=1 for all generators.
        Returns description of H₁ = G/[G,G].
        """
        return {
            "original": group_presentation_str,
            "H1_abelianization": ("Add: all generators commute → "
                                  "reduce relations in ℤ-module language."),
            "note": "H₁(X; ℤ) = π₁(X)ᵃᵇ (abelianization of the fundamental group)."
        }

    @staticmethod
    def exact_sequence_check(maps_and_groups):
        """
        Check exactness of a sequence ... → Aᵢ →fᵢ Aᵢ₊₁ → ...
        Exact at Aᵢ₊₁ means im(fᵢ) = ker(fᵢ₊₁).
        maps_and_groups: list of {"group": G, "map_image": img, "map_kernel": ker}.
        """
        results = []
        for i in range(1, len(maps_and_groups) - 1):
            prev_image   = maps_and_groups[i-1].get("map_image", set())
            curr_kernel  = maps_and_groups[i].get("map_kernel", set())
            exact = (set(prev_image) == set(curr_kernel))
            results.append({"at_group": maps_and_groups[i]["group"],
                            "exact": exact})
        return results

    @staticmethod
    def torsion_part(homology_group_str):
        """
        Extract torsion from homology group description string.
        E.g. "ℤ⊕ℤ/2ℤ⊕ℤ/4ℤ" → free rank=1, torsion=[2,4].
        """
        import re
        torsion = [int(m) for m in re.findall(r'ℤ/(\d+)ℤ', homology_group_str)]
        free    = homology_group_str.count('ℤ') - homology_group_str.count('ℤ/')
        return {"free_rank": max(0,free), "torsion_coefficients": torsion,
                "original": homology_group_str}


# ─────────────────────────────────────────────────────────────────────────────
# COMBINED INVARIANT CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

class SurfaceInvariantCalculator:
    """
    All-in-one calculator: given a surface, compute every invariant.
    """

    @staticmethod
    def full_profile(chi, orientable, boundary_components=0):
        """
        Given χ and orientability, compute every invariant.
        """
        classification = Surfaces.classify_surface(chi, orientable, boundary_components)

        # Genus / crosscaps
        chi_closed = chi + boundary_components
        if orientable:
            g = (2 - chi_closed) // 2
            H0, H1, H2 = "ℤ", f"ℤ^{2*g}" if g>0 else "0", "ℤ" if boundary_components==0 else "0"
            betti = [1, 2*g, 1 if boundary_components==0 else 0]
            pi1 = f"⟨a₁,b₁,...,a_{g},b_{g} | [a₁,b₁]···[a_{g},b_{g}]=1⟩" if g>0 else "0"
        else:
            k = 2 - chi_closed
            H0, H2 = "ℤ", "0"
            if k == 1:
                H1, pi1 = "ℤ/2ℤ", "ℤ/2ℤ"
            elif k == 2:
                H1, pi1 = "ℤ⊕ℤ/2ℤ", "⟨a,b | abab⁻¹=1⟩"
            else:
                H1, pi1 = f"ℤ^{k-1}⊕ℤ/2ℤ", f"⟨a₁,...,a_{k} | a₁²···a_{k}²=1⟩"
            betti = [1, k-1, 0]

        heawood = EulerCharacteristic.heawood_number(chi)
        poincare_hopf = {"sum_indices_must_equal": chi}

        return {
            "classification":    classification,
            "chi":               chi,
            "orientable":        orientable,
            "boundary_components": boundary_components,
            "H0": H0, "H1": H1, "H2": H2,
            "betti_numbers":     betti,
            "chi_from_betti":    sum((-1)**k*b for k,b in enumerate(betti)),
            "fundamental_group_pi1": pi1,
            "heawood_map_number": heawood.get("heawood_number", heawood.get("H", 4)),
            "poincare_hopf":     poincare_hopf,
        }

    @staticmethod
    def compare(surfaces):
        """
        Compare topological invariants of a list of surfaces.
        surfaces: list of dicts with keys 'name','chi','orientable'.
        """
        rows = []
        for s in surfaces:
            profile = SurfaceInvariantCalculator.full_profile(
                s["chi"], s["orientable"], s.get("boundary_components", 0))
            rows.append({
                "name":      s["name"],
                "chi":       profile["chi"],
                "orientable":profile["orientable"],
                "H1":        profile["H1"],
                "pi1":       profile["fundamental_group_pi1"],
                "betti":     profile["betti_numbers"],
            })
        return rows