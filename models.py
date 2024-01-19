from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Movie(BaseModel):
    id: int
    title: str
    description: str
    director: str
    year: int


class PaginatedResponse(BaseModel, Generic[T]):
    limit: int = Field(description="Number of items returned in the response")
    offset: int = Field(description="Index of the first item returned in the response")
    totalItems: int = Field(description="Total number of items in the database")
    nextPageUrl: Optional[str] = None
    Field(description="URL to the next page of results if available, otherwise null")
    prevPageUrl: Optional[str] = None
    Field(
        description="URL to the previous page of results if available, otherwise null"
    )
    results: List[T] = Field(
        description="List of items returned in response according to the provided parameters"
    )
