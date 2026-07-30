import asyncio
from typing import Any

from google.genai import types

from app.schemas import RecommendationRequest
from app.services.recommendation_service import build_recommendation


BUSCAR_PRODUCTOS_AKI = types.FunctionDeclaration(
    name="buscar_productos_aki",
    description=(
        "Busca productos reales de AKI relacionados con un proyecto. "
        "Úsala cuando el usuario haya descrito con suficiente claridad "
        "qué desea construir, instalar, reparar o mantener."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "keywords": {
                "type": "array",
                "description": (
                    "Palabras clave normalizadas que representan el proyecto."
                ),
                "minItems": 2,
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
        },
        "required": ["keywords"],
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
