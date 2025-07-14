from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from sqlalchemy import select, update

from states import Settings
from storage import async_session
from storage.models import User
from keyboards import YesNo
from storage.schemas import UserSchema


rt = Router(name="settings")


async def handle_settings(message: Message, state: FSMContext, user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = UserSchema.model_validate(result.scalar_one_or_none())
    await state.set_state(Settings.setting)
    await message.answer(
        f"{"Вы в анонимном режиме" if user.anon else "Вы не в анонимном режиме"}\nПереключить?",
        reply_markup=YesNo.reply_keyboard(),
    )


@rt.message(Settings.setting)
async def handle_change_anon(message: Message, state: FSMContext):
    if not YesNo.contains(message.text):
        await message.answer("Неизвестная команда")
        return
    match message.text:
        case YesNo.yes.value:
            async with async_session() as session:
                result = await session.execute(
                    select(User).where(User.id == message.from_user.id)
                )
                user = UserSchema.model_validate(result.scalar_one_or_none())
                result = await session.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(anon=not user.anon)
                    .returning(User.anon)
                )
                await session.commit()
                status = result.scalar_one()
            await state.clear()
            await message.answer(
                f"Режим сменен на {"анонимный" if status else "не анонимный"}",
                reply_markup=ReplyKeyboardRemove(),
            )
        case YesNo.no.value:
            await state.clear()
            await message.answer("Режим не изменен", reply_markup=ReplyKeyboardRemove())
