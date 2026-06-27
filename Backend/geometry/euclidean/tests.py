from django.test import SimpleTestCase

from .solver.operations import SUPPORTED_OPERATIONS


class SupportedOperationsTests(SimpleTestCase):
    def test_supported_operations_include_public_math_engine_functions(self):
        self.assertIn("circle_area", SUPPORTED_OPERATIONS)
        self.assertIn("sin_rule", SUPPORTED_OPERATIONS)
        self.assertIn("distance_between_skew_lines", SUPPORTED_OPERATIONS)
        self.assertNotIn("_fmt", SUPPORTED_OPERATIONS)
