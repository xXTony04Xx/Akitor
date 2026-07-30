from typing import Any, Dict, List, Optional

from app.database import get_supabase_client


def get_all_projects() -> List[Dict[str, Any]]:
    """
    Obtiene todos los proyectos.
    """

    supabase = get_supabase_client()

    response = (
        supabase
        .table("projects")
        .select("id, name, created_at")
        .order("id")
        .execute()
    )

    return response.data


def get_project_by_id(
    project_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Obtiene un proyecto por su ID.
    """

    supabase = get_supabase_client()

    response = (
        supabase
        .table("projects")
        .select("id, name, created_at")
        .eq("id", project_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def get_keywords_by_project_id(
    project_id: int,
) -> List[Dict[str, Any]]:
    """
    Obtiene las keywords relacionadas con un proyecto.
    """

    supabase = get_supabase_client()

    relations_response = (
        supabase
        .table("project_keywords")
        .select("keyword_id")
        .eq("project_id", project_id)
        .execute()
    )

    if not relations_response.data:
        return []

    keyword_ids = [
        relation["keyword_id"]
        for relation in relations_response.data
    ]

    keywords_response = (
        supabase
        .table("keywords")
        .select("id, name, type")
        .in_("id", keyword_ids)
        .execute()
    )

    return keywords_response.data


def get_all_projects_with_keywords() -> List[Dict[str, Any]]:
    """
    Obtiene todos los proyectos con sus keywords relacionadas.
    Esta función será utilizada por el recomendador.
    """

    supabase = get_supabase_client()

    projects_response = (
        supabase
        .table("projects")
        .select("id, name, created_at")
        .order("id")
        .execute()
    )

    projects = projects_response.data

    if not projects:
        return []

    relations_response = (
        supabase
        .table("project_keywords")
        .select("project_id, keyword_id")
        .execute()
    )

    keywords_response = (
        supabase
        .table("keywords")
        .select("id, name, type")
        .execute()
    )

    keywords_by_id = {
        keyword["id"]: keyword
        for keyword in keywords_response.data
    }

    keywords_by_project: Dict[int, List[Dict[str, Any]]] = {}

    for relation in relations_response.data:
        project_id = relation["project_id"]
        keyword_id = relation["keyword_id"]

        keyword = keywords_by_id.get(keyword_id)

        if keyword is None:
            continue

        keywords_by_project.setdefault(
            project_id,
            [],
        ).append(keyword)

    result = []

    for project in projects:
        result.append(
            {
                **project,
                "keywords": keywords_by_project.get(
                    project["id"],
                    [],
                ),
            }
        )

    return result