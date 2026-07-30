from typing import Any

from app.database import get_supabase_client


def get_products_by_project_id(project_id: int) -> list[dict[str, Any]]:

    supabase = get_supabase_client()

    response = (
        supabase
        .table("project_products")
        .select(
            """
            product_id,
            quantity,
            products (
                id,
                sku,
                name
            )
            """
        )
        .eq("project_id", project_id)
        .execute()
    )

    products: list[dict[str, Any]] = []

    for relation in response.data:
        product = relation.get("products")

        if not product:
            continue

        products.append(
            {
                "id": product["id"],
                "sku": product["sku"],
                "name": product["name"],
                "quantity": relation["quantity"],
            }
        )

    return products