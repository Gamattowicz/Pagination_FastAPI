import json

import sqlalchemy
from fastapi import FastAPI, Query, Request

from database import database, movie_table
from models import Movie, PaginatedResponse, PaginatedResponseP

app = FastAPI()


@app.get("/")
def home():
    return {"Hello": "World"}


@app.post("/movies", response_model=dict, status_code=201)
async def load_movies_to_database():
    with open("movies_examples.json", "r") as f:
        data = json.load(f)
    await database.connect()
    for movie in data:
        query = movie_table.select().where(movie_table.c.id == movie["id"])
        result = await database.fetch_one(query)
        if result is None:
            query = movie_table.insert().values(movie)
            await database.execute(query)
    await database.disconnect()
    return {"status": "Movies loaded successfully"}


async def paginate(
    request: Request, limit: int, offset: int
) -> PaginatedResponse[Movie]:
    await database.connect()
    query = movie_table.select().limit(limit).offset(offset)
    movies = await database.fetch_all(query)
    count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(movie_table)
    total = await database.fetch_one(count_query)
    base_url = str(request.base_url)
    next_page = (
        f"{base_url}movie?limit={limit}&offset={offset + limit}"
        if offset + limit < total[0]
        else None
    )
    prev_page = (
        f"{base_url}movie?limit={limit}&offset={max(0, offset - limit)}"
        if offset - limit >= 0
        else None
    )
    await database.disconnect()

    return {
        "limit": limit,
        "offset": offset,
        "totalItems": total[0],
        "nextPageUrl": next_page,
        "prevPageUrl": prev_page,
        "results": movies,
    }


@app.get("/movie", response_model=PaginatedResponse[Movie], status_code=200)
async def get_all_movies(
    request: Request,
    limit: int = Query(10, gt=0),
    offset: int = Query(0, ge=0),
):
    return await paginate(request, limit, offset)


async def paginate_p(
    request: Request, page: int, per_page: int
) -> PaginatedResponseP[Movie]:
    offset = (page - 1) * per_page
    await database.connect()
    query = movie_table.select().limit(per_page).offset(offset)
    movies = await database.fetch_all(query)
    count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(movie_table)
    total = await database.fetch_one(count_query)
    base_url = str(request.base_url)
    next_page = (
        f"{base_url}moviep?page={page + 1}&per_page={per_page}"
        if offset + per_page < total[0]
        else None
    )
    prev_page = (
        f"{base_url}moviep?page={page - 1}&per_page={per_page}" if page > 1 else None
    )
    await database.disconnect()

    return {
        "page": page,
        "per_page": per_page,
        "totalItems": total[0],
        "nextPageUrl": next_page,
        "prevPageUrl": prev_page,
        "results": movies,
    }


@app.get("/moviep", response_model=PaginatedResponseP[Movie], status_code=200)
async def get_all_movies_p(
    request: Request,
    page: int = Query(1, gt=0),
    per_page: int = Query(10, gt=0),
):
    return await paginate_p(request, page, per_page)
