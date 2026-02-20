from datetime import datetime

from pydantic import BaseModel


# --- Households ---

class CreateHouseholdRequest(BaseModel):
    household_name: str
    your_name: str


class JoinHouseholdRequest(BaseModel):
    join_code: str
    your_name: str


class HouseholdResponse(BaseModel):
    household_name: str
    join_code: str
    your_name: str
    token: str


# --- Items ---

class AddItemRequest(BaseModel):
    raw_input: str


class SearchRequest(BaseModel):
    query: str


class ItemResponse(BaseModel):
    id: int
    name: str
    location: str
    category: str
    added_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AddItemResponse(BaseModel):
    message: str
    item: ItemResponse


class SearchResultItem(BaseModel):
    id: int
    name: str
    location: str
    category: str
    score: int


class SearchResponse(BaseModel):
    query: str
    message: str = ""
    results: list[SearchResultItem]


class ItemListResponse(BaseModel):
    count: int
    items: list[ItemResponse]


class DeleteResponse(BaseModel):
    message: str


# --- Errors (returned as 200 for Siri Shortcuts compatibility) ---

class ErrorResponse(BaseModel):
    error: str


# --- Health ---

class HealthResponse(BaseModel):
    status: str
