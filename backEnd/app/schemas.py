from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

class ProjectResponse(BaseModel):
    id: int
    name: str
    created_at: datetime


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int


class KeywordResponse(BaseModel):
    id: int
    name: str
    type: str


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    quantity: float


class ProjectDetailResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    keywords: list[KeywordResponse]
    products: list[ProductResponse]


class AIResponseRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=20_000,
        description="Instrucción o pregunta que se enviará al modelo.",
        examples=["Resume las ventajas de este producto en tres puntos."],
    )


class AIResponse(BaseModel):
    id: str
    model: str
    output: str


class RecommendationKeyword(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)


class RecommendationRequest(BaseModel):
    keywords: list[RecommendationKeyword] = Field(min_length=1)


class MatchedKeywordResponse(RecommendationKeyword):
    weight: int


class MatchedProjectResponse(BaseModel):
    id: int
    name: str
    score: int
    matched_keywords: list[MatchedKeywordResponse]


class RecommendedProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    project_id: int
    project_name: str
    project_score: int


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    matched_projects: list[MatchedProjectResponse] = Field(
        validation_alias="matchedProjects",
        serialization_alias="matchedProjects",
    )
    products: list[RecommendedProductResponse]
    total_products: int = Field(
        validation_alias="totalProducts",
        serialization_alias="totalProducts",
    )
