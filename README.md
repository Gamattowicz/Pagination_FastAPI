# FastAPI Pagination Tutorial

This project is a tutorial on how to implement pagination in a FastAPI application. We use encode/databases libraries for database interactions and sqlite as the database.

## Project Structure

- `main.py`: This is the main file where the FastAPI application is created and routes are defined.
- `database.py`: This file sets up the database connection and defines the table schema.
- `models.py`: This file defines the Pydantic models for our application.
- `movies_examples.json`: This file contains example movie data in JSON format.

## Setup

1. Clone the repository:

```sh
git clone <repository_url>
```

2. Navigate to the project directory:

```sh
cd <project_directory>
```

3. Create a virtual environment and activate it:

```sh
python3 -m venv venv
source venv/bin/activate
```

4. Install the required packages:

```sh
pip install -r requirements.txt
```

## Running the Application

To run the application, use the following command:

```sh
uvicorn main:app --reload
```

The application will be available at http://localhost:8000.

## Endpoints

GET /: Returns a simple greeting.
GET /movies: Loads the movie data from movies_examples.json into the database.
