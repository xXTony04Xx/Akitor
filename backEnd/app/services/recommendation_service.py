import unicodedata
from typing import Any

from app.repositories.algolia_product_repository import (
    search_products_by_title,
)
from app.repositories.product_repository import (
    get_products_by_project_ids,
)
from app.repositories.project_repository import (
    get_all_projects_with_keywords,
)


KEYWORD_WEIGHTS = {
    "object": 5,
    "action": 4,
    "material": 3,
    "location": 2,
    "use": 1,
}

TOP_PROJECTS_LIMIT = 3
PRODUCTS_LIMIT = 20

# Se eliminan primero los términos que normalmente describen el contexto y no
# el nombre del producto. El objeto se conserva hasta el último intento.
KEYWORD_RELAXATION_PRIORITY = {
    "use": 0,
    "location": 1,
    "action": 2,
    "material": 3,
    "object": 4,
}


def normalize_text(value: str) -> str:
    """
    Convierte el texto a minúsculas, elimina espacios extra
    y remueve tildes.
    """

    normalized = unicodedata.normalize("NFKD", value)

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    return " ".join(
        without_accents.lower().strip().split()
    )


def normalize_keyword_type(keyword_type: str) -> str:
    return normalize_text(keyword_type)


def build_progressive_queries(
    input_keywords: list[dict[str, str]],
) -> list[str]:
    """Genera búsquedas de mayor a menor especificidad, sin repetirlas."""

    ordered_keywords = sorted(
        input_keywords,
        key=lambda keyword: KEYWORD_RELAXATION_PRIORITY.get(
            normalize_keyword_type(keyword["type"]),
            0,
        ),
    )
    terms = [normalize_text(keyword["name"]) for keyword in ordered_keywords]
    queries = []

    while terms:
        query = " ".join(terms)
        if query and query not in queries:
            queries.append(query)
        terms.pop(0)

    return queries


def search_catalog_progressively(
    input_keywords: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Relaja una palabra por intento y se detiene al encontrar resultados."""

    for query in build_progressive_queries(input_keywords):
        print(f"[AKITOR] Buscando en Algolia por título: {query}", flush=True)
        products = search_products_by_title(query, PRODUCTS_LIMIT)
        if products:
            return products

    return []


def calculate_project_score(
    input_keywords: list[dict[str, str]],
    project_keywords: list[dict[str, Any]],
) -> tuple[int, list[dict[str, Any]], bool]:
    """
    Compara las keywords recibidas contra las keywords del proyecto.

    Retorna:
    - Puntaje total.
    - Keywords coincidentes.
    - Indica si hubo coincidencia de tipo object.
    """

    normalized_project_keywords = {
        (
            normalize_text(keyword["name"]),
            normalize_keyword_type(keyword["type"]),
        ): keyword
        for keyword in project_keywords
    }

    score = 0
    matched_keywords = []
    has_object_match = False

    for input_keyword in input_keywords:
        normalized_name = normalize_text(input_keyword["name"])
        normalized_type = normalize_keyword_type(input_keyword["type"])

        key = (normalized_name, normalized_type)

        if key not in normalized_project_keywords:
            continue

        weight = KEYWORD_WEIGHTS.get(normalized_type, 1)

        score += weight

        matched_keywords.append(
            {
                "name": input_keyword["name"],
                "type": input_keyword["type"],
                "weight": weight,
            }
        )

        if normalized_type == "object":
            has_object_match = True

    return score, matched_keywords, has_object_match


def build_recommendation(
    input_keywords: list[dict[str, str]],
    search_mode: str = "project",
) -> dict[str, Any]:
    """
    Construye la recomendación completa.
    """

    if search_mode == "product":
        catalog_products = search_catalog_progressively(input_keywords)
        return {
            "matchedProjects": [],
            "products": catalog_products[:PRODUCTS_LIMIT],
            "totalProducts": len(catalog_products[:PRODUCTS_LIMIT]),
        }

    projects = get_all_projects_with_keywords()

    ranked_projects = []

    request_contains_object = any(
        normalize_keyword_type(keyword["type"]) == "object"
        for keyword in input_keywords
    )

    for project in projects:
        score, matched_keywords, has_object_match = (
            calculate_project_score(
                input_keywords=input_keywords,
                project_keywords=project["keywords"],
            )
        )

        if score <= 0:
            continue

        ranked_projects.append(
            {
                "id": project["id"],
                "name": project["name"],
                "score": score,
                "matched_keywords": matched_keywords,
                "has_object_match": has_object_match,
            }
        )

    ranked_projects.sort(
        key=lambda project: (
            project["has_object_match"]
            if request_contains_object
            else False,
            project["score"],
            len(project["matched_keywords"]),
        ),
        reverse=True,
    )

    top_projects = ranked_projects[:TOP_PROJECTS_LIMIT]

    project_ids = [
        project["id"]
        for project in top_projects
    ]

    products = get_products_by_project_ids(project_ids)

    projects_by_id = {
        project["id"]: project
        for project in top_projects
    }

    project_position = {
        project["id"]: index
        for index, project in enumerate(top_projects)
    }

    products.sort(
        key=lambda product: project_position.get(
            product["project_id"],
            999,
        )
    )

    products_by_sku: dict[str, dict[str, Any]] = {}

    for product in products:
        sku = normalize_text(product["sku"])

        if sku in products_by_sku:
            continue

        project = projects_by_id.get(product["project_id"])

        if project is None:
            continue

        products_by_sku[sku] = {
            "id": product["id"],
            "sku": product["sku"],
            "name": product["name"],
            "project_id": project["id"],
            "project_name": project["name"],
            "project_score": project["score"],
        }

    recommended_products = list(
        products_by_sku.values()
    )[:PRODUCTS_LIMIT]

    cleaned_projects = []

    for project in top_projects:
        cleaned_projects.append(
            {
                "id": project["id"],
                "name": project["name"],
                "score": project["score"],
                "matched_keywords": project["matched_keywords"],
            }
        )

    return {
        "matchedProjects": cleaned_projects,
        "products": recommended_products,
        "totalProducts": len(recommended_products),
    }
