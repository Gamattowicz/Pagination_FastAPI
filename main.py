import json

from fastapi import FastAPI

from database import database, movie_table

app = FastAPI()


@app.get("/")
def home():
    return {"Hello": "World"}


@app.get("/movies")
async def load_movies_to_database():
    with open("movies_examples.json", "r") as f:
        data = json.load(f)
    query = movie_table.insert().values(data)
    await database.connect()
    await database.execute(query)
    await database.disconnect()
