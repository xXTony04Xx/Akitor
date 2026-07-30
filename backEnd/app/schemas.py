from datetime import datetime
from typing import List

from pydantic import BaseModel, Field



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
    keywords: List[KeywordResponse]
    products: List[ProductResponse]


class RecommendationKeywordRequest(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)


class RecommendationRequest(BaseModel):
    keywords: List[RecommendationKeywordRequest] = Field(
        min_length=1
    )


class MatchedKeywordResponse(BaseModel):
    name: str
    type: str
    weight: int


class MatchedProjectResponse(BaseModel):
    id: int
    name: str
    score: int
    matched_keywords: List[MatchedKeywordResponse]


class RecommendedProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    quantity: float
    project_id: int
    project_name: str
    project_score: int


class RecommendationResponse(BaseModel):
    matchedProjects: List[MatchedProjectResponse]
    products: List[RecommendedProductResponse]
    totalProducts: int