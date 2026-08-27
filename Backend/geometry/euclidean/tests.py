from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from .parser.parser_service import ParserService
from .solver.operations import SUPPORTED_OPERATIONS


class SupportedOperationsTests(SimpleTestCase):
    def test_supported_operations_include_public_math_engine_functions(self):
        self.assertIn("circle_area", SUPPORTED_OPERATIONS)
        self.assertIn("sin_rule", SUPPORTED_OPERATIONS)
        self.assertIn("distance_between_skew_lines", SUPPORTED_OPERATIONS)
        self.assertNotIn("_fmt", SUPPORTED_OPERATIONS)


class SolveApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "status": "ok"})

    def test_distance_request(self):
        response = self.client.post(
            "/api/solve/",
            {"operation": "distance", "data": {"x1": 0, "y1": 0, "x2": 3, "y2": 4}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"], 5.0)
        self.assertEqual(response.json()["visualization"]["dimension"], "2d")

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
        self.assertEqual(response.json()["error"]["code"], "invalid_parameters")

    def test_unsupported_operation_is_rejected(self):
        response = self.client.post(
            "/api/solve/", {"operation": "unknown", "data": {}}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "unsupported_operation")

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

    def test_parser_accepts_fenced_json(self):
        result = ParserService._parse_json(
            '```json\n{"operation":"distance","data":{"x1":0}}\n```'
        )
        self.assertEqual(result["operation"], "distance")
