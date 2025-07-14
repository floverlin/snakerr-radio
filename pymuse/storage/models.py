from sqlalchemy import (
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)

    username: Mapped[str]
    link: Mapped[str]
    anon: Mapped[bool]
    timeout: Mapped[datetime | None] = mapped_column(nullable=True)


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)

    uploader_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str]
    artist: Mapped[str]
    comment: Mapped[str | None] = mapped_column(nullable=True)

    user = relationship(User, backref="songs")


class Rating(Base):
    __tablename__ = "ratings"

    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int | None] = mapped_column(nullable=True)
    comment: Mapped[str | None] = mapped_column(nullable=True)

    song = relationship(Song, backref="ratings")
    user = relationship(User, backref="ratings")

    primary_key = PrimaryKeyConstraint(song_id, user_id)
