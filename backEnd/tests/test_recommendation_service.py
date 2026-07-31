import unittest
from unittest.mock import patch

from app.services.recommendation_service import (
    build_recommendation,
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

    @patch(
        "app.services.recommendation_service.get_all_projects_with_keywords",
        return_value=[],
    )
    @patch(
        "app.services.recommendation_service.search_catalog_progressively"
    )
    def test_project_mode_does_not_query_algolia(
        self,
        search_catalog,
        _get_projects,
    ) -> None:
        result = build_recommendation(
            [{"name": "silla", "type": "object"}],
            "project",
        )

        search_catalog.assert_not_called()
        self.assertEqual(result["products"], [])

    @patch(
        "app.services.recommendation_service.search_catalog_progressively"
    )
    def test_product_mode_only_queries_algolia(self, search_catalog) -> None:
        product = {"id": "p1", "sku": "001", "name": "Taladro"}
        search_catalog.return_value = [product]

        result = build_recommendation(
            [{"name": "taladro", "type": "object"}],
            "product",
        )

        self.assertEqual(result["products"], [product])
        self.assertEqual(result["matchedProjects"], [])


if __name__ == "__main__":
    unittest.main()
