from typing import Any

from app.database import get_supabase_client


def get_products_by_project_id(
    project_id: int,
) -> list[dict[str, Any]]:
    supabase = get_supabase_client()

    relations_response = (
        supabase
        .table("project_products")
        .select("product_id, quantity")
        .eq("project_id", project_id)
        .execute()
    )

    if not relations_response.data:
        return []

    product_ids = [
        relation["product_id"]
        for relation in relations_response.data
    ]

    products_response = (
        supabase
        .table("products")
        .select("id, sku, name")
        .in_("id", product_ids)
        .execute()
    )

    products_by_id = {
        product["id"]: product
        for product in products_response.data
    }

    result = []

    for relation in relations_response.data:
        product = products_by_id.get(relation["product_id"])

        if product is None:
            continue

        result.append(
            {
                "id": product["id"],
                "sku": product["sku"],
                "name": product["name"],
                "quantity": relation["quantity"],
            }
        )

    return result


def get_products_by_project_ids(
    project_ids: list[int],
) -> list[dict[str, Any]]:
    if not project_ids:
        return []

    supabase = get_supabase_client()

    relations_response = (
        supabase
        .table("project_products")
        .select("project_id, product_id, quantity")
        .in_("project_id", project_ids)
        .execute()
    )

    relations = relations_response.data

    if not relations:
        return []

    product_ids = list(
        {
            relation["product_id"]
            for relation in relations
        }
    )

    products_response = (
        supabase
        .table("products")
        .select("id, sku, name")
        .in_("id", product_ids)
        .execute()
    )

    products_by_id = {
        product["id"]: product
        for product in products_response.data
    }

    result = []

    for relation in relations:
        product = products_by_id.get(relation["product_id"])

        if product is None:
            continue

        result.append(
            {
                "id": product["id"],
                "sku": product["sku"],
                "name": product["name"],
                "quantity": relation["quantity"],
                "project_id": relation["project_id"],
            }
        )

    return result