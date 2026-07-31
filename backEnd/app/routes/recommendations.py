from fastapi import APIRouter, HTTPException, status
from postgrest.exceptions import APIError

from app.schemas import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import (
    build_recommendation,
)


router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["Recommendations"],
)


@router.post(
    "",
    response_model=RecommendationResponse,
    summary="Recomendar productos",
)
def create_recommendation(
    request: RecommendationRequest,
) -> RecommendationResponse:
    """
    Recibe las keywords extraídas por el chat y devuelve
    proyectos y productos relacionados.
    """

    try:
        keywords = [
            keyword.model_dump()
            for keyword in request.keywords
        ]

        recommendation = build_recommendation(
            keywords,
            request.search_mode,
        )

        return RecommendationResponse(**recommendation)

    except APIError as error:
        print("ERROR SUPABASE:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible consultar la base de conocimiento.",
        )

    except Exception as error:
        print("ERROR RECOMENDACIÓN:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al generar la recomendación.",
        )
