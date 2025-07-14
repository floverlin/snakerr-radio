from aiogram import Router
from aiogram.types import Message, InputMediaAudio, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import ListenChart
from storage import SongRepository
from keyboards import NewInlineKeyboard


rt = Router(name="chart")
MY_CHART = "Мой чарт"
GLOBAL_CHART = "Глобальный чарт"
chart_kb = NewInlineKeyboard([[(MY_CHART, MY_CHART)], [(GLOBAL_CHART, GLOBAL_CHART)]])

songs_kb = NewInlineKeyboard([[("5", "5"), ("7", "7"), ("10", "10")]])


async def handle_chart(message: Message, state: FSMContext, user_id: int):
    await state.set_state(ListenChart.select_chart)
    return await message.answer(
        "Выберите, что будете слушать:", reply_markup=chart_kb.keyboard
    )


@rt.callback_query(ListenChart.select_chart)
async def handle_select_chart(
    callback: CallbackQuery, state: FSMContext, menu: Message
):
    await state.set_state(ListenChart.select_songs)
    await state.update_data(chart=callback.data)
    await callback.answer()
    return [
        await menu.edit_text(
            "Сколько треков вам передать?", reply_markup=songs_kb.keyboard
        )
    ]


@rt.callback_query(ListenChart.select_songs)
async def handle_select_chart(
    callback: CallbackQuery, state: FSMContext, menu: Message
):
    chart = await state.get_value("chart")
    await callback.answer()
    limit = int(callback.data)
    songs = []
    if chart == MY_CHART:
        songs = await SongRepository.get_my_chart(callback.from_user.id, limit=limit)
    elif chart == GLOBAL_CHART:
        songs = await SongRepository.get_global_chart(limit=limit)

    if not songs:
        await callback.message.answer("Песен нет")

    media = [InputMediaAudio(media=song.id) for song in songs]
    await callback.message.answer_media_group(media)
    await state.clear()
