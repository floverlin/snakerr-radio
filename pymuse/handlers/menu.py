from html import escape
from aiogram import Router, F, html
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from storage import UserRepository
from keyboards import NewInlineKeyboard

from .upload import handle_add
from .listen import handle_listen
from .settings import handle_settings
from .chart import handle_chart

rt = Router(name="menu")

main_kb = NewInlineKeyboard(
    [
        [("🎵 Слушать", "menu_listen"), ("➕ Загрузить", "menu_upload")],
        [("⚙️ Настройки", "menu_settings"), ("🔊 Чарт", "menu_chart")],
    ]
)


async def handle_menu(message: Message, state: FSMContext):
    await state.clear()
    user = await UserRepository.get_by_id(message.from_user.id)
    return [
        await message.answer(
            f"Здравствуйте, {html.bold(escape(message.from_user.first_name))}!\n\
Вы{" " if user.anon else " не "}в анонимном режиме\n\
Веберите пункт меню:",
            reply_markup=main_kb.keyboard,
            parse_mode=ParseMode.HTML,
        )
    ]


@rt.callback_query(F.data.startswith("menu_"))
async def handle_menu_choose(callback: CallbackQuery, state: FSMContext, user_id: int):
    await callback.answer()
    match callback.data[5:]:
        case "listen":
            return await handle_listen(callback.message, state, user_id)
        case "upload":
            return await handle_add(callback.message, state, user_id)
        case "settings":
            return await handle_settings(callback.message, state, user_id)
        case "chart":
            return await handle_chart(callback.message, state, user_id)
