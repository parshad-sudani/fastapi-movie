"""
    models.py - Database Models for FastAPI Movie API
    This module defines the database models for movies and comments using SQLAlchemy.

    Classes:
        Movie: Represents a movie record with title, genre, and year.
        Comment: Represents a user comment linked to a specific movie.

    Relationships:
        - A Comment is associated with a Movie via a foreign key.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Movie(Base):
    """
    Developed by parshad on 2025-02-13
    Here we have defined the movie class for the handle movie's field and field type 
    """
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # Added VARCHAR length
    genre = Column(String(100))
    year = Column(Integer)
    comments = relationship('Comment', back_populates='movie', cascade='all, delete')


class Comment(Base):
    """
    Developed by parshad on 2025-02-13
    Here we have defined the comment class for the handle movie's comment
    """
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id', ondelete='CASCADE'))
    comment = Column(String(500))
    movie = relationship('Movie')
