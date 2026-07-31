import asyncio
from typing import Any

from google.genai import types

from app.schemas import RecommendationRequest
from app.services.recommendation_service import build_recommendation


BUSCAR_PRODUCTOS_AKI = types.FunctionDeclaration(
    name="buscar_productos_aki",
    description=(
        "Busca productos de AKI en una de dos fuentes. Usa search_mode=project "
        "para proyectos: es la opción prioritaria y aprovecha el historial de "
        "productos comprados por clientes en proyectos similares. Usa "
        "search_mode=product únicamente cuando el cliente pida encontrar o "
        "consultar un producto concreto por su nombre; ese modo busca títulos "
        "en Algolia y relaja automáticamente los términos secundarios."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "description": (
                    "Palabras clave normalizadas del producto solicitado o "
                    "del proyecto descrito."
                ),
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": (
                                "Palabra clave breve, normalizada y en singular."
                            ),
                        },
                        "type": {
                            "type": "string",
                            "enum": [
                                "action",
                                "object",
                                "location",
                                "material",
                                "use",
                            ],
                            "description": "Categoría de la palabra clave.",
                        },
                    },
                    "required": ["name", "type"],
                    "additionalProperties": False,
                },
            },
            "search_mode": {
                "type": "string",
                "enum": ["project", "product"],
                "description": (
                    "project para recomendar según proyectos y compras "
                    "anteriores; product solo para buscar un producto "
                    "específico por título."
                ),
            },
        },
        "required": ["keywords", "search_mode"],
        "additionalProperties": False,
    },
)

AKI_TOOLS = [
    types.Tool(function_declarations=[BUSCAR_PRODUCTOS_AKI]),
]


async def buscar_productos_aki(arguments: dict[str, Any]) -> dict[str, Any]:
    print("[AKITOR] Validando palabras clave extraídas por Gemini...", flush=True)
    request = RecommendationRequest.model_validate(arguments)
    keywords = [keyword.model_dump() for keyword in request.keywords]

    print(f"[AKITOR] Keywords extraídas: {keywords}", flush=True)
    print("[AKITOR] Consultando proyectos y productos relacionados...", flush=True)
    recommendation = await asyncio.to_thread(
        build_recommendation,
        keywords,
        request.search_mode,
    )

    products = [
        {
            "sku": product["sku"],
            "name": product["name"],
        }
        for product in recommendation["products"]
        if product.get("sku") and product.get("name")
    ]

    print(
        f"[AKITOR] Consulta completada: {len(products)} producto(s) encontrado(s).",
        flush=True,
    )

    return {
        "products": products,
        "totalProducts": len(products),
    }
