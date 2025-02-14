"""
This module defines Pydantic models for the FastAPI Movie API, including models 
for creating, updating, and responding with movie and comment data.

Classes:
    - MovieCreate: Pydantic model for creating a new movie.
    - MovieUpdate: Pydantic model for updating an existing movie.
    - MovieResponse: Pydantic model for movie response data.
    - CommentCreate: Pydantic model for creating a new comment for a movie.
    - CommentUpdate: Pydantic model for updating an existing comment.
"""

from typing import Optional
from pydantic import BaseModel, Field


class MovieCreate(BaseModel):
    """
    Pydantic model for creating a new movie.
    """
    title: str = Field(..., example="Inception")
    genre: Optional[str] = Field(None, example="Action, Sci-Fi")
    year: Optional[int] = Field(None, example=2010)


class MovieUpdate(BaseModel):
    """
    Pydantic model for updating an existing movie.
    """
    title: Optional[str] = Field(None, example="Inception")
    genre: Optional[str] = Field(None, example="Action, Sci-Fi")
    year: Optional[int] = Field(None, example=2010)


class MovieResponse(BaseModel):
    """
    Pydantic model for movie response data.
    """
    id: int
    title: str
    genre: str
    year: int

    class Config:
        """
        config class of movie reesponse    
        """
        from_attributes = True
        orm_mode = True


class CommentCreate(BaseModel):
    comment: str = Field(..., example="Great movie!")
    movie_id: int


class CommentUpdate(BaseModel):
    """
    Pydantic model for updating an existing comment.
    """
    comment: Optional[str] = Field(None, example="Updated review.")
