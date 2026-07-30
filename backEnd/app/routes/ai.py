from fastapi import APIRouter, HTTPException, status
from google.genai.errors import APIError
from pydantic import ValidationError

from app.schemas import AIResponse, AIResponseRequest
from app.services.gemini_service import generate_text


router = APIRouter(
    prefix="/api/v1/ai",
    tags=["AI"],
)


@router.post(
    "/responses",
    response_model=AIResponse,
    summary="Generar una respuesta con Gemini",
)
async def create_ai_response(payload: AIResponseRequest) -> AIResponse:
    try:
        response_id, model, output = await generate_text(payload.prompt)

        return AIResponse(
            id=response_id,
            model=model,
            output=output,
        )

    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La integración con Gemini no está configurada.",
        ) from error

    except APIError as error:
        if error.code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Gemini alcanzó el límite del nivel gratuito.",
            ) from error

        if error.code in {401, 403}:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini rechazó las credenciales configuradas.",
            ) from error

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gemini no pudo procesar la solicitud.",
        ) from error
