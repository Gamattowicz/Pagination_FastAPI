from typing import Generic, List, Optional, TypeVar

from pydantic import AnyHttpUrl, BaseModel, Field

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
    nextPageUrl: Optional[AnyHttpUrl] = None
    Field(description="URL to the next page of results if available, otherwise null")
    prevPageUrl: Optional[AnyHttpUrl] = None
    Field(
        description="URL to the previous page of results if available, otherwise null"
    )
    results: List[T] = Field(
        description="List of items returned in response according to the provided parameters"
    )


class PaginatedResponseP(BaseModel, Generic[T]):
    page: int = Field(description="The current page number being displayed")
    per_page: int = Field(description="The number of items displayed on each page")
    totalItems: int = Field(description="Total number of items in the database")
    nextPageUrl: Optional[AnyHttpUrl] = None
    Field(description="URL to the next page of results if available, otherwise null")
    prevPageUrl: Optional[AnyHttpUrl] = None
    Field(
        description="URL to the previous page of results if available, otherwise null"
    )
    results: List[T] = Field(
        description="List of items returned in response according to the provided parameters"
    )
