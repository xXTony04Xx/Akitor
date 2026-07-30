from fastapi import FastAPI, HTTPException, status
from app.database import get_supabase_client
from app.routes.projects import router as projects_router
from app.routes.recommendations import (
    router as recommendations_router,
)



app = FastAPI(
    title="Kiver Backend",
    description="API para recomendar productos a partir de proyectos relacionados.",
    version="1.0.0",
)


app.include_router(projects_router)
app.include_router(recommendations_router)

@app.get(
    "/health",
    tags=["Health"],
    summary="Comprobar el estado de la API",
)
def health_check() -> dict[str, str]:

    return {
        "status": "ok",
        "service": "kiver-backend",
    }


@app.get(
    "/health/database",
    tags=["Health"],
    summary="Comprobar la conexión con Supabase",
)
def database_health_check() -> dict:

    try:
        supabase = get_supabase_client()

        response = (
            supabase
            .table("projects")
            .select("id")
            .limit(1)
            .execute()
        )

        return {
            "status": "ok",
            "service": "kiver-backend",
            "database": "connected",
            "sample": response.data,
        }

    except Exception as error:
        print("ERROR SUPABASE:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible consultar la base de datos.",
        )