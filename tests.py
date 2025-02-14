import pytest
from fastapi.testclient import TestClient
from main import app  # Your FastAPI application instance
from database import get_db, Base, DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Movie, Comment
from dotenv import load_dotenv
import os

load_dotenv()

# Setup the testing database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # SQLite for testing purposes
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override for testing


@pytest.fixture
def db():
    # Create the test database session
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture()
def client():
    # Override the get_db dependency in the FastAPI app
    def override_get_db():
        db_session = SessionLocal()
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


def test_create_movie(client, db):
    # Test movie creation by title
    response = client.post("/movies", params={"movie_title": "Inception"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data["data"]


def test_movie_not_found(client):
    # Test movie not found from OMDB API
    response = client.post(
        "/movies", params={"movie_title": "NonExistingMovie"})
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "fail"
    assert data["message"] == "Movie not found"


def test_read_movies(client, db):
    # Add a movie to the database
    movie = Movie(title="Inception", genre="Sci-Fi", year=2010)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Test retrieving movies
    response = client.get("/movies", params={"genre": "Sci-Fi"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) > 0
    assert data["data"][0]["title"] == "Inception"


def test_update_movie(client, db):
    # Add a movie to the database
    movie = Movie(title="Inception", genre="Sci-Fi", year=2010)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Test updating movie details
    response = client.put(f"/movies/{movie.id}", json={"title": "Interstellar", "genre": "Sci-Fi", "year": 2014})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["title"] == "Interstellar"


def test_delete_movie(client, db):
    # Add a movie to the database
    movie = Movie(title="Inception", genre="Sci-Fi", year=2010)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Test deleting movie
    response = client.delete(f"/movies/{movie.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Delete movie detail successfully !!"


def test_create_comment(client, db):
    # Add a movie to the database
    movie = Movie(title="Inception", genre="Sci-Fi", year=2010)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Test creating comment
    response = client.post(
        "/comments", json={"comment": "Great movie!", "movie_id": movie.id})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data["data"]


def test_read_comments(client, db):
    # Add a movie to the database
    movie = Movie(title="Inception", genre="Sci-Fi", year=2010)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Add a comment for the movie
    comment = Comment(comment="Great movie!", movie_id=movie.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Test retrieving comments for the movie
    response = client.get("/comments", params={"movie_id": movie.id})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) > 0
    assert data["data"][0]["comment"] == "Great movie!"


def test_update_comment(client, db):
    # Add a movie to the database
    movie = Movie(title="Inception", genre="Sci-Fi", year=2010)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Add a comment for the movie
    comment = Comment(comment="Great movie!", movie_id=movie.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Test updating comment - make sure you are sending data that fits the Pydantic model
    response = client.put(f"/comments/{comment.id}", json={"comment": "Amazing movie!"})
    
    # Check the status code
    assert response.status_code == 200  # Expect 200 OK if the update is successful
    
    # Check if the response contains the updated comment
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["comment"] == "Amazing movie!"
    

def test_delete_comment(client, db):
    # Add a movie to the database
    movie = Movie(title="Inception", genre="Sci-Fi", year=2010)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    # Add a comment for the movie
    comment = Comment(comment="Great movie!", movie_id=movie.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Test deleting comment
    response = client.delete(f"/comments/{comment.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Delete comment detail successfully !!"
