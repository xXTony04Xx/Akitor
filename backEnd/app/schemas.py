from datetime import datetime
from pydantic import BaseModel


class ProjectResponse(BaseModel):
    id: int
    name: str
    created_at: datetime


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int


class KeywordResponse(BaseModel):
    id: int
    name: str
    type: str


class ProjectProductResponse(BaseModel):
    id: int
    sku: str
    name: str


class ProjectDetailResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    keywords: list[KeywordResponse]
    products: list[ProjectProductResponse]