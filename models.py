from pydantic import BaseModel


class Movie(BaseModel):
    id: int
    title: str
    description: str
    director: str
    year: int
