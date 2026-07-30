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
    keywords: list[KeywordResponse]
    products: list[ProjectProductResponse]


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
