import json
from typing import List

from fastapi import FastAPI

from database import database, movie_table
from models import Movie

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


@app.get("/movie", response_model=List[Movie])
async def get_all_movies():
    query = movie_table.select()
    await database.connect()
    results = await database.fetch_all(query)
    await database.disconnect()
    return results
