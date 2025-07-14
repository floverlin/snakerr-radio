from pydantic import BaseModel
import datetime


class SongSchema(BaseModel):
    id: str
    uploader_id: int
    title: str
    artist: str
    comment: str | None

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    id: int
    username: str
    anon: bool
    link: str
    timeout: datetime.datetime | None

    class Config:
        from_attributes = True
