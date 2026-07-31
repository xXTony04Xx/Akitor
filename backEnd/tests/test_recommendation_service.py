import unittest
from unittest.mock import patch

from app.services.recommendation_service import (
    build_progressive_queries,
    search_catalog_progressively,
)


class ProgressiveProductSearchTests(unittest.TestCase):
    def test_queries_keep_the_object_until_the_last_attempt(self) -> None:
        keywords = [
            {"name": "construir", "type": "action"},
            {"name": "silla", "type": "object"},
            {"name": "madera", "type": "material"},
            {"name": "comedor", "type": "location"},
        ]

        self.assertEqual(
            build_progressive_queries(keywords),
            [
                "comedor construir madera silla",
                "construir madera silla",
                "madera silla",
                "silla",
            ],
        )

    @patch(
        "app.services.recommendation_service.search_products_by_title"
    )
    def test_search_stops_at_first_attempt_with_results(self, search) -> None:
        product = {"id": "p1", "sku": "001", "name": "Silla de madera"}
        search.side_effect = [[], [product]]

        result = search_catalog_progressively(
            [
                {"name": "construir", "type": "action"},
                {"name": "silla", "type": "object"},
            ]
        )

        self.assertEqual(result, [product])
        self.assertEqual(search.call_count, 2)


if __name__ == "__main__":
    unittest.main()
