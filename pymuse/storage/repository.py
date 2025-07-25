from .session import async_session
from .models import User, Song, Rating
from .schemas import SongSchema, UserSchema

from datetime import datetime, timedelta
from random import choice

from sqlalchemy import select, update, func
from sqlalchemy.orm import aliased


class UserRepository:

    @staticmethod
    async def get_by_id(id: int):
        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == id))
            return UserSchema.model_validate(result.scalar_one())

    @staticmethod
    async def update(id: int, username: str, link: str):
        """update user if his info changed"""
        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == id))
            user = result.scalar_one_or_none()
            if not user:
                return
            if user.username != username or user.link != link:
                await session.execute(
                    update(User)
                    .where(User.id == id)
                    .values(username=username, link=link)
                )
                await session.commit()

    @staticmethod
    async def add(id: int, username: str, link: str):
        """add user if not exist"""
        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == id))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    id=id,
                    username=username,
                    link=link,
                    anon=True,
                )
                session.add(user)
                await session.commit()
                return True
            return False


class SongRepository:
    @staticmethod
    async def get_my_chart(user_id: int, limit: int):
        async with async_session() as session:
            results = await session.execute(
                select(Song)
                .join(Rating, Song.id == Rating.song_id)
                .join(User, User.id == Rating.user_id)
                .where(User.id == user_id)
                .where(Rating.rating >= 4)
                .order_by(func.random())
                .limit(limit)
            )
        return [SongSchema.model_validate(result) for result in results.scalars().all()]

    @staticmethod
    async def get_global_chart(limit: int):
        async with async_session() as session:
            avg_rating = func.avg(Rating.rating)
            results = await session.execute(
                select(Song)
                .join(Rating, Song.id == Rating.song_id)
                .group_by(Song.id)
                .having(avg_rating >= 4)
                .order_by(func.random())
                .limit(limit)
            )
        return [SongSchema.model_validate(result) for result in results.scalars().all()]

    @staticmethod
    async def find_same(title: str, artist: str):
        async with async_session() as session:
            result = await session.execute(
                select(Song)
                .where(func.lower(Song.title) == func.lower(title))
                .where(func.lower(Song.artist) == func.lower(artist))
            )
            song = result.scalar_one_or_none()
            if not song:
                return None
            return SongSchema.model_validate(song)

    @staticmethod
    async def add(file_id: str, uploader_id: int, title: str, artist: str):
        async with async_session() as session:
            song = Song(
                uploader_id=uploader_id,
                id=file_id,
                title=title,
                artist=artist,
            )
            session.add(song)
            session.commit()

    @staticmethod
    async def add_with_timeout(song: SongSchema, timeout: int):
        async with async_session() as session:
            song = Song(**song.model_dump())
            session.add(song)
            await session.execute(
                update(User)
                .where(User.id == song.uploader_id)
                .values(timeout=datetime.now() + timedelta(hours=timeout))
            )
            await session.commit()

    @staticmethod
    async def get_unrated(listener_id: int):
        async with async_session() as session:
            Uploader = aliased(User)
            result = await session.execute(
                select(Song, Uploader)
                .join(Uploader, Uploader.id == Song.uploader_id, isouter=True)
                .join(
                    Rating,
                    (Rating.song_id == Song.id) & (Rating.user_id == listener_id),
                    isouter=True,
                )
                .where(Rating.rating == None)
                .limit(10)  # TODO
            )
            songs_with_users = [
                (SongSchema.model_validate(song), UserSchema.model_validate(user))
                for song, user in result.all()
            ]
        if not songs_with_users:
            return None
        song_with_user = choice(songs_with_users)
        return song_with_user
