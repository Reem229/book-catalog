import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
            'picture': self.picture,
        }


class BookCatalog(Base):
    __tablename__ = 'bookcatalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    author = Column(String(250), nullable=False)
    description = Column(String(250))
    pages = Column(String(100), nullable=False)
    picture = Column(String(250), nullable=False)
    bookcatalog_id = Column(Integer, ForeignKey('bookcatalog.id'))
    bookcatalog = relationship(BookCatalog)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'author': self.author,
            'description': self.description,
            'pages': self.pages,
            'picture': self.picture,
            'bookcatalog_id': self.bookcatalog_id,
        }


engine = create_engine('sqlite:///bookscatalog.db')


Base.metadata.create_all(engine)
