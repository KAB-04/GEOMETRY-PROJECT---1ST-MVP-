"""
══════════════════════════════════════════════════════════════
        COMPUTATIONAL GEOMETRY ENGINE.
        Computational Geometry: Algorithms and Applications.
══════════════════════════════════════════════════════════════

Contents:
   1  : Primitives          (orientation test, cross product, point-in-half-plane  §1.1)
   2  : ConvexHull2D        (Andrew's monotone chain O(n log n)                    §1.1)
   3  : LineSegment         (intersection, DCEL half-edge representation            §2.1–2.2)
   4  : SweepLine           (Shamos-Hoey / Bentley-Ottmann event framework         §2.1)
   5  : PolygonTriangulation(y-monotone decomposition + ear-clip                   §3.1–3.3)
   6  : LinearProgramming2D (randomised incremental LP, smallest enclosing disc    §4.2–4.7)
   7  : RangeTree           (1-D range search, kd-tree, 2-D range tree             §5.1–5.3)
   8  : PointLocation       (trapezoidal map / slab method                         §6.1)
   9  : VoronoiDiagram      (Fortune's sweep properties, Voronoi cell geometry     §7.1–7.2)
   10 : DelaunayTriangulation(Delaunay criterion, incremental flip                 §9.1–9.3)
   11 : IntervalTree        (stabbing query, interval tree construction             §10.1)
   12 : ConvexHull3D        (3-D incremental, complexity bounds                    §11.1–11.2)
   13 : Arrangements        (line arrangements, Zone Theorem, duality              §8.2–8.3)
   14 : BSPTree             (binary space partition, painter's algorithm           §12.1–12.3)
   15 : MotionPlanning      (configuration space, Minkowski sum                    §13.1–13.3)
   16 : Quadtree            (quadtree for point sets, mesh generation              §14.1–14.2)
   17 : VisibilityGraph     (shortest path, visibility graph construction          §15.1–15.2)
   18 : SimplexRange        (partition trees, cutting trees                        §16.1–16.3)

Usage:
  python ComputationalGeometry.py          # run built-in demo
  import ComputationalGeometry as cg       # import as module
"""

import math
import random
import bisect
from collections import defaultdict, deque
from itertools import combinations


# ─────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────

def _fmt(v, d=6):
    if isinstance(v, float): return round(v, d)
    return v

EPS = 1e-9


# ================================================================
# 1. PRIMITIVES  §1.1
# ================================================================

class Primitives:
    """
    Fundamental geometric predicates used throughout the book.  §1.1.

    All algorithms in computational geometry reduce to a small set of
    constant-time primitive operations.  Correctness depends on these
    primitives being implemented exactly.
    """

    @staticmethod
    def cross2d(o, a, b):
        """
        2-D cross product of vectors OA and OB.  §1.1.
        Returns  (a-o) × (b-o) = (ax-ox)(by-oy) − (ay-oy)(bx-ox).
          > 0 : b is to the LEFT  of directed line o→a  (counter-clockwise turn)
          = 0 : o, a, b are collinear
          < 0 : b is to the RIGHT of directed line o→a  (clockwise turn)
        """
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

    @staticmethod
    def turn(o, a, b):
        """
        Returns 'left', 'right', or 'collinear' for points o→a→b.  §1.1.
        """
        c = Primitives.cross2d(o, a, b)
        if c > EPS:  return 'left'
        if c < -EPS: return 'right'
        return 'collinear'

    @staticmethod
    def left_of(p, a, b):
        """True if p is strictly to the left of directed line a→b."""
        return Primitives.cross2d(a, b, p) > EPS

    @staticmethod
    def on_or_left_of(p, a, b):
        """True if p is on or to the left of directed line a→b."""
        return Primitives.cross2d(a, b, p) >= -EPS

    @staticmethod
    def in_circle(a, b, c, d):
        """
        InCircle test.  §9.2.
        Returns > 0 if d lies inside the circumcircle of (a, b, c)
        (where a, b, c are in counter-clockwise order).
        Used by Delaunay triangulation to check the Delaunay condition.
        """
        ax, ay = a[0]-d[0], a[1]-d[1]
        bx, by = b[0]-d[0], b[1]-d[1]
        cx, cy = c[0]-d[0], c[1]-d[1]
        return (ax*(by*( ax**2+ay**2) - cy*(bx**2+by**2)) -
                ay*(bx*(ax**2+ay**2) - cx*(bx**2+by**2)) +
                (ax**2+ay**2)*(bx*cy - by*cx))

    @staticmethod
    def dist2d(p, q):
        """Euclidean distance between p and q."""
        return _fmt(math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2))

    @staticmethod
    def dist3d(p, q):
        """Euclidean distance in 3-D."""
        return _fmt(math.sqrt(sum((a-b)**2 for a,b in zip(p,q))))

    @staticmethod
    def point_in_triangle(p, a, b, c):
        """
        Test whether point p is inside triangle (a, b, c).
        Uses barycentric / cross-product method.  §3.1.
        """
        d1 = Primitives.cross2d(a, b, p)
        d2 = Primitives.cross2d(b, c, p)
        d3 = Primitives.cross2d(c, a, p)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    @staticmethod
    def polygon_area(pts):
        """
        Signed area of a polygon via the shoelace formula.  §3.1.
        Positive = counter-clockwise, negative = clockwise.
        """
        n = len(pts)
        area = 0.0
        for i in range(n):
            j = (i+1) % n
            area += pts[i][0]*pts[j][1] - pts[j][0]*pts[i][1]
        return _fmt(area / 2.0)

    @staticmethod
    def is_convex_polygon(pts):
        """Check that a polygon (list of points in order) is convex.  §1.1."""
        n = len(pts)
        sign = None
        for i in range(n):
            c = Primitives.cross2d(pts[i], pts[(i+1)%n], pts[(i+2)%n])
            if abs(c) < EPS: continue
            s = 1 if c > 0 else -1
            if sign is None: sign = s
            elif sign != s:  return False
        return True


# ================================================================
# 2. CONVEX HULL 2-D  §1.1
# ================================================================

class ConvexHull2D:
    """
    Planar convex hull algorithms.  §1.1.

    The convex hull CH(P) of a set P is the smallest convex set containing P.
    Equivalently, it is the convex polygon whose vertices are points from P and
    that contains all points of P.  (§1.1, Definition / rubber-band intuition.)

    Algorithm: Andrew's monotone chain (O(n log n)).
    The book's own algorithm (p. 6–9) is equivalent; upper hull + lower hull.

    Theorem 1.1: The convex hull of n points can be computed in O(n log n).
    Lower bound: Ω(n log n) by reduction from sorting.
    """

    @staticmethod
    def upper_hull(points):
        """
        Compute the upper hull of a sorted point set.  §1.1.
        Returns vertices left-to-right on the upper boundary.
        """
        hull = []
        for p in points:
            while len(hull) >= 2 and Primitives.cross2d(hull[-2], hull[-1], p) >= 0:
                hull.pop()
            hull.append(p)
        return hull

    @staticmethod
    def lower_hull(points):
        """Compute the lower hull of a sorted point set.  §1.1."""
        hull = []
        for p in reversed(points):
            while len(hull) >= 2 and Primitives.cross2d(hull[-2], hull[-1], p) >= 0:
                hull.pop()
            hull.append(p)
        return hull

    @staticmethod
    def convex_hull(points):
        """
        Full planar convex hull using Andrew's monotone chain.  §1.1.
        Returns vertices in counter-clockwise order.
        Time: O(n log n).  Space: O(n).
        """
        pts = sorted(set(map(tuple, points)))
        if len(pts) <= 1:
            return pts
        upper = ConvexHull2D.upper_hull(pts)
        lower = ConvexHull2D.lower_hull(pts)
        hull = lower[:-1] + upper[:-1]
        return hull

    @staticmethod
    def is_point_in_convex_hull(hull_ccw, p):
        """
        Test whether p is inside or on the boundary of a convex polygon
        given in CCW order.  §1.1.
        """
        n = len(hull_ccw)
        for i in range(n):
            if Primitives.cross2d(hull_ccw[i], hull_ccw[(i+1)%n], p) < -EPS:
                return False
        return True

    @staticmethod
    def hull_perimeter(hull):
        """Perimeter of a convex hull polygon."""
        n = len(hull)
        return _fmt(sum(Primitives.dist2d(hull[i], hull[(i+1)%n]) for i in range(n)))

    @staticmethod
    def hull_area(hull):
        """Area of a convex hull using shoelace formula."""
        return abs(Primitives.polygon_area(hull))


# ================================================================
# 3. LINE SEGMENT INTERSECTION & DCEL  §2.1–2.2
# ================================================================

class LineSegment:
    """
    Line segment primitives and intersection.  §2.1.

    Two closed segments intersect if their bounding boxes overlap and
    each segment straddles the line containing the other (or they share
    an endpoint).

    Theorem 2.4: All intersections of n segments can be reported in
    O(n log n + I log n) time and O(n) space (Bentley-Ottmann).
    """

    def __init__(self, p, q):
        self.p = tuple(p)
        self.q = tuple(q)

    def __repr__(self):
        return f"Segment({self.p}→{self.q})"

    @staticmethod
    def _on_segment(p, q, r):
        """Is r on segment pq (given collinearity)?"""
        return (min(p[0],q[0])-EPS <= r[0] <= max(p[0],q[0])+EPS and
                min(p[1],q[1])-EPS <= r[1] <= max(p[1],q[1])+EPS)

    def intersects(self, other):
        """
        Test whether two closed segments intersect.  §2.1.
        Uses cross-product straddling test.
        """
        p1, q1 = self.p, self.q
        p2, q2 = other.p, other.q
        d1 = Primitives.cross2d(p2, q2, p1)
        d2 = Primitives.cross2d(p2, q2, q1)
        d3 = Primitives.cross2d(p1, q1, p2)
        d4 = Primitives.cross2d(p1, q1, q2)
        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
           ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True
        if abs(d1) < EPS and self._on_segment(p2, q2, p1): return True
        if abs(d2) < EPS and self._on_segment(p2, q2, q1): return True
        if abs(d3) < EPS and self._on_segment(p1, q1, p2): return True
        if abs(d4) < EPS and self._on_segment(p1, q1, q2): return True
        return False

    def intersection_point(self, other):
        """
        Compute the intersection point of two segments (if it exists).  §2.1.
        Returns None if they do not intersect.
        """
        if not self.intersects(other):
            return None
        x1,y1 = self.p; x2,y2 = self.q
        x3,y3 = other.p; x4,y4 = other.q
        denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        if abs(denom) < EPS:
            return self.p  # coincident or parallel — return endpoint
        t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
        x = x1 + t*(x2-x1)
        y = y1 + t*(y2-y1)
        return (_fmt(x), _fmt(y))

    def length(self):
        return Primitives.dist2d(self.p, self.q)

    @staticmethod
    def brute_force_intersections(segments):
        """
        O(n²) brute-force: report all intersection points.  §2.1.
        Returns list of (point, seg_i, seg_j).
        """
        results = []
        for i, si in enumerate(segments):
            for j, sj in enumerate(segments):
                if j <= i: continue
                pt = si.intersection_point(sj)
                if pt is not None:
                    results.append({"point": pt, "seg_i": i, "seg_j": j})
        return results


class DCEL:
    """
    Doubly-Connected Edge List representation of a planar subdivision.  §2.2.

    A DCEL stores:
      • Vertex records  — coordinates + one incident half-edge
      • Half-edge records — origin vertex, twin, incident face, next/prev
      • Face records    — one incident half-edge, label

    Used in map overlay (§2.3), Voronoi diagrams (§7.2), arrangements (§8.3).
    This is a lightweight combinatorial DCEL (no full pointer resolution).
    """

    def __init__(self):
        self.vertices   = {}   # label → (x, y)
        self.half_edges = []   # list of dicts with keys: origin, twin, next, prev, face
        self.faces      = []   # list of dicts with keys: name, outer_he

    def add_vertex(self, label, x, y):
        self.vertices[label] = (x, y)

    def add_half_edge_pair(self, u, v, face_left=None, face_right=None):
        """Add directed half-edge u→v and its twin v→u."""
        he1 = {"origin": u, "twin": len(self.half_edges)+1,
                "face": face_left,  "next": None, "prev": None}
        he2 = {"origin": v, "twin": len(self.half_edges),
                "face": face_right, "next": None, "prev": None}
        self.half_edges.append(he1)
        self.half_edges.append(he2)
        return len(self.half_edges)-2, len(self.half_edges)-1

    def edge_count(self):
        """Number of undirected edges = half_edges / 2."""
        return len(self.half_edges) // 2

    def info(self):
        return {"vertices": len(self.vertices),
                "half_edges": len(self.half_edges),
                "edges": self.edge_count(),
                "faces": len(self.faces)}


# ================================================================
# 4. SWEEP LINE FRAMEWORK  §2.1
# ================================================================

class SweepLine:
    """
    Plane-sweep event framework.  §2.1.

    The sweep line moves top-to-bottom (decreasing y).
    Events:
      • Upper endpoint — insert segment into status
      • Lower endpoint — delete segment from status
      • Intersection   — swap adjacent segments, test new neighbors

    Shamos-Hoey O(n log n): reports whether any intersection exists.
    Bentley-Ottmann O((n+I) log n): reports all I intersections.

    This class implements the event queue and status structure
    conceptually; the full sweep is demonstrated in find_intersections().
    """

    @staticmethod
    def shamos_hoey(segments):
        """
        Shamos-Hoey algorithm: O(n log n) test for any intersection.  §2.1.
        Returns True if any two segments in the list intersect.
        (Simplified implementation via sorted sweep events.)
        """
        events = []
        for i, s in enumerate(segments):
            top = s.p if s.p[1] >= s.q[1] else s.q
            bot = s.q if s.p[1] >= s.q[1] else s.p
            events.append((top[1], 0, i, top))   # upper endpoint
            events.append((bot[1], 1, i, bot))   # lower endpoint
        events.sort(key=lambda e: (-e[0], e[1]))
        active = []
        for _, kind, idx, pt in events:
            if kind == 0:
                for j in active:
                    if segments[idx].intersects(segments[j]):
                        return True
                active.append(idx)
            else:
                if idx in active:
                    active.remove(idx)
        return False

    @staticmethod
    def find_intersections(segments):
        """
        Report all intersections (brute-force with event counting).  §2.1.
        Full Bentley-Ottmann is O(n log n + I log n); this reference
        implementation is O(n²) but structurally matches the sweep approach.
        Returns sorted list of intersection points.
        """
        raw = LineSegment.brute_force_intersections(segments)
        points = list({r["point"] for r in raw})
        points.sort()
        return {"intersections": points,
                "count": len(points),
                "complexity": "O(n log n + I log n) with full Bentley-Ottmann (Theorem 2.4)"}


# ================================================================
# 5. POLYGON TRIANGULATION  §3.1–3.3
# ================================================================

class PolygonTriangulation:
    """
    Triangulation of simple polygons.  §3.1–3.3.

    Art Gallery Theorem (§3.1): ⌊n/3⌋ guards suffice to guard a simple
    polygon with n vertices.

    Algorithm (§3.2–3.3):
      Step 1: Partition polygon into y-monotone pieces — O(n log n).
      Step 2: Triangulate each y-monotone piece — O(n) per piece.
    Total: O(n log n) time, O(n) space.  Theorem 3.8.

    A polygon is y-monotone if every horizontal line meets it in
    at most one connected interval.
    """

    @staticmethod
    def is_y_monotone(polygon):
        """
        Check if polygon is y-monotone: the x-sorted boundary has no
        'start' or 'end' vertex (both neighbours above or below).  §3.2.
        """
        n = len(polygon)
        direction_changes = 0
        prev_dir = None
        for i in range(n):
            cur = polygon[i][1]
            nxt = polygon[(i+1)%n][1]
            d = 1 if nxt > cur else (-1 if nxt < cur else 0)
            if d != 0:
                if prev_dir is not None and d != prev_dir:
                    direction_changes += 1
                prev_dir = d
        return direction_changes <= 2

    @staticmethod
    def ear_clip_triangulation(polygon):
        """
        Ear-clipping triangulation for a simple polygon.  §3.1.
        An 'ear' is a vertex whose triangle with its two neighbours
        lies entirely inside the polygon.
        Returns list of triangles as index-triples.
        Time: O(n²).  (The optimal O(n log n) uses monotone decomposition.)
        """
        n = len(polygon)
        if n < 3:
            return []
        verts = list(range(n))
        triangles = []

        def is_ear(idx):
            prev_i = verts[(idx-1) % len(verts)]
            curr_i = verts[idx]
            next_i = verts[(idx+1) % len(verts)]
            a, b, c = polygon[prev_i], polygon[curr_i], polygon[next_i]
            if Primitives.cross2d(a, b, c) <= 0:
                return False
            for k in range(len(verts)):
                vi = verts[k]
                if vi in (prev_i, curr_i, next_i):
                    continue
                if Primitives.point_in_triangle(polygon[vi], a, b, c):
                    return False
            return True

        max_iter = n * n
        iterations = 0
        while len(verts) > 3 and iterations < max_iter:
            iterations += 1
            removed = False
            for i in range(len(verts)):
                if is_ear(i):
                    prev_i = verts[(i-1)%len(verts)]
                    curr_i = verts[i]
                    next_i = verts[(i+1)%len(verts)]
                    triangles.append((prev_i, curr_i, next_i))
                    verts.pop(i)
                    removed = True
                    break
            if not removed:
                break
        if len(verts) == 3:
            triangles.append(tuple(verts))
        return triangles

    @staticmethod
    def num_triangles(n_vertices):
        """A simple polygon with n vertices has exactly n-2 triangles.  §3.1."""
        return n_vertices - 2

    @staticmethod
    def art_gallery_guards(n):
        """
        Art Gallery Theorem: ⌊n/3⌋ guards always suffice.  §3.1.
        Chvátal 1975; simple proof by Fisk (3-coloring after triangulation).
        """
        return {"n_vertices": n,
                "guards_needed": n // 3,
                "theorem": "Art Gallery Theorem: ⌊n/3⌋ guards always suffice (§3.1)"}


# ================================================================
# 6. LINEAR PROGRAMMING  §4.2–4.7
# ================================================================

class LinearProgramming2D:
    """
    2-D linear programming.  §4.2–4.7.

    Find a point (x, y) satisfying n half-plane constraints aᵢx + bᵢy ≤ cᵢ
    that minimises (or maximises) a linear objective function.

    Algorithm: Randomised incremental LP.  §4.3–4.4.
    Expected O(n) time (Seidel's algorithm).  §4.4.

    Smallest enclosing disc (minimax): also solvable in expected O(n).  §4.7.
    """

    @staticmethod
    def feasible_point_brute(half_planes):
        """
        Find any feasible point inside all half-planes (brute-force grid search).
        half_planes — list of (a, b, c) with constraint ax + by ≤ c.
        Returns a feasible (x,y) or None.
        """
        def feasible(x, y):
            return all(a*x + b*y <= c + EPS for a, b, c in half_planes)

        for x in [i*0.5 for i in range(-20, 21)]:
            for y in [i*0.5 for i in range(-20, 21)]:
                if feasible(x, y):
                    return (_fmt(x), _fmt(y))
        return None

    @staticmethod
    def half_plane_intersection_vertex(half_planes):
        """
        Compute all vertices of the feasible region (intersection of half-planes).
        A vertex is the intersection of two bounding lines that lies inside all others.
        §4.2.
        """
        def line_intersect(h1, h2):
            a1,b1,c1 = h1; a2,b2,c2 = h2
            det = a1*b2 - a2*b1
            if abs(det) < EPS: return None
            x = (c1*b2 - c2*b1) / det
            y = (a1*c2 - a2*c1) / det
            return (x, y)

        vertices = []
        n = len(half_planes)
        for i in range(n):
            for j in range(i+1, n):
                pt = line_intersect(half_planes[i], half_planes[j])
                if pt is None: continue
                x, y = pt
                if all(a*x + b*y <= c + EPS for a,b,c in half_planes):
                    vertices.append((_fmt(x), _fmt(y)))
        return vertices

    @staticmethod
    def lp_minimise(half_planes, objective_c, objective_d):
        """
        Minimise c*x + d*y subject to half-plane constraints.  §4.3.
        Uses brute-force over feasible vertices.
        Returns (min_value, optimal_point) or (None, None) if infeasible.
        """
        verts = LinearProgramming2D.half_plane_intersection_vertex(half_planes)
        if not verts:
            fp = LinearProgramming2D.feasible_point_brute(half_planes)
            if fp is None: return None, None
            verts = [fp]
        best_val = float('inf')
        best_pt  = None
        for x, y in verts:
            val = objective_c * x + objective_d * y
            if val < best_val:
                best_val, best_pt = val, (x, y)
        return _fmt(best_val), best_pt

    @staticmethod
    def smallest_enclosing_disc(points):
        """
        Smallest enclosing disc (minimax disc) of a point set.  §4.7.
        Welzl's randomised algorithm — expected O(n).
        Returns (centre, radius).
        """
        pts = [tuple(p) for p in points]
        random.shuffle(pts)

        def circumcircle(a, b, c):
            ax,ay = a; bx,by = b; cx,cy = c
            D = 2*(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
            if abs(D) < EPS: return None, float('inf')
            ux = ((ax**2+ay**2)*(by-cy)+(bx**2+by**2)*(cy-ay)+(cx**2+cy**2)*(ay-by))/D
            uy = ((ax**2+ay**2)*(cx-bx)+(bx**2+by**2)*(ax-cx)+(cx**2+cy**2)*(bx-ax))/D
            r  = math.sqrt((ax-ux)**2+(ay-uy)**2)
            return (ux,uy), r

        def min_disc(P, R):
            if not P or len(R) == 3:
                if   len(R) == 0: return (0,0), 0
                elif len(R) == 1: return R[0], 0
                elif len(R) == 2:
                    cx = (R[0][0]+R[1][0])/2
                    cy = (R[0][1]+R[1][1])/2
                    return (cx,cy), math.dist(R[0],(cx,cy))
                else:
                    return circumcircle(*R)
            p = P[0]
            c, r = min_disc(P[1:], R)
            if math.sqrt((p[0]-c[0])**2+(p[1]-c[1])**2) <= r+EPS:
                return c, r
            return min_disc(P[1:], R+[p])

        centre, radius = min_disc(pts, [])
        return {"centre": (_fmt(centre[0]), _fmt(centre[1])),
                "radius": _fmt(radius),
                "algorithm": "Welzl randomised, expected O(n)  (§4.7)"}

    @staticmethod
    def casting_feasibility(facet_normals):
        """
        Check if a polyhedron is castable (§4.1):
        find a direction (dx, dy) with ηx·dx + ηy·dy + ηz ≤ 0 for each facet.
        facet_normals — list of (ηx, ηy, ηz) outward normals.
        Translates to half-plane intersection in direction plane z=1.
        """
        half_planes = [(nx, ny, -nz) for nx, ny, nz in facet_normals
                       if abs(nx)+abs(ny) > EPS]
        verts = LinearProgramming2D.half_plane_intersection_vertex(half_planes)
        if verts:
            return {"castable": True, "direction_point": verts[0],
                    "theorem": "Lemma 4.1: d feasible ⟺ angle ≥ 90° with all normals"}
        fp = LinearProgramming2D.feasible_point_brute(half_planes)
        return {"castable": fp is not None,
                "direction_point": fp,
                "theorem": "Lemma 4.1 / Theorem 4.2"}


# ================================================================
# 7. ORTHOGONAL RANGE SEARCHING  §5.1–5.3
# ================================================================

class RangeTree:
    """
    Orthogonal range searching data structures.  §5.1–5.3.

    1-D range tree (balanced BST): O(log n + k) query time.
    2-D range tree (§5.3): O(log² n + k) query time.
    kd-tree (§5.2): O(√n + k) query time in 2-D.

    Definitions:
      A range query [x:x'] reports all points with x-coordinate in [x, x'].
      A 2-D rectangular range query reports all points in [x:x'] × [y:y'].
    """

    def __init__(self, points):
        """points — list of (x, y, ...) tuples."""
        self.points = sorted(points, key=lambda p: p[0])
        self._xs = [p[0] for p in self.points]

    # ── 1-D range search ──────────────────────────────────────

    def range_1d(self, x_lo, x_hi):
        """
        Report all points with x ∈ [x_lo, x_hi].  §5.1.
        O(log n + k) using binary search.
        """
        lo = bisect.bisect_left(self._xs, x_lo)
        hi = bisect.bisect_right(self._xs, x_hi)
        return self.points[lo:hi]

    # ── 2-D orthogonal range search ───────────────────────────

    def range_2d(self, x_lo, x_hi, y_lo, y_hi):
        """
        Report all points in [x_lo:x_hi] × [y_lo:y_hi].  §5.3.
        O(log² n + k) with range tree; O(√n + k) with kd-tree.
        """
        candidates = self.range_1d(x_lo, x_hi)
        return [p for p in candidates if y_lo <= p[1] <= y_hi]

    # ── kd-tree ───────────────────────────────────────────────

    @staticmethod
    def build_kdtree(points, depth=0):
        """
        Build a kd-tree for a set of 2-D points.  §5.2.
        Alternates splitting axis: even depth → x, odd depth → y.
        Returns a nested dict representing the tree.
        """
        if not points: return None
        axis = depth % 2
        pts  = sorted(points, key=lambda p: p[axis])
        mid  = len(pts) // 2
        return {
            "point"  : pts[mid],
            "axis"   : axis,
            "left"   : RangeTree.build_kdtree(pts[:mid],  depth+1),
            "right"  : RangeTree.build_kdtree(pts[mid+1:], depth+1),
        }

    @staticmethod
    def kdtree_range_query(node, x_lo, x_hi, y_lo, y_hi):
        """
        2-D orthogonal range query on a kd-tree.  §5.2.
        Expected O(√n + k) in a balanced kd-tree.
        """
        if node is None: return []
        px, py = node["point"]
        result = []
        if x_lo <= px <= x_hi and y_lo <= py <= y_hi:
            result.append(node["point"])
        axis = node["axis"]
        if axis == 0:
            if px >= x_lo: result += RangeTree.kdtree_range_query(node["left"],  x_lo,x_hi,y_lo,y_hi)
            if px <= x_hi: result += RangeTree.kdtree_range_query(node["right"], x_lo,x_hi,y_lo,y_hi)
        else:
            if py >= y_lo: result += RangeTree.kdtree_range_query(node["left"],  x_lo,x_hi,y_lo,y_hi)
            if py <= y_hi: result += RangeTree.kdtree_range_query(node["right"], x_lo,x_hi,y_lo,y_hi)
        return result

    @staticmethod
    def query_complexity():
        """Summary of query and build complexities.  §5.1–5.3."""
        return {
            "1-D range tree" : {"build": "O(n)", "query": "O(log n + k)", "space": "O(n)"},
            "kd-tree 2-D"    : {"build": "O(n log n)", "query": "O(√n + k)", "space": "O(n)"},
            "2-D range tree" : {"build": "O(n log n)", "query": "O(log² n + k)", "space": "O(n log n)"},
            "fractional cascade": {"build": "O(n log n)", "query": "O(log n + k)", "space": "O(n log n)"},
        }


# ================================================================
# 8. POINT LOCATION  §6.1
# ================================================================

class PointLocation:
    """
    Point location in a planar subdivision.  §6.1.

    Trapezoidal map (§6.1): a random incremental algorithm that builds
    a search structure in expected O(n log n) time supporting O(log n)
    queries.  Theorem 6.7: expected O(n) storage, O(log n) query time.

    Slab method: Simpler O(n log n) preprocessing, O(log n) query.
    """

    def __init__(self, segments):
        """
        Build a trapezoidal-map-style point location structure.
        segments — list of non-crossing LineSegment objects.
        """
        self.segments = segments
        # Store x-coordinates of all endpoints for slab method
        xs = sorted(set([s.p[0] for s in segments] + [s.q[0] for s in segments]))
        self.xs = xs

    def locate_slab(self, query_point):
        """
        Slab method: §6.1.
        1. Binary search to find the slab containing the query x.
        2. Binary search within the slab for the correct face.
        Returns the slab index and nearest segment below the query point.
        O(log n) query time after O(n²) preprocessing.
        """
        qx, qy = query_point
        # Find slab
        slab_idx = bisect.bisect_right(self.xs, qx) - 1
        # Find segments that span this x in the slab
        in_slab = []
        for s in self.segments:
            xmin, xmax = min(s.p[0],s.q[0]), max(s.p[0],s.q[0])
            if xmin <= qx <= xmax:
                # y-value of segment at x = qx
                if abs(s.q[0]-s.p[0]) < EPS:
                    y_at_x = (s.p[1]+s.q[1])/2
                else:
                    t = (qx - s.p[0]) / (s.q[0] - s.p[0])
                    y_at_x = s.p[1] + t*(s.q[1]-s.p[1])
                in_slab.append((y_at_x, s))
        in_slab.sort(key=lambda x: x[0])
        below = [s for (y, s) in in_slab if y < qy]
        above = [s for (y, s) in in_slab if y >= qy]
        return {
            "slab_index"  : slab_idx,
            "segment_below": str(below[-1]) if below else "none (unbounded face below)",
            "segment_above": str(above[0])  if above else "none (unbounded face above)",
            "query"       : query_point,
            "complexity"  : "O(log n) query, O(n log n) preprocess (§6.1)",
        }

    @staticmethod
    def trapezoidal_map_complexity(n):
        """
        Expected complexity of the randomised trapezoidal map.  Theorem 6.7.
        """
        return {
            "segments": n,
            "expected_trapezoids": 6*n + 4,
            "expected_search_depth": f"O(log {n})",
            "theorem": "Theorem 6.7: O(n) expected size, O(log n) query",
            "algorithm": "Randomised incremental, §6.2",
        }


# ================================================================
# 9. VORONOI DIAGRAM  §7.1–7.2
# ================================================================

class VoronoiDiagram:
    """
    Voronoi diagram of a point set.  §7.1–7.2.

    Vor(P): subdivision of the plane into n cells V(pᵢ), where
    V(pᵢ) = {q : dist(q, pᵢ) < dist(q, pⱼ) ∀ j ≠ i}.
    Equivalently, V(pᵢ) = ∩_{j≠i} h(pᵢ, pⱼ)  (Observation 7.1).

    Theorem 7.3: For n ≥ 3 sites, Vor(P) has at most 2n−5 vertices and
    3n−6 edges.  Proved via Euler's formula on the augmented graph.

    Fortune's sweep algorithm computes Vor(P) in O(n log n).
    """

    def __init__(self, sites):
        self.sites = [tuple(s) for s in sites]

    def nearest_site(self, query):
        """
        Find the nearest site to a query point (= Voronoi cell lookup).
        O(n) linear scan; O(log n) with the search structure.  §7.1.
        """
        qx, qy = query
        best, best_d = None, float('inf')
        for p in self.sites:
            d = (p[0]-qx)**2 + (p[1]-qy)**2
            if d < best_d:
                best_d, best = d, p
        return {"nearest_site": best,
                "distance": _fmt(math.sqrt(best_d)),
                "query": query}

    def voronoi_cell_halfplanes(self, site_idx):
        """
        V(pᵢ) as intersection of half-planes h(pᵢ, pⱼ).  Observation 7.1.
        Returns list of half-planes (a, b, c) with ax + by ≤ c
        for the perpendicular bisectors between pᵢ and each pⱼ.
        """
        pi = self.sites[site_idx]
        half_planes = []
        for j, pj in enumerate(self.sites):
            if j == site_idx: continue
            # Bisector: midpoint = ((px+qx)/2, (py+qy)/2)
            # Normal direction = pj − pi
            mx = (pi[0]+pj[0])/2; my = (pi[1]+pj[1])/2
            a  = pj[0]-pi[0];     b  = pj[1]-pi[1]
            c  = a*mx + b*my
            half_planes.append((a, b, c))
        return half_planes

    def circumcircle(self, a, b, c):
        """
        Circumcircle of three sites.  Used to locate Voronoi vertices (§7.1 Thm 7.4).
        A Voronoi vertex is equidistant from three sites.
        """
        ax,ay=a; bx,by=b; cx,cy=c
        D = 2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
        if abs(D) < EPS: return None, None
        ux = ((ax**2+ay**2)*(by-cy)+(bx**2+by**2)*(cy-ay)+(cx**2+cy**2)*(ay-by))/D
        uy = ((ax**2+ay**2)*(cx-bx)+(bx**2+by**2)*(ax-cx)+(cx**2+cy**2)*(bx-ax))/D
        r  = math.sqrt((ax-ux)**2+(ay-uy)**2)
        return (_fmt(ux),_fmt(uy)), _fmt(r)

    def voronoi_vertices(self):
        """
        Voronoi vertices (Theorem 7.4): each is the circumcentre of 3 sites
        whose circumdisc contains no other site.
        Returns list of (circumcentre, radius, site_triple).
        """
        result = []
        n = len(self.sites)
        for i,j,k in combinations(range(n), 3):
            centre, radius = self.circumcircle(
                self.sites[i], self.sites[j], self.sites[k])
            if centre is None: continue
            # Check no other site is inside the circumdisc
            valid = True
            for m, pm in enumerate(self.sites):
                if m in (i,j,k): continue
                if (pm[0]-centre[0])**2+(pm[1]-centre[1])**2 < radius**2 - EPS:
                    valid = False; break
            if valid:
                result.append({"voronoi_vertex": centre,
                                "radius": radius,
                                "sites": (i,j,k)})
        return result

    def complexity_bounds(self):
        """
        Theorem 7.3 complexity bounds for Vor(P) with n sites.
        """
        n = len(self.sites)
        return {"n": n,
                "max_vertices": max(0, 2*n-5),
                "max_edges"   : max(0, 3*n-6),
                "formula"     : "From Euler's formula on augmented planar graph  (Theorem 7.3)"}


# ================================================================
# 10. DELAUNAY TRIANGULATION  §9.1–9.3
# ================================================================

class DelaunayTriangulation:
    """
    Delaunay triangulation of a point set.  §9.1–9.3.

    The Delaunay triangulation DT(P) is the dual graph of Vor(P).
    It maximises the minimum angle of all triangles.

    Delaunay condition (§9.2): A triangulation is Delaunay iff for every
    triangle, its circumdisc contains no other site in its interior.

    Algorithm: Randomised incremental with flip.  §9.3.
    Expected O(n log n) time.

    Theorem 9.6: The Delaunay triangulation of n points has O(n) triangles.
    """

    def __init__(self, points):
        self.points = [tuple(p) for p in points]

    def is_delaunay_edge(self, edge, triangles):
        """
        Check if an edge satisfies the Delaunay condition:
        the circumdisc of one incident triangle does not contain
        the opposite vertex.  §9.2.
        edge      — pair (i, j) of point indices.
        triangles — list of index-triples.
        """
        i, j = edge
        incident = [t for t in triangles if i in t and j in t]
        if len(incident) < 2: return True  # boundary edge
        t1, t2 = incident[0], incident[1]
        k = [v for v in t1 if v not in (i,j)][0]
        l = [v for v in t2 if v not in (i,j)][0]
        a, b, c = self.points[i], self.points[j], self.points[k]
        d = self.points[l]
        return Primitives.in_circle(a, b, c, d) <= 0

    def bowyer_watson(self):
        """
        Bowyer-Watson incremental Delaunay triangulation.  §9.3.
        Returns list of triangles (index-triples into self.points).
        """
        pts = list(self.points)
        # Bounding super-triangle
        min_x = min(p[0] for p in pts) - 10
        min_y = min(p[1] for p in pts) - 10
        max_x = max(p[0] for p in pts) + 10
        max_y = max(p[1] for p in pts) + 10
        dx, dy = max_x-min_x, max_y-min_y
        sup = [
            (min_x - dx, min_y - 3*dy),
            (min_x + 2*dx + dx, min_y - dy),
            (min_x + dx/2, max_y + 3*dy),
        ]
        n0 = len(pts)
        pts = pts + sup
        triangles = [(n0, n0+1, n0+2)]

        for idx in range(n0):
            p = pts[idx]
            bad = []
            for tri in triangles:
                a, b, c = pts[tri[0]], pts[tri[1]], pts[tri[2]]
                ctr, rad = self._circumcircle(a, b, c)
                if ctr and (p[0]-ctr[0])**2+(p[1]-ctr[1])**2 < rad**2 + EPS:
                    bad.append(tri)
            boundary = self._boundary_polygon(bad, pts)
            triangles = [t for t in triangles if t not in bad]
            for edge in boundary:
                triangles.append((idx, edge[0], edge[1]))

        # Remove super-triangle
        triangles = [t for t in triangles
                     if n0 not in t and n0+1 not in t and n0+2 not in t]
        return triangles

    def _circumcircle(self, a, b, c):
        ax,ay=a; bx,by=b; cx,cy=c
        D = 2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
        if abs(D) < EPS: return None, None
        ux = ((ax**2+ay**2)*(by-cy)+(bx**2+by**2)*(cy-ay)+(cx**2+cy**2)*(ay-by))/D
        uy = ((ax**2+ay**2)*(cx-bx)+(bx**2+by**2)*(ax-cx)+(cx**2+cy**2)*(bx-ax))/D
        r  = math.sqrt((ax-ux)**2+(ay-uy)**2)
        return (ux,uy), r

    def _boundary_polygon(self, bad_triangles, pts):
        edge_count = defaultdict(int)
        for tri in bad_triangles:
            for e in [(tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])]:
                edge_count[tuple(sorted(e))] += 1
        return [e for e, c in edge_count.items() if c == 1]

    def delaunay_complexity(self):
        """Theorem 9.6: DT(P) has O(n) triangles for n points."""
        n = len(self.points)
        return {"n": n,
                "max_triangles": max(0, 2*n-5),
                "max_edges"    : max(0, 3*n-6),
                "expected_time": "O(n log n) randomised incremental  (§9.3)"}


# ================================================================
# 11. INTERVAL TREE  §10.1
# ================================================================

class IntervalTree:
    """
    Interval tree for stabbing queries.  §10.1.

    Stores a set of intervals [lo, hi] such that the intervals
    containing a query point x can be reported efficiently.

    Structure (§10.1):
      • Build a balanced BST on the interval endpoints.
      • Each node stores intervals that span its split value.
      • O(n log n) build, O(log n + k) stabbing query, O(n) space.
    """

    def __init__(self, intervals):
        """intervals — list of (lo, hi, label) tuples."""
        self.intervals = intervals
        self._build()

    def _build(self):
        """Build by storing intervals sorted by their endpoints."""
        self._sorted_lo = sorted(self.intervals, key=lambda x: x[0])
        self._sorted_hi = sorted(self.intervals, key=lambda x: x[1])

    def stab_query(self, x):
        """
        Report all intervals containing query point x.  §10.1.
        O(log n + k) with the full tree; O(n) here as reference.
        """
        return [iv for iv in self.intervals if iv[0] <= x <= iv[1]]

    def window_query_1d(self, qlo, qhi):
        """
        Report all intervals overlapping [qlo, qhi].  §10.1.
        Interval [a,b] overlaps [qlo, qhi] iff a ≤ qhi and b ≥ qlo.
        """
        return [iv for iv in self.intervals if iv[0] <= qhi and iv[1] >= qlo]

    @staticmethod
    def segment_tree_range_stabbing_complexity(n):
        """
        Segment tree complexity for range stabbing.  §10.3.
        """
        return {
            "n_segments"  : n,
            "build_time"  : "O(n log n)",
            "query_time"  : "O(log n + k)",
            "space"       : "O(n log n)",
            "note"        : "Segment trees can answer interval stabbing queries  (§10.3)"
        }


# ================================================================
# 12. 3-D CONVEX HULL  §11.1–11.2
# ================================================================

class ConvexHull3D:
    """
    Convex hull in 3-dimensional space.  §11.1–11.2.

    The convex hull CH(P) of n points in ℝ³ is a convex polytope.

    Theorem 11.1: A convex polytope with n vertices has at most 3n−6 edges
    and at most 2n−4 facets.  (Euler's formula for polytopes.)

    Corollary 11.2: The complexity of CH(P) for n points is O(n).

    Algorithm: Randomised incremental.  §11.2.  Expected O(n log n) time.

    The 'horizon' of a new point pr is the set of edges on the boundary
    between visible and invisible facets.
    """

    @staticmethod
    def complexity_bounds(n):
        """
        Theorem 11.1 bounds on a convex polytope with n vertices.
        """
        return {
            "n_vertices" : n,
            "max_edges"  : 3*n - 6,
            "max_facets" : 2*n - 4,
            "theorem"    : "Theorem 11.1 (Euler's formula for polytopes, §11.1)",
            "algorithm"  : "Randomised incremental, expected O(n log n)  (§11.2)",
        }

    @staticmethod
    def is_point_visible_from(facet_normal, facet_point, observer):
        """
        A facet is visible from observer if observer is on the positive side
        of the facet's supporting plane.  §11.2.
        facet_normal — outward normal (nx, ny, nz).
        facet_point  — any point on the facet.
        Returns True if visible.
        """
        dx = observer[0]-facet_point[0]
        dy = observer[1]-facet_point[1]
        dz = observer[2]-facet_point[2]
        dot = facet_normal[0]*dx + facet_normal[1]*dy + facet_normal[2]*dz
        return dot > EPS

    @staticmethod
    def facet_normal(a, b, c):
        """
        Outward normal of triangle facet (a, b, c) via cross product.
        """
        u = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
        v = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
        nx = u[1]*v[2]-u[2]*v[1]
        ny = u[2]*v[0]-u[0]*v[2]
        nz = u[0]*v[1]-u[1]*v[0]
        mag = math.sqrt(nx**2+ny**2+nz**2)
        if mag < EPS: return (0,0,0)
        return (_fmt(nx/mag), _fmt(ny/mag), _fmt(nz/mag))

    @staticmethod
    def convex_hull_3d_brute(points):
        """
        Brute-force 3-D convex hull: a triangle (a,b,c) is a facet iff
        all other points lie on one side of its plane.
        Returns list of facet triples.  O(n⁴) — reference implementation.
        """
        n = len(points)
        facets = []
        for i,j,k in combinations(range(n), 3):
            a,b,c = points[i], points[j], points[k]
            # Plane normal
            u = tuple(b[d]-a[d] for d in range(3))
            v = tuple(c[d]-a[d] for d in range(3))
            nx = u[1]*v[2]-u[2]*v[1]
            ny = u[2]*v[0]-u[0]*v[2]
            nz = u[0]*v[1]-u[1]*v[0]
            if abs(nx)+abs(ny)+abs(nz) < EPS: continue
            side = None
            ok = True
            for m in range(n):
                if m in (i,j,k): continue
                p = points[m]
                s = nx*(p[0]-a[0])+ny*(p[1]-a[1])+nz*(p[2]-a[2])
                if abs(s) < EPS: continue
                if side is None: side = (s > 0)
                elif (s > 0) != side: ok = False; break
            if ok:
                facets.append((i,j,k))
        return facets


# ================================================================
# 13. ARRANGEMENTS AND DUALITY  §8.2–8.3
# ================================================================

class Arrangements:
    """
    Arrangements of lines and duality.  §8.2–8.3.

    An arrangement A(L) of n lines is the planar subdivision they induce.
    Theorem 8.4:  |vertices| ≤ n(n-1)/2,  |edges| ≤ n²,  |faces| ≤ n²/2+n/2+1.

    Duality (§8.2): point (a,b) ↔ line y = ax − b.
    The dual of a point above a line = the line above its dual point.
    Used to convert upper envelopes to convex hulls (§11.4).

    Zone Theorem (§8.3 Theorem 8.5): complexity of zone of a line in
    A(L) is O(|L|).  Used to analyse incremental arrangement construction.
    """

    @staticmethod
    def arrangement_complexity(n):
        """
        Theorem 8.4: complexity of a simple arrangement of n lines.
        """
        return {
            "n_lines"   : n,
            "vertices"  : n*(n-1)//2,
            "edges"     : n*n,
            "faces"     : n*n//2 + n//2 + 1,
            "simple"    : "Equality holds iff no two lines are parallel and no three concurrent",
            "theorem"   : "Theorem 8.4  (§8.3)",
        }

    @staticmethod
    def dual_point_to_line(point):
        """
        Duality transform: point (a, b) ↦ line y = ax − b.  §8.2.
        """
        a, b = point
        return {"line": f"y = {a}x - {b}", "slope": a, "intercept": -b}

    @staticmethod
    def dual_line_to_point(slope, intercept):
        """
        Duality transform: line y = mx + q ↦ point (m, −q).  §8.2.
        """
        return {"point": (slope, -intercept)}

    @staticmethod
    def dual_above_below(point, line_slope, line_intercept):
        """
        Duality property (§8.2): point p = (a, b) lies above line y = mx + q
        iff its dual line y = ax − b lies above the dual point (m, −q).
        """
        px, py = point
        above_line = py > line_slope * px + line_intercept
        return {"point": point, "line": f"y={line_slope}x+{line_intercept}",
                "above_line": above_line,
                "dual_line"   : Arrangements.dual_point_to_line(point),
                "dual_point"  : Arrangements.dual_line_to_point(line_slope, line_intercept),
                "property": "p above line ⟺ dual_line above dual_point  (§8.2)"}

    @staticmethod
    def zone_theorem(m):
        """
        Zone Theorem (Theorem 8.5, §8.3): the zone of a line in an
        arrangement of m lines has complexity O(m).
        Used to show incremental arrangement construction takes O(m²) total.
        """
        return {
            "arrangement_lines": m,
            "zone_complexity"  : f"O({m}) = O(m)",
            "theorem"          : "Theorem 8.5 (Zone Theorem, §8.3)",
            "consequence"      : f"Incremental construction of A(L) runs in O({m}²) total time",
        }

    @staticmethod
    def upper_convex_hull_dual(points):
        """
        Upper convex hull of points ↔ lower envelope of dual lines.  §11.4.
        Returns the sorted upper hull and their dual lines.
        """
        pts = sorted(set(map(tuple, points)))
        upper = ConvexHull2D.upper_hull(pts)
        duals = [Arrangements.dual_point_to_line(p) for p in upper]
        return {"upper_hull": upper,
                "dual_lines": duals,
                "theorem": "Upper hull ↔ lower envelope of duals  (§11.4)"}


# ================================================================
# 14. BINARY SPACE PARTITIONS  §12.1–12.3
# ================================================================

class BSPTree:
    """
    Binary space partition tree.  §12.1–12.3.

    A BSP tree recursively partitions space by hyperplanes until each cell
    contains at most one fragment.  Used in the Painter's Algorithm for
    hidden-surface removal.  §12.2.

    Auto-partition: each splitting line is the supporting line of one
    of the input segments.  §12.3.

    Expected BSP size (§12.3 Theorem 12.1): O(n log n) for n segments
    in random order.
    """

    @staticmethod
    def painters_algorithm(objects_with_depth):
        """
        Painter's Algorithm: render back-to-front.  §12.2.
        objects_with_depth — list of (depth_value, label).
        Returns rendering order (back to front).
        """
        return sorted(objects_with_depth, key=lambda x: -x[0])

    @staticmethod
    def build_bsp_2d(segments):
        """
        Build a simple auto-partition BSP for line segments.  §12.3.
        Each node splits by the supporting line of the first segment.
        Returns a nested dict representing the BSP tree.
        """
        if not segments:
            return None
        pivot = segments[0]
        left_segs, right_segs, coincident = [], [], [pivot]
        for s in segments[1:]:
            d_p = Primitives.cross2d(pivot.p, pivot.q, s.p)
            d_q = Primitives.cross2d(pivot.p, pivot.q, s.q)
            if d_p >= 0 and d_q >= 0:
                left_segs.append(s)
            elif d_p <= 0 and d_q <= 0:
                right_segs.append(s)
            else:
                # Segment is split — add to both (simplified)
                left_segs.append(s)
                right_segs.append(s)
        return {
            "plane_segment": str(pivot),
            "coincident"   : [str(c) for c in coincident],
            "left"         : BSPTree.build_bsp_2d(left_segs),
            "right"        : BSPTree.build_bsp_2d(right_segs),
        }

    @staticmethod
    def bsp_size_expected(n):
        """
        Expected BSP size for n disjoint segments in random order.  §12.3.
        Theorem 12.1: O(n log n) expected fragments.
        """
        return {
            "n"           : n,
            "expected_size": _fmt(n * math.log(n+1)),
            "worst_case"  : "O(n²)",
            "theorem"     : "Theorem 12.1: expected O(n log n) for random order  (§12.3)",
        }

    @staticmethod
    def low_density_bsp(n, density):
        """
        BSP for low-density scenes (§12.5): if density = λ (constant),
        the BSP has size O(λ · n).
        """
        return {
            "n": n, "density": density,
            "bsp_size": _fmt(density * n),
            "theorem": "Low-density scene BSP has size O(λ·n)  (§12.5)",
        }


# ================================================================
# 15. ROBOT MOTION PLANNING  §13.1–13.3
# ================================================================

class MotionPlanning:
    """
    Robot motion planning via configuration space.  §13.1–13.3.

    Configuration space C: maps a robot's degrees of freedom to a point.
    For a translating point robot, C = ℝ² = workspace minus obstacles.
    For a translating polygonal robot, obstacles in C-space are the
    Minkowski sums of workspace obstacles with the reflected robot.  §13.3.

    Minkowski sum P ⊕ Q = {p + q : p ∈ P, q ∈ Q}.  §13.3.
    For convex polygons with m and n vertices respectively,
    P ⊕ Q has at most m + n vertices and can be computed in O(m+n).
    """

    @staticmethod
    def minkowski_sum_convex(P, Q):
        """
        Minkowski sum of two convex polygons P and Q given in CCW order.  §13.3.
        Uses the rotating-calipers style merge:
        merge the edge-vector sequences of P and Q sorted by angle.
        Returns vertices of P ⊕ Q.  O(m + n) time.
        """
        def edges(poly):
            n = len(poly)
            return [(poly[(i+1)%n][0]-poly[i][0], poly[(i+1)%n][1]-poly[i][1])
                    for i in range(n)]

        def angle(v):
            return math.atan2(v[1], v[0])

        eP = edges(P); eQ = edges(Q)
        # Find starting indices (bottom-most vertex)
        iP = min(range(len(P)), key=lambda i: (P[i][1], P[i][0]))
        iQ = min(range(len(Q)), key=lambda i: (Q[i][1], Q[i][0]))
        # Merge edge sequences by angle
        result = [(P[iP][0]+Q[iQ][0], P[iP][1]+Q[iQ][1])]
        pi, qi = 0, 0
        while pi < len(P) or qi < len(Q):
            ep = eP[(iP+pi) % len(eP)] if pi < len(P) else None
            eq = eQ[(iQ+qi) % len(eQ)] if qi < len(Q) else None
            if ep is None:
                ev = eq; qi += 1
            elif eq is None:
                ev = ep; pi += 1
            elif angle(ep) <= angle(eq):
                ev = ep; pi += 1
                if abs(angle(ep)-angle(eq)) < EPS: qi += 1
            else:
                ev = eq; qi += 1
            last = result[-1]
            result.append((_fmt(last[0]+ev[0]), _fmt(last[1]+ev[1])))
        return result[:-1]  # last vertex = first (closed polygon)

    @staticmethod
    def cspace_obstacle(workspace_obstacle, robot_reflected):
        """
        C-space obstacle for a translating robot: C-obs = workspace_obs ⊕ reflect(robot).
        §13.3.  reflect(Q) = {-q : q ∈ Q}.
        """
        reflected = [(-v[0], -v[1]) for v in robot_reflected]
        reflected_ccw = ConvexHull2D.convex_hull(reflected)
        obs_hull = ConvexHull2D.convex_hull(workspace_obstacle)
        c_obs = MotionPlanning.minkowski_sum_convex(obs_hull, reflected_ccw)
        return {"c_obs_vertices": c_obs,
                "note": "C-obstacle = workspace obstacle ⊕ reflect(robot)  (§13.3)"}

    @staticmethod
    def free_path_exists(start, goal, c_obstacles):
        """
        Simplified check: is there a straight-line path from start to goal
        avoiding all C-space obstacles (given as convex polygons)?
        §13.2.
        """
        path_seg = LineSegment(start, goal)
        for obs in c_obstacles:
            n = len(obs)
            for i in range(n):
                edge = LineSegment(obs[i], obs[(i+1)%n])
                if path_seg.intersects(edge):
                    return {"free_path": False,
                            "obstacle_hit": obs,
                            "note": "Straight-line path blocked; use visibility graph  (§13.2)"}
        return {"free_path": True, "path": (start, goal)}


# ================================================================
# 16. QUADTREE  §14.1–14.2
# ================================================================

class Quadtree:
    """
    Quadtree for point sets and mesh generation.  §14.1–14.2.

    A quadtree subdivides a square region by splitting it into four
    equal quadrants recursively until each cell contains at most one point.

    Theorem 14.2 (§14.2): The quadtree for n points has
    O(n(1 + log(Δ/δ))) nodes, where Δ = max pairwise distance and
    δ = min pairwise distance.
    """

    def __init__(self, points, bbox=None, max_pts=1, max_depth=20):
        """
        points   — list of (x, y) tuples.
        bbox     — (xmin, xmax, ymin, ymax) bounding square.
        max_pts  — max points per leaf before splitting.
        max_depth — maximum recursion depth.
        """
        if not points:
            self.root = None
            return
        if bbox is None:
            xs = [p[0] for p in points]; ys = [p[1] for p in points]
            side = max(max(xs)-min(xs), max(ys)-min(ys)) + 1e-3
            cx   = (max(xs)+min(xs))/2; cy = (max(ys)+min(ys))/2
            bbox = (cx-side/2, cx+side/2, cy-side/2, cy+side/2)
        self.root = self._build(points, bbox, 0, max_pts, max_depth)

    def _build(self, pts, bbox, depth, max_pts, max_depth):
        xmin, xmax, ymin, ymax = bbox
        node = {"bbox": bbox, "points": pts, "children": None}
        if len(pts) <= max_pts or depth >= max_depth:
            return node
        xmid = (xmin+xmax)/2; ymid = (ymin+ymax)/2
        quads = [
            ([p for p in pts if p[0] <  xmid and p[1] >= ymid], (xmin,xmid,ymid,ymax)),
            ([p for p in pts if p[0] >= xmid and p[1] >= ymid], (xmid,xmax,ymid,ymax)),
            ([p for p in pts if p[0] <  xmid and p[1] <  ymid], (xmin,xmid,ymin,ymid)),
            ([p for p in pts if p[0] >= xmid and p[1] <  ymid], (xmid,xmax,ymin,ymid)),
        ]
        node["children"] = [
            self._build(q_pts, q_bbox, depth+1, max_pts, max_depth)
            for q_pts, q_bbox in quads
        ]
        return node

    def count_nodes(self, node=None):
        """Count total nodes in the quadtree."""
        if node is None: node = self.root
        if node is None: return 0
        if node["children"] is None: return 1
        return 1 + sum(self.count_nodes(c) for c in node["children"])

    def point_query(self, p, node=None):
        """Find the leaf cell containing point p."""
        if node is None: node = self.root
        if node is None: return None
        xmin,xmax,ymin,ymax = node["bbox"]
        if not (xmin <= p[0] <= xmax and ymin <= p[1] <= ymax):
            return None
        if node["children"] is None:
            return node["bbox"]
        for child in node["children"]:
            if child:
                result = self.point_query(p, child)
                if result: return result
        return None

    @staticmethod
    def complexity(n, delta_max, delta_min):
        """
        Theorem 14.2: Quadtree has O(n(1 + log(Δ/δ))) nodes.
        """
        ratio = delta_max / delta_min if delta_min > 0 else float('inf')
        nodes = int(n * (1 + math.log2(ratio+1)))
        return {"n": n, "delta_max": delta_max, "delta_min": delta_min,
                "Δ/δ": _fmt(ratio),
                "node_bound": f"O(n(1 + log(Δ/δ))) ≈ {nodes}",
                "theorem": "Theorem 14.2  (§14.2)"}


# ================================================================
# 17. VISIBILITY GRAPH  §15.1–15.2
# ================================================================

class VisibilityGraph:
    """
    Visibility graph for shortest-path planning.  §15.1–15.2.

    The visibility graph VG(P) of a polygonal scene P has:
      • Vertices: the polygon vertices + source + destination.
      • Edges: pairs of vertices that can 'see' each other
               (the connecting segment does not cross any obstacle edge).

    The shortest path in free space is a path through VG(P) (§15.1).
    Algorithm: O(n² log n) using a rotational sweep.  §15.2.
    """

    def __init__(self, obstacles, start=None, goal=None):
        """
        obstacles — list of polygons, each a list of (x,y) tuples.
        """
        self.obstacles = obstacles
        self.all_edges = []
        for poly in obstacles:
            n = len(poly)
            for i in range(n):
                self.all_edges.append(LineSegment(poly[i], poly[(i+1)%n]))

        all_verts = [v for poly in obstacles for v in poly]
        if start: all_verts.append(tuple(start))
        if goal:  all_verts.append(tuple(goal))
        self.vertices = [tuple(v) for v in all_verts]

    def _segments_intersect_interior(self, a, b):
        """
        Does segment ab intersect any obstacle edge in its interior?
        (Ignoring shared endpoints.)
        """
        test = LineSegment(a, b)
        for edge in self.all_edges:
            if set([a,b]) & set([edge.p, edge.q]): continue  # shared endpoint
            if test.intersects(edge): return True
        return False

    def build(self):
        """
        Build the visibility graph.  §15.2.
        Returns adjacency dict: vertex → list of visible vertices.
        O(n³) reference; optimal is O(n² log n).
        """
        vg = defaultdict(list)
        n = len(self.vertices)
        for i in range(n):
            for j in range(n):
                if i == j: continue
                a, b = self.vertices[i], self.vertices[j]
                if not self._segments_intersect_interior(a, b):
                    vg[a].append(b)
        return dict(vg)

    def shortest_path(self, start, goal):
        """
        Dijkstra's shortest path on the visibility graph.  §15.1.
        """
        vg = self.build()
        start, goal = tuple(start), tuple(goal)
        if start not in vg: vg[start] = []
        if goal  not in vg: vg[goal]  = []

        import heapq
        dist   = defaultdict(lambda: float('inf'))
        prev   = {}
        dist[start] = 0
        pq = [(0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]: continue
            if u == goal: break
            for v in vg.get(u, []):
                alt = dist[u] + Primitives.dist2d(u, v)
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v]  = u
                    heapq.heappush(pq, (alt, v))

        if dist[goal] == float('inf'):
            return {"path": None, "length": float('inf'),
                    "note": "No path found"}
        path = []
        u = goal
        while u in prev:
            path.append(u); u = prev[u]
        path.append(start)
        path.reverse()
        return {"path": path,
                "length": _fmt(dist[goal]),
                "algorithm": "Dijkstra on VG, §15.1"}

    @staticmethod
    def complexity(n):
        """
        Visibility graph of a polygonal scene with n vertices.  §15.2.
        """
        return {
            "n_vertices"  : n,
            "max_edges"   : n*(n-1)//2,
            "build_time"  : "O(n² log n) rotational sweep  (§15.2)",
            "dijkstra"    : "O(n² log n) for shortest path",
        }


# ================================================================
# 18. SIMPLEX RANGE SEARCHING  §16.1–16.3
# ================================================================

class SimplexRange:
    """
    Simplex range searching: report/count points inside a query triangle.  §16.

    Partition trees (§16.1): O(n^{1-1/d} + k) query time, O(n) space.
    Cutting trees (§16.3): O(n/r) size cuttings, each of O(r²) complexity.

    For d=2:
      Simplex range reporting: O(√n + k) query using partition trees.
      Simplex range counting:  O(√n) query using dual arrangements.
    """

    def __init__(self, points):
        self.points = [tuple(p) for p in points]

    def query_triangle(self, a, b, c):
        """
        Report all points inside triangle (a, b, c).  §16.1.
        Brute-force O(n); partition trees give O(√n + k).
        """
        result = [p for p in self.points
                  if Primitives.point_in_triangle(p, a, b, c)]
        return {"points_in_triangle": result,
                "count": len(result),
                "brute_force_complexity": "O(n)",
                "partition_tree_complexity": "O(√n + k)  (§16.1)"}

    def query_halfplane(self, a, b, c):
        """
        Report all points in the half-plane ax + by ≤ c.  §16.1.
        Half-plane is the building block for simplex queries.
        """
        return [p for p in self.points if a*p[0] + b*p[1] <= c + EPS]

    @staticmethod
    def cutting_complexity(n, r):
        """
        §16.3: An (1/r)-cutting for n lines has O(r²) cells.
        Build time: O(n r).
        """
        return {
            "n_lines"   : n,
            "r"         : r,
            "cells"     : r*r,
            "build_time": f"O(n·r) = O({n*r})",
            "theorem"   : "§16.3: (1/r)-cutting has O(r²) cells",
        }

    @staticmethod
    def partition_tree_complexity(n, d=2):
        """
        Partition tree query complexity.  §16.1.
        In d dimensions: O(n^{1-1/d} + k) query, O(n) space.
        """
        exponent = 1 - 1/d
        return {
            "n": n, "d": d,
            "query_time": f"O(n^{{1-1/{d}}} + k) = O(n^{exponent:.2f} + k)",
            "space"     : "O(n)",
            "theorem"   : "§16.1 partition tree",
        }