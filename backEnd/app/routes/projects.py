from fastapi import APIRouter, HTTPException, status
from postgrest.exceptions import APIError

from app.repositories.product_repository import get_products_by_project_id
from app.repositories.project_repository import (
    get_all_projects,
    get_keywords_by_project_id,
    get_project_by_id,
)
from app.schemas import ProjectDetailResponse, ProjectListResponse


router = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects"],
)


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="Listar proyectos",
)
def list_projects() -> ProjectListResponse:

    try:
        projects = get_all_projects()

        return ProjectListResponse(
            projects=projects,
            total=len(projects),
        )

    except APIError as error:
        print("ERROR SUPABASE:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible consultar los proyectos.",
        )

    except Exception as error:
        print("ERROR INTERNO:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al consultar los proyectos.",
        )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Obtener proyecto por ID",
)
def get_project_detail(project_id: int) -> ProjectDetailResponse:

    try:
        project = get_project_by_id(project_id)

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proyecto no encontrado.",
            )

        keywords = get_keywords_by_project_id(project_id)
        products = get_products_by_project_id(project_id)

        return ProjectDetailResponse(
            id=project["id"],
            name=project["name"],
            created_at=project["created_at"],
            keywords=keywords,
            products=products,
        )

    except HTTPException:
        raise

    except APIError as error:
        print("ERROR SUPABASE:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible consultar el proyecto.",
        )

    except Exception as error:
        print("ERROR INTERNO:", repr(error))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error inesperado al consultar el proyecto.",
        )