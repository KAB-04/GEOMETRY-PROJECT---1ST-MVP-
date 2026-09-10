from unittest.mock import MagicMock, patch
import math
import os

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from .parser.parser_service import ParserService
from google.genai.errors import ClientError, ServerError

from .parser.exceptions import (
    ProviderAccessDenied,
    ProviderRateLimited,
    ProviderUnavailable,
    ProviderUnreachable,
)
from .parser.gemini_client import GeminiClient
from .explanations import build_explanation, operation_label
from .solver.operations import SUPPORTED_OPERATIONS

DISTANCE_WORD_PROBLEM = (
    "Ama lives at point (2, 3) on a coordinate map, while Kojo lives at point "
    "(8, 11). What is the straight-line distance between their homes?"
)


class GeminiRetryTests(SimpleTestCase):
    def make_client(self, responses):
        fake_client = MagicMock()
        fake_client.models.generate_content.side_effect = responses
        with patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "test-gemini-key",
                "GROQ_API_KEY": "",
                "GROQ_MODEL": "qwen/qwen3.6-27b",
                "LLM_FALLBACK_ENABLED": "false",
            },
            clear=False,
        ), patch("euclidean.parser.gemini_client.genai.Client", return_value=fake_client):
            client = GeminiClient()
        return client, fake_client

    @staticmethod
    def unavailable_error():
        return ServerError(503, {"error": {"status": "UNAVAILABLE"}})

    def test_gemini_503_then_success_retries_once(self):
        response = MagicMock(text='{"status":"ok"}')
        client, fake_client = self.make_client([self.unavailable_error(), response])
        with patch("euclidean.parser.gemini_client.time.sleep") as sleep:
            self.assertEqual(client.generate("test"), '{"status":"ok"}')
        self.assertEqual(fake_client.models.generate_content.call_count, 2)
        sleep.assert_called_once_with(1)

    def test_gemini_two_503s_then_success_retries_twice(self):
        response = MagicMock(text='{"status":"ok"}')
        client, fake_client = self.make_client([self.unavailable_error(), self.unavailable_error(), response])
        with patch("euclidean.parser.gemini_client.time.sleep") as sleep:
            self.assertEqual(client.generate("test"), '{"status":"ok"}')
        self.assertEqual(fake_client.models.generate_content.call_count, 3)
        self.assertEqual(sleep.call_args_list, [((1,),), ((2,),)])

    def test_gemini_three_503s_returns_unavailable(self):
        client, fake_client = self.make_client([self.unavailable_error()] * 3)
        with patch("euclidean.parser.gemini_client.time.sleep"):
            with self.assertRaises(ProviderUnavailable):
                client.generate("test")
        self.assertEqual(fake_client.models.generate_content.call_count, 3)

    def test_gemini_429_is_rate_limited_without_503_retry(self):
        rate_limit = ClientError(429, {"error": {"status": "RESOURCE_EXHAUSTED"}})
        client, fake_client = self.make_client([rate_limit])
        with patch("euclidean.parser.gemini_client.time.sleep") as sleep:
            with self.assertRaises(ProviderRateLimited):
                client.generate("test")
        self.assertEqual(fake_client.models.generate_content.call_count, 1)
        sleep.assert_not_called()


class SupportedOperationsTests(SimpleTestCase):
    def test_supported_operations_include_public_math_engine_functions(self):
        self.assertIn("circle_area", SUPPORTED_OPERATIONS)
        self.assertIn("sin_rule", SUPPORTED_OPERATIONS)
        self.assertIn("distance_between_skew_lines", SUPPORTED_OPERATIONS)
        self.assertIn("triangle_area", SUPPORTED_OPERATIONS)
        self.assertIn("triangle_perimeter", SUPPORTED_OPERATIONS)
        self.assertIn("triangle_third_angle", SUPPORTED_OPERATIONS)
        self.assertIn("midpoint", SUPPORTED_OPERATIONS)
        self.assertNotIn("_fmt", SUPPORTED_OPERATIONS)


class SolveApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "status": "ok"})

    def test_provider_network_errors_are_safe_and_classified(self):
        for exception, code, status_code in (
            (ProviderUnreachable("DNS failed"), "AI_PROVIDER_UNREACHABLE", 503),
            (ProviderAccessDenied("access denied"), "AI_PROVIDER_ACCESS_DENIED", 502),
            (ProviderRateLimited("rate limited"), "AI_PROVIDER_RATE_LIMITED", 429),
        ):
            with patch("euclidean.views.parser_service") as service:
                service.parse.side_effect = exception
                response = self.client.post("/api/solve/", {"question": "Find a distance."}, format="json")
            self.assertEqual(response.status_code, status_code)
            self.assertEqual(response.json()["error"]["code"], code)
            self.assertNotIn("DNS failed", response.json()["error"]["message"])

    def test_distance_request(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "distance", "data": {"x1": 0, "y1": 0, "x2": 3, "y2": 4}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], 5.0)
        self.assertEqual(response.json()["operation_label"], "Distance Between Two Points")
        self.assertIn("distance formula", response.json()["explanation"]["concept"])
        self.assertEqual(response.json()["visualization"]["dimension"], "2d")
        self.assertEqual(
            [item["type"] for item in response.json()["visualization"]["objects"]],
            ["point", "point", "segment"],
        )

    def test_cors_header_is_present(self):
        response = self.client.get("/api/health/", HTTP_ORIGIN="http://127.0.0.1:5173")
        self.assertEqual(response["Access-Control-Allow-Origin"], "http://127.0.0.1:5173")

    def test_missing_parameters_are_rejected(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "distance", "data": {"x1": 0}},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "INVALID_GEOMETRY_PARAMETERS")
        self.assertEqual(
            response.json()["error"]["message"],
            "The problem could not be interpreted with all required geometric information.",
        )

    def test_invalid_physical_dimensions_are_rejected(self):
        cases = [
            {"operation": "circle_area", "data": {"rho": 0}},
            {"operation": "circle_circumference", "data": {"rho": -2}},
            {"operation": "triangle_area", "data": {"base": 5, "height": 0}},
            {"operation": "rectangle_area", "data": {"length": -1, "width": 4}},
            {"operation": "pythagoras", "data": {"a": 0, "b": 4}},
        ]
        for payload in cases:
            response = self.client.post("/api/solve/", payload, format="json")
            self.assertEqual(response.status_code, 400, payload)
            self.assertEqual(response.json()["error"]["code"], "INVALID_GEOMETRY_PARAMETERS")

    def test_3d_distance_returns_3d_visualization(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "distance3d", "data": {"points": [{"id": "A", "x": 1, "y": 2, "z": 3}, {"id": "B", "x": 5, "y": 5, "z": 6}]}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.json()["result"], math.sqrt(34))
        self.assertEqual(response.json()["visualization"]["dimension"], "3d")
        self.assertEqual([item["type"] for item in response.json()["visualization"]["objects"]], ["point3d", "point3d", "segment3d"])

    def test_3d_midpoint_preserves_z_coordinate(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "midpoint3d", "data": {"points": [{"id": "A", "x": 2, "y": 4, "z": 6}, {"id": "B", "x": 8, "y": 10, "z": 12}]}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], {"type": "point3d", "x": 5.0, "y": 7.0, "z": 9.0})
        self.assertEqual(response.json()["visualization"]["dimension"], "3d")

    def test_3d_vector_triangle_plane_and_cuboid_contracts(self):
        points = [{"id": "A", "x": 0, "y": 0, "z": 0}, {"id": "B", "x": 5, "y": 0, "z": 0}, {"id": "C", "x": 2, "y": 3, "z": 4}]
        vector = self.client.post("/api/solve/", {"operation": "vector3d", "data": {"points": points[:2]}}, format="json")
        triangle = self.client.post("/api/solve/", {"operation": "triangle3d", "data": {"points": points}}, format="json")
        plane = self.client.post("/api/solve/", {"operation": "plane3d", "data": {"points": points}}, format="json")
        cuboid = self.client.post("/api/solve/", {"operation": "cuboid_volume", "data": {"width": 5, "height": 3, "depth": 4}}, format="json")
        self.assertEqual(vector.status_code, triangle.status_code, 200)
        self.assertEqual(vector.json()["visualization"]["objects"][-1]["type"], "vector3d")
        self.assertEqual(triangle.json()["visualization"]["objects"][-1]["type"], "triangle3d")
        self.assertEqual(plane.json()["visualization"]["objects"][-1]["type"], "plane")
        self.assertEqual(cuboid.json()["result"], 60)
        self.assertEqual(cuboid.json()["visualization"]["objects"][-1]["type"], "cuboid")

    def test_unsupported_operation_is_rejected(self):
        response = self.client.post(
            "/api/solve/", {"operation": "unknown", "data": {}}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "UNSUPPORTED_GEOMETRY_OPERATION")

    @patch("euclidean.views.ParserService")
    def test_question_request_uses_parser_then_solver(self, parser_class):
        parser_class.return_value.parse.return_value = {
            "operation": "distance",
            "data": {"x1": 0, "y1": 0, "x2": 3, "y2": 4},
        }
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/", {"question": "distance from (0,0) to (3,4)"}, format="json"
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], 5.0)
        parser_class.return_value.parse.assert_called_once()

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_distance_word_problem_from_gemini_json(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"distance","data":{"x1":2,"y1":3,"x2":8,"y2":11}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {"question": DISTANCE_WORD_PROBLEM},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["operation"], "distance")
        self.assertEqual(response.json()["result"], 10.0)

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_circle_area_word_problem_from_gemini_radius_alias(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"circle_area","data":{"radius":7}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {"question": "A circular garden has a radius of 7 metres. What is the area of the garden?"},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.json()["result"], math.pi * 49)
        object_types = [item["type"] for item in response.json()["visualization"]["objects"]]
        self.assertEqual(object_types, ["point", "circle", "segment", "point"])

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_triangle_area_word_problem_from_gemini_json(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"triangle_area","data":{"base":18,"height":12}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {
                    "question": (
                        "A triangular piece of land has a base of 18 metres and a "
                        "perpendicular height of 12 metres. Find its area."
                    )
                },
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], 108.0)
        object_types = [item["type"] for item in response.json()["visualization"]["objects"]]
        self.assertIn("polygon", object_types)
        self.assertEqual(object_types.count("segment"), 2)

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_midpoint_word_problem_from_gemini_points(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"midpoint","data":{"point1":[2,4],"point2":[10,12]}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {
                    "question": (
                        "Two towns are represented by A(2,4) and B(10,12). "
                        "What point lies exactly halfway between them?"
                    )
                },
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], [6.0, 8.0])
        point_ids = [item["id"] for item in response.json()["visualization"]["objects"] if item["type"] == "point"]
        self.assertEqual(point_ids, ["A", "B", "M"])

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_triangle_third_angle_word_problem_from_gemini_json(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"triangle_third_angle","data":{"angle1":45,"angle2":65}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {"question": "Two angles of a triangle are 45° and 65°. Find the third angle."},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], 70.0)
        self.assertNotIn("triangle_third_angle", str(response.json()["explanation"]))
        angles = [item["value"] for item in response.json()["visualization"]["objects"] if item["type"] == "angle"]
        self.assertEqual(angles, [45, 65, 70])

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_triangle_remaining_angle_word_problem_from_gemini_json(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"triangle_third_angle","data":{"angle1":30,"angle2":90}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {"question": "A triangle has two angles measuring 30° and 90°. What is the remaining angle?"},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], 60.0)

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_invalid_triangle_third_angle_returns_controlled_error(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"triangle_third_angle","data":{"angle1":120,"angle2":80}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {"question": "A triangle has angles of 120° and 80°. Find the third angle."},
                format="json",
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "INVALID_GEOMETRY_PARAMETERS")

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_ladder_word_problem_from_gemini_pythagoras(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"pythagoras","data":{"a":8,"b":6}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {
                    "question": (
                        "A ladder reaches 8 metres up a wall and its base is 6 metres "
                        "from the wall. How long is the ladder?"
                    )
                },
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], 10.0)
        object_types = [item["type"] for item in response.json()["visualization"]["objects"]]
        self.assertIn("polygon", object_types)
        self.assertIn("angle", object_types)

    def test_reflection_y_axis_preserves_all_triangle_vertices(self):
        response = self.client.post(
            "/api/solve/",
            {
                "operation": "transform",
                "data": {
                    "transformation": "reflection_y_axis",
                    "points": [
                        {"id": "A", "x": 2, "y": 1},
                        {"id": "B", "x": 6, "y": 1},
                        {"id": "C", "x": 4, "y": 5},
                    ],
                },
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [(point["id"], point["x"], point["y"]) for point in response.json()["result"]["transformed"]],
            [("A′", -2, 1), ("B′", -6, 1), ("C′", -4, 5)],
        )
        self.assertEqual(len(response.json()["visualization"]["objects"]), 11)

    def test_single_point_transformations(self):
        cases = [
            ("reflection_y_axis", (-4, 2)),
            ("reflection_x_axis", (4, -2)),
            ("reflection_origin", (-4, -2)),
            ("reflection_y_equals_x", (2, 4)),
            ("rotation_90_ccw", (-2, 4)),
            ("rotation_90_cw", (2, -4)),
            ("rotation_180", (-4, -2)),
        ]
        for transformation, expected in cases:
            response = self.client.post(
                "/api/solve/",
                {"operation": "transform", "data": {"transformation": transformation, "points": [{"id": "P", "x": 4, "y": 2}]}},
                format="json",
            )
            self.assertEqual(response.status_code, 200, transformation)
            point = response.json()["result"]["transformed"][0]
            self.assertAlmostEqual(point["x"], expected[0], msg=transformation)
            self.assertAlmostEqual(point["y"], expected[1], msg=transformation)

    def test_translation_transforms_every_vertex(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "transform", "data": {"transformation": "translation", "dx": 4, "dy": 3, "points": [{"id": "A", "x": 1, "y": 1}, {"id": "B", "x": 5, "y": 1}, {"id": "C", "x": 3, "y": 4}]}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([(point["x"], point["y"]) for point in response.json()["result"]["transformed"]], [(5, 4), (9, 4), (7, 7)])

    def test_circle_circle_intersection_relationships(self):
        cases = [
            ({"x1": 0, "y1": 0, "r1": 5, "x2": 8, "y2": 0, "r2": 5}, "intersecting", 2),
            ({"x1": 0, "y1": 0, "r1": 5, "x2": 10, "y2": 0, "r2": 5}, "tangent", 1),
            ({"x1": 0, "y1": 0, "r1": 5, "x2": 15, "y2": 0, "r2": 5}, "separate", 0),
            ({"x1": 0, "y1": 0, "r1": 5, "x2": 0, "y2": 0, "r2": 5}, "coincident", "infinite"),
            ({"x1": 0, "y1": 0, "r1": 5, "x2": 3, "y2": 0, "r2": 2}, "tangent", 1),
            ({"x1": 0, "y1": 0, "r1": 10, "x2": 2, "y2": 0, "r2": 3}, "contained", 0),
        ]
        for data, relationship, count in cases:
            response = self.client.post("/api/solve/", {"operation": "circle_circle_intersection", "data": data}, format="json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["result"]["final"]["relationship"], relationship)
            self.assertEqual(response.json()["result"]["final"]["intersection_count"], count)

    def test_circle_circle_intersection_points_and_visualization(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "circle_circle_intersection", "data": {"x1": 0, "y1": 0, "r1": 5, "x2": 8, "y2": 0, "r2": 5}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        points = response.json()["result"]["final"]["points"]
        self.assertAlmostEqual(points[0]["x"], 4)
        self.assertAlmostEqual(abs(points[0]["y"]), 3)
        self.assertEqual([item["type"] for item in response.json()["visualization"]["objects"]].count("circle"), 2)
        self.assertEqual([item["type"] for item in response.json()["visualization"]["objects"]].count("point"), 4)

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_circle_intersection_word_problem_is_not_routed_to_distance(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"circle_circle_intersection","data":{"x1":0,"y1":0,"r1":5,"x2":8,"y2":0,"r2":5}}'
        )
        question = (
            "Circle A has center (0, 0) and radius 5. Circle B has center (8, 0) "
            "and radius 5. Determine whether the circles intersect, and if they do, "
            "find their intersection points."
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post("/api/solve/", {"question": question}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["operation"], "circle_circle_intersection")
        self.assertEqual(response.json()["result"]["final"]["intersection_count"], 2)

    def test_non_horizontal_circle_intersection(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "circle_circle_intersection", "data": {"x1": 2, "y1": 3, "r1": 5, "x2": 7, "y2": 9, "r2": 5}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["final"]["intersection_count"], 2)

    def test_nearby_distinct_circle_centers_are_not_coincident(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "circle_circle_intersection", "data": {"x1": 0, "y1": 0, "r1": 5, "x2": 1e-10, "y2": 0, "r2": 5}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["final"]["relationship"], "intersecting")
        self.assertEqual(response.json()["result"]["final"]["intersection_count"], 2)

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_transformation_word_problem_is_not_routed_to_midpoint(self, gemini_client):
        gemini_client.return_value.generate.return_value = (
            '{"operation":"transform","data":{"transformation":"reflection_y_axis","points":['
            '{"id":"A","x":2,"y":1},{"id":"B","x":6,"y":1},{"id":"C","x":4,"y":5}]}}'
        )
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {"question": "Triangle ABC has vertices A(2, 1), B(6, 1), and C(4, 5). Reflect the triangle across the y-axis."},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["operation"], "transform")
        self.assertNotEqual(response.json()["operation"], "midpoint")

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_transformation_intent_cannot_be_silently_midpoint(self, gemini_client):
        gemini_client.return_value.generate.return_value = '{"operation":"midpoint","data":{"x1":2,"y1":1,"x2":6,"y2":1}}'
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {"question": "Reflect P(2,1) across the y-axis."},
                format="json",
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "UNSUPPORTED_GEOMETRY_OPERATION")

    def test_duplicate_transformation_ids_are_rejected(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "transform", "data": {"transformation": "reflection_y_axis", "points": [{"id": "A", "x": 2, "y": 1}, {"id": "A", "x": 6, "y": 1}]}},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "INVALID_GEOMETRY_PARAMETERS")

    def test_rectangle_visualization_contains_four_vertices(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "rectangle_area", "data": {"length": 105, "width": 68}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        visualization = response.json()["visualization"]
        self.assertEqual(visualization["objects"][4]["vertices"], ["A", "B", "C", "D"])

    @patch("euclidean.parser.parser_service.GeminiClient")
    def test_empty_gemini_distance_data_returns_controlled_error(self, gemini_client):
        gemini_client.return_value.generate.return_value = '{"operation":"distance","data":{}}'
        with patch("euclidean.views.parser_service", None):
            response = self.client.post(
                "/api/solve/",
                {"question": DISTANCE_WORD_PROBLEM},
                format="json",
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "INVALID_GEOMETRY_PARAMETERS")

    def test_parser_accepts_fenced_json(self):
        result = ParserService._parse_json(
            '```json\n{"operation":"distance","data":{"x1":0}}\n```'
        )
        self.assertEqual(result["operation"], "distance")

    def test_parser_accepts_json_with_model_preamble(self):
        result = ParserService._parse_json(
            'Here is the parsed request:\n{"operation":"pythagoras","data":{"a":3,"b":4}}'
        )
        self.assertEqual(result, {"operation": "pythagoras", "data": {"a": 3, "b": 4}})

    @patch.object(ParserService, "_parse_json")
    @patch.object(ParserService, "__init__", return_value=None)
    def test_parser_normalizes_hypotenuse_operation(self, _init, parse_json):
        parse_json.return_value = {"operation": "hypotenuse", "data": {"a": 3, "b": 4}}
        parser = ParserService()
        parser.client = type("Client", (), {"generate": lambda self, prompt: "{}"})()
        result = parser.parse("Find the hypotenuse of sides 3 and 4")
        self.assertEqual(result["operation"], "pythagoras")

    @patch.object(ParserService, "_parse_json")
    @patch.object(ParserService, "__init__", return_value=None)
    def test_parser_normalizes_common_data_field_and_parameter_aliases(self, _init, parse_json):
        parse_json.return_value = {
            "operation": "circle area",
            "parameters": {"radius": "8"},
        }
        parser = ParserService()
        parser.client = type("Client", (), {"generate": lambda self, prompt: "{}"})()
        result = parser.parse("Find the area of a circle with radius 8")
        self.assertEqual(result, {"operation": "circle_area", "data": {"rho": 8}})

    @patch.object(ParserService, "_parse_json")
    @patch.object(ParserService, "__init__", return_value=None)
    def test_parser_converts_degree_angle_fields_to_radians(self, _init, parse_json):
        parse_json.return_value = {
            "operation": "cosine_rule_side",
            "data": {"b": 3, "c": 4, "alpha_deg": 60},
        }
        parser = ParserService()
        parser.client = type("Client", (), {"generate": lambda self, prompt: "{}"})()
        result = parser.parse("Find the third side with angle 60 degrees")
        self.assertEqual(result["operation"], "cosine_rule_side")
        self.assertAlmostEqual(result["data"]["alpha_rad"], math.pi / 3)

    @patch.object(ParserService, "_parse_json")
    @patch.object(ParserService, "__init__", return_value=None)
    def test_parser_flattens_point_data_for_distance(self, _init, parse_json):
        parse_json.return_value = {
            "operation": "distance",
            "data": {"point1": {"x": 2, "y": 3}, "point2": {"x": 8, "y": 11}},
        }
        parser = ParserService()
        parser.client = type("Client", (), {"generate": lambda self, prompt: "{}"})()
        result = parser.parse(DISTANCE_WORD_PROBLEM)
        self.assertEqual(result["data"], {"x1": 2, "y1": 3, "x2": 8, "y2": 11})

    @patch.object(ParserService, "_parse_json")
    @patch.object(ParserService, "__init__", return_value=None)
    def test_parser_normalizes_triangle_angle_aliases(self, _init, parse_json):
        parse_json.return_value = {
            "operation": "third_angle",
            "data": {"alpha_deg": 45, "beta_deg": 65},
        }
        parser = ParserService()
        parser.client = type("Client", (), {"generate": lambda self, prompt: "{}"})()
        result = parser.parse("Two angles of a triangle are 45° and 65°. Find the third angle.")
        self.assertEqual(
            result,
            {"operation": "triangle_third_angle", "data": {"angle1": 45, "angle2": 65}},
        )


class ExplanationTests(SimpleTestCase):
    def assert_student_explanation(self, operation, data, result, expected_text, question=""):
        explanation = build_explanation(operation, data, result, question)
        self.assertIsInstance(explanation, dict)
        self.assertIn("concept", explanation)
        self.assertIn("formula", explanation)
        self.assertIn("steps", explanation)
        self.assertIn("conclusion", explanation)
        combined = " ".join(
            [explanation["concept"], explanation["formula"], *explanation["steps"], explanation["conclusion"]]
        )
        self.assertIn(expected_text, combined)
        if "_" in operation:
            self.assertNotIn(operation, combined)

    def test_distance_explanation_uses_engine_result(self):
        self.assert_student_explanation(
            "distance",
            {"x1": 2, "y1": 3, "x2": 8, "y2": 11},
            10.0,
            "d = 10",
        )

    def test_circle_area_explanation(self):
        self.assert_student_explanation(
            "circle_area",
            {"rho": 7},
            math.pi * 49,
            "153.94",
            "A circular garden has a radius of 7 metres. Find its area.",
        )
        explanation = build_explanation("circle_area", {"rho": 7}, math.pi * 49, "A circle has radius 7 m.")
        self.assertIn(r"\pi", explanation["formula"])
        self.assertIn(r"49\pi", " ".join(explanation["steps"]))

    def test_explanations_use_latex_powers_and_roots(self):
        distance = build_explanation("distance", {"x1": 2, "y1": 3, "x2": 8, "y2": 11}, 10.0)
        pythagoras = build_explanation("pythagoras", {"a": 8, "b": 6}, 10.0)
        self.assertIn(r"\sqrt", distance["formula"])
        self.assertIn("^2", pythagoras["formula"])

    def test_triangle_area_explanation(self):
        self.assert_student_explanation("triangle_area", {"base": 18, "height": 12}, 108.0, "108")

    def test_missing_triangle_angle_explanation(self):
        self.assert_student_explanation(
            "triangle_third_angle",
            {"angle1": 45, "angle2": 65},
            70.0,
            "70 degrees",
        )

    def test_midpoint_explanation(self):
        self.assert_student_explanation(
            "midpoint",
            {"x1": 2, "y1": 4, "x2": 10, "y2": 12},
            (6.0, 8.0),
            "(6, 8)",
        )

    def test_slope_explanation(self):
        self.assert_student_explanation(
            "slope",
            {"x1": 2, "y1": 4, "x2": 10, "y2": 12},
            1.0,
            "m = 1",
        )

    def test_pythagoras_explanation(self):
        self.assert_student_explanation("pythagoras", {"a": 8, "b": 6}, 10.0, "c = 10")

    def test_rectangle_explanations(self):
        self.assert_student_explanation("rectangle_area", {"length": 8, "width": 5}, 40.0, "40")
        self.assert_student_explanation("rectangle_perimeter", {"length": 8, "width": 5}, 26.0, "26")

    def test_operation_labels_are_student_friendly(self):
        self.assertEqual(operation_label("triangle_third_angle"), "Triangle - Missing Angle")
        self.assertNotIn("_", operation_label("rectangle_perimeter"))
