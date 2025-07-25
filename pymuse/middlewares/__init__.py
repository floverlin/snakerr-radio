from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.enums import ChatType

from storage import UserRepository

from typing import Callable, Any, Awaitable, TypeAlias, Union
from datetime import datetime
import logging

from typing import Any

Handler: TypeAlias = Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]

menues: dict[int, Message | None] = dict()
to_delete: dict[int, list[Message] | None] = dict()


class UpdateUserInfo(BaseMiddleware):
    async def __call__(
        self, handler: Handler, event: Message | CallbackQuery, data: dict[str, Any]
    ) -> Any:
        if (
            event.from_user.id
            and event.from_user.first_name
            and event.from_user.username
        ):
            id = event.from_user.id
            username = event.from_user.first_name
            link = event.from_user.username

            await UserRepository.update(id, username, link)
        else:
            raise Exception()
        result = await handler(event, data)
        return result


class Log(BaseMiddleware):
    async def __call__(
        self, handler: Handler, event: Message | CallbackQuery, data: dict[str, Any]
    ) -> Any:
        id = event.from_user.id
        name = event.from_user.first_name
        text = event.text
        logging.info(
            f"[{datetime.now().strftime("%d.%m.%Y %H:%M")}]event from {name} with id {id} with text {text}"
        )
        result = await handler(event, data)
        return result


class Menu(BaseMiddleware):
    async def __call__(
        self, handler: Handler, event: Message | CallbackQuery, data: dict[str, Any]
    ) -> Any:

        menu = menues.get(event.from_user.id, None)
        delete = to_delete.get(event.from_user.id, None)

        data["menu"] = menu
        data["user_id"] = event.from_user.id

        result: dict[str] | None = await handler(event, data)

        try:
            if delete:
                [await d.delete() for d in delete]
        except Exception:
            print("delete message(s) error")

        if result:
            if isinstance(result, list):
                result = {"delete": result}
            elif isinstance(result, Message):
                result = {"menu": result}

            to_delete[event.from_user.id] = result.get("delete", None)
            menues[event.from_user.id] = result.get("menu", None)
        else:
            to_delete[event.from_user.id] = None
            menues[event.from_user.id] = None


class PrivateChatOnly(BaseMiddleware):
    async def __call__(
        self, handler: Handler, event: Message | CallbackQuery, data: dict[str, Any]
    ) -> Any:
        chat_type = None
        if isinstance(event, Message):
            chat_type = event.chat.type
        elif isinstance(event, CallbackQuery) and event.message:
            chat_type = event.message.chat.type
        else:
            return await handler(event, data)

        if chat_type != ChatType.PRIVATE:
            if isinstance(event, Message):
                await event.answer(
                    "Этот бот работает только в личных сообщениях!",
                    reply_markup=ReplyKeyboardRemove(),
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "Этот бот работает только в личных сообщениях!", show_alert=True
                )
            return

        return await handler(event, data)
