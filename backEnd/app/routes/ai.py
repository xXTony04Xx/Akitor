import asyncio
from collections.abc import AsyncIterable

from fastapi import APIRouter, HTTPException, status
from fastapi.sse import EventSourceResponse, ServerSentEvent
from google.genai.errors import APIError
from pydantic import ValidationError

from app.schemas import AIResponse, AIResponseRequest
from app.services.gemini_service import generate_text


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=AIResponse,
    summary="Conversar con Akitor",
)
async def chat(payload: AIResponseRequest) -> AIResponse:
    print("[AKITOR] POST /chat iniciado.", flush=True)
    try:
        response_id, model, output = await generate_text(
            payload.prompt,
            payload.history,
        )

        print(
            f"[AKITOR] Solicitud completada con el modelo {model}.",
            flush=True,
        )
        return AIResponse(
            id=response_id,
            model=model,
            output=output,
        )

    except ValidationError as error:
        print("[AKITOR] Falta configurar Gemini.", flush=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La integración con Gemini no está configurada.",
        ) from error

    except APIError as error:
        print(
            f"[AKITOR] Gemini respondió con error HTTP {error.code}: "
            f"{error.status} - {error.message}",
            flush=True,
        )
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


@router.post(
    "/stream",
    response_class=EventSourceResponse,
    summary="Conversar con Akitor y recibir progreso",
)
async def stream_chat(
    payload: AIResponseRequest,
) -> AsyncIterable[ServerSentEvent]:
    queue: asyncio.Queue[tuple[str, dict] | None] = asyncio.Queue()

    async def progress(event: str, data: dict) -> None:
        await queue.put((event, data))

    async def run_chat() -> None:
        try:
            response_id, model, output = await generate_text(
                payload.prompt,
                payload.history,
                progress,
            )
            await queue.put(
                (
                    "result",
                    {
                        "id": response_id,
                        "model": model,
                        "output": output,
                    },
                )
            )
        except ValidationError:
            await queue.put(
                (
                    "error",
                    {
                        "message": (
                            "La integración con Gemini no está configurada."
                        )
                    },
                )
            )
        except APIError as error:
            await queue.put(
                (
                    "error",
                    {
                        "message": "Gemini no pudo procesar la solicitud.",
                        "code": error.code,
                    },
                )
            )
        finally:
            await queue.put(None)

    task = asyncio.create_task(run_chat())

    try:
        while True:
            item = await queue.get()
            if item is None:
                break

            event, data = item
            yield ServerSentEvent(event=event, data=data)
    finally:
        if not task.done():
            task.cancel()
