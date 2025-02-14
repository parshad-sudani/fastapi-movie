"""
FastAPI Movie API
"""

import os
import traceback
import httpx
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import get_db, Base, DATABASE_URL
from models import Movie, Comment
from schemas import MovieCreate, CommentCreate, MovieResponse, CommentUpdate


load_dotenv()
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
OMDB_API_URL = "http://www.omdbapi.com/"


app = FastAPI(title="Movie API",
              description="FastAPI CRUD for Movies and Comments")

STATUS_SUCCESS = "success"
STATUS_FAILED = "fail"
CREATE_SUCCESS_STATUS_CODE = 201


# it's creating talbles in database automatically
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)


@app.post("/movies", response_model=MovieCreate)
def create_movie(movie_title: str, db: Session = Depends(get_db)):
    """
        Fetch movie details from the OMDB API and store them in the database.
        Args:
            movie_title (str): Title of the movie to fetch.
            db (Session): SQLAlchemy database session.
        Returns:
            JSONResponse: Movie creation status and ID if successful.
    """
    try:
        response = httpx.get(f"{OMDB_API_URL}?t={movie_title}&apikey={OMDB_API_KEY}")
        data = response.json()
        print(F"founded data : {data}")

        if data.get("Response") == "False":
            return JSONResponse(
                status_code=404,
                content={
                    "status": STATUS_FAILED,
                    "message": "Movie not found",
                    "data": None
                }
            )
        new_movie = Movie(
            title=data["Title"], genre=data["Genre"], year=int(data["Year"]))
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)
        return JSONResponse(
            status_code=200,
            content={
                "status": STATUS_SUCCESS,
                "message": "Added movie successfully !!",
                "data": {
                    "id": new_movie.id
                }
            }
        )
    except Exception as e:
        # Print stack trace for debugging purposes
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": STATUS_FAILED,
                "message": str(e)
            }
        )


@app.get("/movies")
def read_movies(genre: str = None, year: int = None, db: Session = Depends(get_db)):
    """
    Retrieve movies with optional genre and year filters.
    """
    try:
        query = db.query(Movie)
        print(F"year : {year}")
        if genre:
            query = query.filter(Movie.genre.ilike(f"%{genre}%"))
        if year:
            query = query.filter(Movie.year == year)

        movies = query.all()
        # Map the movies to the required data format
        mapped_data = [
            {
                "id": movie.id,
                "title": movie.title,
                "genre": movie.genre,
                "year": movie.year
            } for movie in movies
        ]
        return JSONResponse(
            status_code=200,
            content={
                "status": STATUS_SUCCESS,
                "message": "Get movies list successfully!",
                "data": mapped_data
            }
        )
    except Exception as e:
        # Print stack trace for debugging purposes
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": STATUS_FAILED,
                "message": str(e)
            }
        )


@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, movie_data: MovieCreate, db: Session = Depends(get_db)):
    """
    Update an existing movie in the database by movie ID.

    Args:
        movie_id (int): The ID of the movie to update.
        movie_data (MovieCreate): The movie data to update with.
        db (Session): The database session.

    Returns:
        Movie: The updated movie object.

    Raises:
        HTTPException: If the movie is not found or an error occurs.
    """
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()

        if movie is None:
            return JSONResponse(
                status_code=404,
                content={
                    "status": STATUS_FAILED,
                    "message": "Movie not found",
                }
            )
        for key, value in movie_data.dict().items():
            setattr(movie, key, value)
        db.commit()
        db.refresh(movie)

        return JSONResponse(
            status_code=200,
            content={
                "status": STATUS_SUCCESS,
                "message": "Update movie detail successfully!",
                "data": MovieResponse.from_orm(movie).dict()
            }
        )
    except Exception as e:
        # Print stack trace for debugging purposes
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": STATUS_FAILED,
                "message": str(e)
            }
        )


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """
    Delete a movie from the database by its movie ID.

    Args:
        movie_id (int): The ID of the movie to delete.
        db (Session): The database session.

    Returns:
        JSONResponse: A response indicating the result of the deletion.
    """
    try:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            return JSONResponse(
                status_code=404,
                content={
                    "status": STATUS_FAILED,
                    "message": "Movie detail not found"
                }
            )

        db.delete(movie)
        db.commit()
        data = {
            "status": STATUS_SUCCESS,
            "message": "Delete movie detail successfully !!",
        }
        return JSONResponse(
            status_code=200,
            content=data
        )
    except Exception as e:
        # Print stack trace for debugging purposes
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": STATUS_FAILED,
                "message": str(e)
            }
        )


@app.post("/comments", response_model=CommentCreate)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """
    Create a new comment for a movie.

    Args:
        comment (CommentCreate): The comment data to create.
        db (Session): The database session.

    Returns:
        JSONResponse: A response containing the status and created comment ID.
    """
    try:
        comment = Comment(**comment.dict())
        db.add(comment)
        db.commit()
        db.refresh(comment)
        data = {
            "status": STATUS_SUCCESS,
            "message": "Added movie comment successfully !!",
            "data": {
                "id": comment.id
            }
        }
        return JSONResponse(
            status_code=200,
            content=data
        )

    except Exception as e:
        # Print stack trace for debugging purposes
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": STATUS_FAILED,
                "message": str(e)
            }
        )


@app.get("/comments")
def read_comments(comment: str = None, movie_id: int = None, db: Session = Depends(get_db)):
    """
    Retrieve comments with optional comment and movie_id filters.
    """
    try:
        query = db.query(Comment)
        if comment:
            query = query.filter(Comment.comment.ilike(f"%{comment}%"))
        if movie_id:
            query = query.filter(Comment.movie_id == movie_id)

        comments = query.all()

        # Map the comments to the required data format
        mapped_data = [
            {
                "id": comment.id,
                "comment": comment.comment,
                "movie_id": comment.movie_id
            } for comment in comments
        ]

        return JSONResponse(
            status_code=200,
            content={
                "status": STATUS_SUCCESS,
                "message": "Get comments list successfully!",
                "data": mapped_data
            }
        )
    except Exception as e:
        # Print stack trace for debugging purposes
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": STATUS_FAILED,
                "message": str(e)
            }
        )


@app.put("/comments/{comment_id}")
def update_comment(comment_id: int, comment_data: CommentUpdate, db: Session = Depends(get_db)):
    """
    Update an existing comment in the database by comment ID.

    Args:
        comment_id (int): The ID of the comment to update.
        comment_data (CommentCreate): The comment data to update with.
        db (Session): The database session.

    Returns:
        comment: The updated comment object.

    Raises:
        HTTPException: If the comment is not found or an error occurs.
    """
    try:
        # Corrected query syntax
        comment = db.query(Comment).filter(Comment.id == comment_id).first()

        if not comment:
            return JSONResponse(
                status_code=404,
                content={
                    "status": STATUS_FAILED,
                    "message": "Comment not found",  # Fixed message: "Movie" -> "Comment"
                }
            )

        # Update the comment fields
        for key, value in comment_data.dict().items():
            setattr(comment, key, value)

        # Commit and refresh the updated comment
        db.commit()
        db.refresh(comment)

        # Return updated comment data (you can also use a Pydantic response model here)
        return JSONResponse(
            status_code=200,
            content={
                "status": STATUS_SUCCESS,
                "message": "Update comment successfully!",
                "data": {
                    "id": comment.id,
                    "comment": comment.comment,
                    "movie_id": comment.movie_id
                }
            }
        )
    except Exception as e:
        # Print stack trace for debugging purposes
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": STATUS_FAILED,
                "message": str(e)
            }
        )


@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """
    Delete a comment from the database by its comment ID.

    Args:
        comment_id (int): The ID of the comment to delete.
        db (Session): The database session.

    Returns:
        JSONResponse: A response indicating the result of the deletion.
    """
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            return JSONResponse(
                status_code=404,
                content={
                    "status": STATUS_FAILED,
                    "message": "comment detail not found"
                }
            )

        db.delete(comment)
        db.commit()
        data = {
            "status": STATUS_SUCCESS,
            "message": "Delete comment detail successfully !!",
        }
        return JSONResponse(
            status_code=200,
            content=data
        )
    except Exception as e:
        # Print stack trace for debugging purposes
        traceback.print_exc()
        return JSONResponse(
            status_code=400,
            content={
                "status": STATUS_FAILED,
                "message": str(e)
            }
        )
