import databases
import sqlalchemy
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///data.db"

metadata = sqlalchemy.MetaData()

movie_table = sqlalchemy.Table(
    "movies",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("director", sqlalchemy.String),
    sqlalchemy.Column("year", sqlalchemy.Integer),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

database = databases.Database(DATABASE_URL, force_rollback=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
