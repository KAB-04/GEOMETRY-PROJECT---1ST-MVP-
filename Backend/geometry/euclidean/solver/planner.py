from .exceptions import InvalidParametersError
from .Solver import INVALID_GEOMETRY_PARAMETERS_MESSAGE
from ..parser.exceptions import UnsupportedGeometryOperation


class SolutionPlanner:
    def __init__(self, solver):
        self.solver = solver

    def solve(self, semantic_problem):
        geometry_type = semantic_problem.get("geometry_type")
        if geometry_type == "cone":
            return self._solve_cone(semantic_problem)
        if geometry_type == "cylinder":
            return self._solve_cylinder(semantic_problem)
        raise UnsupportedGeometryOperation(f"'{geometry_type}' is not supported by the semantic planner.")

    def _solve_cone(self, problem):
        given = dict(problem.get("given") or {})
        requested = set(problem.get("requested") or [])
        plan = []
        results = {}

        radius = given.get("radius")
        height = given.get("height")
        slant_height = given.get("slant_height")
        if radius is None:
            raise InvalidParametersError(INVALID_GEOMETRY_PARAMETERS_MESSAGE)

        needs_height = "height" in requested or "volume" in requested or "lateral_surface_area" in requested or "total_surface_area" in requested
        if height is None and needs_height:
            if slant_height is None:
                raise InvalidParametersError(INVALID_GEOMETRY_PARAMETERS_MESSAGE)
            height = self.solver.solve(
                "cone_height_from_radius_slant_height",
                {"radius": radius, "slant_height": slant_height},
            )
            plan.append(
                {
                    "operation": "cone_height_from_radius_slant_height",
                    "produces": "height",
                    "kind": "final" if "height" in requested else "intermediate",
                }
            )
        if "height" in requested:
            results["height"] = height
        if "volume" in requested:
            results["volume"] = self.solver.solve("cone_volume", {"radius": radius, "height": height})
            plan.append({"operation": "cone_volume", "produces": "volume", "kind": "final"})
        if "lateral_surface_area" in requested:
            results["lateral_surface_area"] = self.solver.solve("cone_lateral_surface_area", {"radius": radius, "height": height})
            plan.append({"operation": "cone_lateral_surface_area", "produces": "lateral_surface_area", "kind": "final"})
        if "total_surface_area" in requested:
            results["total_surface_area"] = self.solver.solve("cone_total_surface_area", {"radius": radius, "height": height})
            plan.append({"operation": "cone_total_surface_area", "produces": "total_surface_area", "kind": "final"})

        self._ensure_request_satisfied(requested, results)
        data = {"radius": radius, "height": height}
        if slant_height is not None:
            data["slant_height"] = slant_height
        operation = "cone_solution"
        result = results
        if len(results) == 1:
            output = next(iter(results.keys()))
            operation = {
                "height": "cone_height_from_radius_slant_height",
                "volume": "cone_volume",
                "lateral_surface_area": "cone_lateral_surface_area",
                "total_surface_area": "cone_total_surface_area",
            }[output]
            result = results[output]

        return {
            "operation": operation,
            "data": data,
            "result": result,
            "semantic_problem": problem,
            "plan": plan,
        }

    def _solve_cylinder(self, problem):
        given = dict(problem.get("given") or {})
        requested = set(problem.get("requested") or [])
        radius = given.get("radius")
        height = given.get("height")
        if radius is None or height is None:
            raise InvalidParametersError(INVALID_GEOMETRY_PARAMETERS_MESSAGE)

        results = {}
        plan = []
        if "volume" in requested:
            results["volume"] = self.solver.solve("cylinder_volume", {"radius": radius, "height": height})
            plan.append({"operation": "cylinder_volume", "produces": "volume", "kind": "final"})
        if "lateral_surface_area" in requested:
            results["lateral_surface_area"] = self.solver.solve("cylinder_lateral_surface_area", {"radius": radius, "height": height})
            plan.append({"operation": "cylinder_lateral_surface_area", "produces": "lateral_surface_area", "kind": "final"})
        if "total_surface_area" in requested:
            results["total_surface_area"] = self.solver.solve("cylinder_total_surface_area", {"radius": radius, "height": height})
            plan.append({"operation": "cylinder_total_surface_area", "produces": "total_surface_area", "kind": "final"})

        self._ensure_request_satisfied(requested, results)
        operation = plan[0]["operation"] if len(plan) == 1 else "cylinder_solution"
        result = next(iter(results.values())) if len(results) == 1 else results
        return {
            "operation": operation,
            "data": {"radius": radius, "height": height},
            "result": result,
            "semantic_problem": problem,
            "plan": plan,
        }

    @staticmethod
    def _ensure_request_satisfied(requested, results):
        if not requested or not requested.issubset(results.keys()):
            missing = sorted(requested - set(results.keys()))
            raise UnsupportedGeometryOperation(
                f"The planned solution did not satisfy the requested output(s): {', '.join(missing)}."
            )
