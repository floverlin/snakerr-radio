from aiogram.fsm.state import StatesGroup, State


class UploadSong(StatesGroup):
    wait = State()
    set_title = State()
    set_artist = State()
    same = State()
    set_comment = State()
    confirm = State()


class ListenSong(StatesGroup):
    set_rate = State()


class Settings(StatesGroup):
    setting = State()


class ListenChart(StatesGroup):
    select_chart = State()
    select_songs = State()
    listen = State()
