from html import escape
from aiogram import Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

from storage import UserRepository
from middlewares import PrivateChatOnly, UpdateUserInfo, Log, Menu
from filters import IsAdmin
from config import config

from .upload import handle_add, rt as add_router
from .listen import handle_listen, rt as listen_router
from .settings import handle_settings, rt as settings_router
from .chart import handle_chart, rt as chart_router
from .menu import handle_menu, rt as menu_router


rt = Router(name="main")
rt.include_routers(
    add_router, listen_router, settings_router, chart_router, menu_router
)

rt.message.outer_middleware(PrivateChatOnly())

rt.message.middleware(UpdateUserInfo())
rt.message.middleware(Log())
rt.message.middleware(Menu())

rt.callback_query.middleware(Menu())


@rt.message(CommandStart())
async def handle_start(message: Message):
    if await UserRepository.add(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username,
    ):
        await message.answer(
            f"""Привет {html.bold(escape(message.from_user.first_name))}!
Сейчас ты в анонимном режиме
Усли хочешь, чтобы люди видели, что именно ты добавил песню, переключи режим в /settings""",
            parse_mode=ParseMode.HTML,
        )
        return
    await message.answer("Привет!")


@rt.message(Command("menu"))
async def handle_menu_init(message: Message, state: FSMContext):
    return await handle_menu(message, state)


@rt.message(Command("upload"))
async def handle_add_init(message: Message, state: FSMContext, user_id: int):
    return await handle_add(message, state, user_id)


@rt.message(Command("listen"))
async def handle_listen_init(message: Message, state: FSMContext, user_id: int):
    return await handle_listen(message, state, user_id)


@rt.message(Command("settings"))
async def handle_settings_init(message: Message, state: FSMContext, user_id: int):
    return await handle_settings(message, state, user_id)


@rt.message(Command("chart"))
async def handle_chart_init(message: Message, state: FSMContext, user_id: int):
    return await handle_chart(message, state, user_id)


@rt.message(Command("info"))
async def handle_info(message: Message):
    return await message.answer(config.info, reply_markup=ReplyKeyboardRemove())


@rt.message(Command("database"), IsAdmin())
async def handle_database_init(message: Message):
    file = FSInputFile("./database/data.db")
    await message.answer_document(file)


commands = map(
    lambda command: BotCommand(command="/" + command[0], description=command[1]),
    config.commands,
)
