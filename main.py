import json

import sqlalchemy
from fastapi import Depends, FastAPI, Query, Request
from fastapi_pagination import LimitOffsetPage, Page, add_pagination
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.databases import paginate
from fastapi_pagination.ext.sqlalchemy import paginate as paginateC
from fastapi_pagination.links import LimitOffsetPage as LimitOffsetPageLink
from fastapi_pagination.links import Page as PageLink
from sqlalchemy.orm import Session

from database import SessionLocal, database, movie_table
from models import Movie, PaginatedResponse, PaginatedResponseC, PaginatedResponseP

app = FastAPI()

add_pagination(app)


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


def get_db():
    db = SessionLocal()
    with db as session:
        yield session


async def paginate_l(
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
    return await paginate_l(request, limit, offset)


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


async def paginate_c(
    request: Request, cursor: str = None, limit: int = 10
) -> PaginatedResponseC[Movie]:
    await database.connect()

    if cursor is not None:
        query = (
            movie_table.select()
            .where(sqlalchemy.text(f"id > {cursor}"))
            .limit(limit + 1)
        )
    else:
        query = movie_table.select().limit(limit + 1)

    movies = await database.fetch_all(query)

    # If we have more movies than max_results, we prepare a next cursor
    if len(movies) > limit:
        next_cursor = str(movies[-1].id)  # Convert to string
        movies = movies[:-1]  # We remove the last movie, as it is not part of this page
    else:
        next_cursor = None

    count_query = sqlalchemy.select(sqlalchemy.func.count()).select_from(movie_table)
    total = await database.fetch_one(count_query)

    await database.disconnect()

    base_url = str(request.base_url)
    next_page = (
        f"{base_url}moviec?cursor={next_cursor}&limit={limit}"
        if next_cursor is not None
        else None
    )

    return {
        "totalItems": total[0],
        "limit": limit,
        "nextCursor": next_cursor,
        "nextPageUrl": next_page,
        "results": movies,
    }


@app.get("/moviec", response_model=PaginatedResponseC[Movie], status_code=200)
async def get_all_movies_c(
    request: Request,
    cursor: str = Query(None),
    limit: int = Query(10, gt=0),
):
    return await paginate_c(request, cursor, limit)


LimitOffsetPage = LimitOffsetPage.with_custom_options(
    limit=Query(10, ge=1, le=100),
)


@app.get("/moviel-p", response_model=Page[Movie], status_code=200)
@app.get("/moviel-pl", response_model=PageLink[Movie], status_code=200)
@app.get("/moviel-l", response_model=LimitOffsetPage[Movie], status_code=200)
@app.get("/moviel-ll", response_model=LimitOffsetPageLink[Movie], status_code=200)
async def get_all_movies_l():
    return await paginate(database, movie_table.select())


@app.get("/moviel-c", response_model=CursorPage[Movie])
async def get_users(db: Session = Depends(get_db)):
    return paginateC(db, sqlalchemy.select(movie_table).order_by(movie_table.c.id))
