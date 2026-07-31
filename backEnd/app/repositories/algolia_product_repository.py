import json
import os
from typing import Any
from urllib import error, parse, request


ALGOLIA_TIMEOUT_SECONDS = 5


def search_products_by_title(
    query: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Busca productos publicados directamente por título en Algolia."""

    application_id = os.getenv("ALGOLIA_APP_ID")
    search_api_key = os.getenv("ALGOLIA_SEARCH_API_KEY")
    index_name = os.getenv("PRODUCTS_INDEX_NAME", "products")

    if not application_id or not search_api_key or not query.strip():
        return []

    encoded_index = parse.quote(index_name, safe="")
    url = (
        f"https://{application_id}-dsn.algolia.net"
        f"/1/indexes/{encoded_index}/query"
    )
    payload = json.dumps(
        {
            "query": query,
            "hitsPerPage": limit,
            "restrictSearchableAttributes": ["title"],
            "filters": "status:published",
            "attributesToRetrieve": ["objectID", "sku", "title"],
            "typoTolerance": True,
        }
    ).encode("utf-8")

    algolia_request = request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Algolia-Application-Id": application_id,
            "X-Algolia-API-Key": search_api_key,
        },
    )

    try:
        with request.urlopen(
            algolia_request,
            timeout=ALGOLIA_TIMEOUT_SECONDS,
        ) as response:
            response_payload = json.load(response)
    except (error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"[AKITOR] Algolia no pudo completar la búsqueda: {exc}", flush=True)
        return []

    products = []

    for hit in response_payload.get("hits", []):
        sku = hit.get("sku")
        title = hit.get("title")

        if not sku or not title:
            continue

        products.append(
            {
                "id": hit.get("objectID"),
                "sku": str(sku),
                "name": str(title),
            }
        )

    return products
