from aiogram import Router, html
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import ListenSong
from storage import async_session, SongRepository
from storage.models import Rating
from keyboards import Rate

from html import escape


rt = Router(name="listen")


async def handle_listen(message: Message, state: FSMContext, user_id: int):
    song_with_uploader = await SongRepository.get_unrated(user_id)
    if not song_with_uploader:
        await message.answer("Новых песен нет")
        return

    song, user = song_with_uploader
    await state.set_data({"id": song.id})
    await state.set_state(ListenSong.set_rate)
    song.comment = "[без комментария]" if not song.comment else song.comment
    text = f"""Название: {html.bold(escape(song.title))}
Исполнитель: {html.bold(escape(song.artist))}
{"Загрузил: "+html.link(escape(user.username), "https://t.me/" + user.link)+"\nКомментарий: "+song.comment
            if not user.anon
            else "Загрузил: Аноним"}
----------
Оцени после прослушивания"""
    return await message.answer_audio(
        song.id,
        text,
        reply_markup=Rate.inline_keyboard(),
        parse_mode=ParseMode.HTML,
        title=song.title,
        performer=song.artist,
    )


@rt.callback_query(ListenSong.set_rate)
async def handle_rate(callback: CallbackQuery, state: FSMContext, user_id: int):

    await callback.message.delete_reply_markup()

    song_id = await state.get_value("id")
    async with async_session() as session:
        rating = Rating(
            song_id=song_id,
            user_id=callback.from_user.id,
            rating=Rate.int_from_callback(callback.data),
        )
        session.add(rating)
        await session.commit()

    await callback.message.answer(
        f"Оценка поставлена: {Rate.rate_from_callback(callback.data)}"
    )
    await state.clear()
    await handle_listen(callback.message, state, user_id)
