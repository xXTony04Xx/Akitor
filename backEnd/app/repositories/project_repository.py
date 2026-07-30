from typing import Any
from app.database import get_supabase_client
from typing import Any, Dict, Optional


def get_all_projects() -> list[dict[str, Any]]:

    supabase = get_supabase_client()

    response = (
        supabase
        .table("projects")
        .select("id, name, created_at")
        .order("id")
        .execute()
    )

    return response.data


def get_project_by_id(project_id: int) -> dict[str, Any]:

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


def get_keywords_by_project_id(project_id: int) -> list[dict[str, Any]]:

    supabase = get_supabase_client()

    response = (
        supabase
        .table("project_keywords")
        .select(
            """
            keyword_id,
            keywords (
                id,
                name,
                type
            )
            """
        )
        .eq("project_id", project_id)
        .execute()
    )

    keywords: list[dict[str, Any]] = []

    for relation in response.data:
        keyword = relation.get("keywords")

        if keyword:
            keywords.append(keyword)

    return keywords