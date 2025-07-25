from typing import Any
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.types import ReplyKeyboardRemove

from enum import Enum


class Rate(Enum):
    one = "1 💩"
    two = "2 ⭐️"
    three = "3 ⭐️"
    four = "4 ⭐️"
    five = "5 ❤️‍🔥"

    @classmethod
    def contains(cls, string: str):
        return string in {item.value for item in cls}

    @classmethod
    def int_from_message(cls, string) -> int:
        match string:
            case cls.one.value:
                return 1
            case cls.two.value:
                return 2
            case cls.three.value:
                return 3
            case cls.four.value:
                return 4
            case cls.five.value:
                return 5

    @classmethod
    def int_from_callback(cls, string) -> int:
        return int(string[-1:])

    @classmethod
    def rate_from_callback(cls, string) -> int:
        match cls.int_from_callback(string):
            case 1:
                return cls.one.value
            case 2:
                return cls.two.value
            case 3:
                return cls.three.value
            case 4:
                return cls.four.value
            case 5:
                return cls.five.value

    @classmethod
    def inline_keyboard(cls):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=cls.one, callback_data="rate_1"),
                    InlineKeyboardButton(text=cls.two, callback_data="rate_2"),
                ],
                [
                    InlineKeyboardButton(text=cls.three, callback_data="rate_3"),
                    InlineKeyboardButton(text=cls.four, callback_data="rate_4"),
                ],
                [
                    InlineKeyboardButton(text=cls.five, callback_data="rate_5"),
                ],
            ],
        )

    @classmethod
    def reply_keyboard(cls):
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=cls.one),
                    KeyboardButton(text=cls.two),
                ],
                [
                    KeyboardButton(text=cls.three),
                    KeyboardButton(text=cls.four),
                ],
                [
                    KeyboardButton(text=cls.five),
                ],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )


class YesNo(Enum):
    yes = "Да"
    no = "Нет"

    @classmethod
    def reply_keyboard(cls):
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=cls.yes), KeyboardButton(text=cls.no)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    @classmethod
    def contains(cls, string: str):
        return string in {item.value for item in cls}


class Keyboard:
    _values: set[str] = set()
    _keyboard: Any = ReplyKeyboardRemove()

    def contains(self, string: str) -> bool:
        return string in self._values

    @property
    def keyboard(self):
        return self._keyboard


class NewReplyKeyboard(Keyboard):
    def __init__(self, buttons: list[list[str]]):
        self._keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=text) for text in row] for row in buttons],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        values = set()
        for row in buttons:
            for text in row:
                values.add(text)

        self._values = values


class NewInlineKeyboard(Keyboard):
    def __init__(self, buttons: list[list[tuple[str, str]]]):
        self._keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=text, callback_data=callback_data)
                    for text, callback_data in row
                ]
                for row in buttons
            ],
        )

        values = set()
        for row in buttons:
            for text, _ in row:
                values.add(text)

        self._values = values
