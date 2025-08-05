from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import UploadSong
from storage import SongRepository, UserRepository
from storage.schemas import SongSchema
from keyboards import NewReplyKeyboard
from config import config
from modules.downloader import download, valid_size
from modules.renamer import rename
from modules.youtube import download as download_from_youtube

from datetime import datetime
from enum import Enum


class AddCancel(Enum):
    ADD = "Добавить"
    CANCEL = "Отмена"


AddCancelKeyboard = NewReplyKeyboard([[AddCancel.ADD.value], [AddCancel.CANCEL.value]])


class SaveCancel(Enum):
    SAVE = "Сохранить"
    CANCEL = "Отмена"


SaveCancelKeyboard = NewReplyKeyboard(
    [[SaveCancel.SAVE.value], [SaveCancel.CANCEL.value]]
)


rt = Router(name="upload")


async def handle_add(message: Message, state: FSMContext, user_id: int):

    # get user
    user = await UserRepository.get_by_id(user_id)

    # check timeout
    if user.timeout and user.timeout > datetime.now():
        delta = (user.timeout - datetime.now()).seconds
        hours, minutes = delta // 3600, delta % 3600 // 60
        await message.answer(
            f"Вы еще не можете загружать новые песни\nЗагрузка будет доступна через {hours}:{minutes}"
        )
        return

    await state.set_state(UploadSong.wait)
    return [
        await message.answer(
            "Отправь (перешли) мне песню или ссылку для скачивания (например: https://download.ru/song)"
        )
    ]


@rt.message(UploadSong.wait)
async def handle_upload(message: Message, state: FSMContext):
    data = dict(
        id=None,
        uploader_id=message.from_user.id,
        title=None,
        init_title=None,
        artist=None,
        init_artist=None,
        comment=None,
    )
    audio_info = None

    if message.audio:
        if not valid_size(message.audio.file_size):
            await message.answer("Файл слишком большой!\nМаксимальный размер - 50МБ")
            await state.clear()
            return

        data["id"] = message.audio.file_id
        data["init_title"] = message.audio.title
        data["init_artist"] = message.audio.performer

    elif message.text:
        if not message.text.startswith(("http://", "https://")):
            await message.answer(
                "Неверная ссылка (она должна начинаться с http или https)"
            )
            await state.clear()
            return

        if message.text.startswith("https://www.youtube.com/watch"):
            wait_message = await message.answer("Подождите, файл скачивается...")
            downloaded = await download_from_youtube(message.text)
            if not downloaded:
                await message.answer("Произошла ошибка или файл слишком большой")
                await wait_message.delete()
                await state.clear()
                return

            async with downloaded as file:
                audio_info = await message.answer_audio(
                    file.file,
                    title=file.title,
                    performer=file.artist,
                )
                await wait_message.delete()
                data["id"] = audio_info.audio.file_id
        else:
            wait_message = await message.answer("Подождите, файл скачивается...")
            downloaded = await download(message.text)
            if not downloaded:
                await message.answer("Произошла ошибка или файл слишком большой")
                await wait_message.delete()
                await state.clear()
                return
            async with downloaded as file:
                audio_info = await message.answer_audio(
                    file.file,
                    title=file.title,
                    performer=file.artist,
                )
                await wait_message.delete()
                data["id"] = audio_info.audio.file_id

    await state.update_data(**data)

    await state.set_state(UploadSong.set_title)
    init_title = await state.get_value("init_title")
    return [
        m
        for m in (
            await message.answer(
                f"Введите название песни...{f"\n(# = {init_title})" if init_title else ""}"
            ),
            audio_info,
        )
        if m
    ]


@rt.message(F.text, UploadSong.set_title)
async def handle_set_title(message: Message, state: FSMContext):
    text = message.text
    init_title = await state.get_value("init_title")
    if text.strip() == "#" and init_title:
        await state.update_data(title=init_title)
    else:
        await state.update_data(title=text)

    await state.set_state(UploadSong.set_artist)
    init_artist = await state.get_value("init_artist")
    return [
        await message.answer(
            f"Название: {await state.get_value("title")}\nНапишите исполнителя песни...{f"\n(# = {init_artist})" if init_artist else ""}"
        )
    ]


@rt.message(F.text, UploadSong.set_artist)
async def handle_set_artist(message: Message, state: FSMContext):
    text = message.text
    init_artist = await state.get_value("init_artist")
    if text.strip() == "#" and init_artist:
        await state.update_data(artist=init_artist)
    else:
        await state.update_data(artist=text)

    same = await SongRepository.find_same(
        await state.get_value("title"),
        await state.get_value("artist"),
    )
    if same:
        await state.set_state(UploadSong.same)
        return [
            await message.answer_audio(
                same.id,
                caption=f"Название: {await state.get_value("title")}\n\
Исполнитель: {await state.get_value("artist")}\n\
Уже есть файл с такими данными\n\
Если это он же, лучше не добавлять копию",
                reply_markup=AddCancelKeyboard.keyboard,
            )
        ]

    await state.set_state(UploadSong.set_comment)
    return [
        await message.answer(
            f"Название: {await state.get_value("title")}\n\
Исполнитель: {await state.get_value("artist")}\n\
Напишите комментарий, почему Вам захотелось поделиться этим треком\n\
или оставьте решетку # для отправки без комментария"
        )
    ]


@rt.message(UploadSong.same)
async def handle_same(message: Message, state: FSMContext):
    if not AddCancelKeyboard.contains(message.text):
        await message.answer("Неизвестная команда")
        return

    if message.text == AddCancel.ADD.value:
        await state.set_state(UploadSong.set_comment)
        return [
            await message.answer(
                f"Название: {await state.get_value("title")}\n\
Исполнитель: {await state.get_value("artist")}\n\
Напишите комментарий, почему Вам захотелось поделиться этим треком\n\
или оставьте решетку # для отправки без комментария"
            )
        ]

    if message.text == AddCancel.CANCEL.value:
        await state.clear()
        await message.answer("Добавление песни отменено")
        return


@rt.message(F.text, UploadSong.set_comment)
async def handle_set_comment(message: Message, state: FSMContext):
    if message.text == "#":
        await state.update_data(comment=None)
    else:
        await state.update_data(comment=message.text)

    await state.set_state(UploadSong.confirm)
    return [
        await message.answer(
            f"Название: {await state.get_value('title')}\n\
Исполнитель: {await state.get_value('artist')}\n\
Комментарий: {cmnt if (cmnt := await state.get_value("comment")) else "[без комментария]"}\n\
Сохранить?",
            reply_markup=SaveCancelKeyboard.keyboard,
        )
    ]


@rt.message(UploadSong.confirm)
async def handle_confirm(message: Message, state: FSMContext):
    if not SaveCancelKeyboard.contains(message.text):
        await message.answer("Неизвестная команда")
        return

    if message.text == SaveCancel.SAVE.value:
        audio_message = await message.answer_audio(
            await state.get_value("id"), caption="Подготовка... подождите..."
        )
        async with await rename(audio_message.audio.file_id) as renamed:
            renamed_audio_message = await message.answer_audio(
                renamed.file,
                caption="Обновление информации...",
                title=await state.get_value("title"),
                performer=await state.get_value("artist"),
            )
            await state.update_data(id=renamed_audio_message.audio.file_id)
        await audio_message.delete()
        await SongRepository.add_with_timeout(
            SongSchema(**await state.get_data()),
            config.timeout,
        )

        if config.timeout == 0:
            await message.answer("Песня сохранена!")
        else:
            await message.answer(
                f"Песня сохранена!\nЗагрузить новую можно будет через {config.timeout} час{choose_end(config.timeout)}"
            )
        await renamed_audio_message.delete()

    if message.text == SaveCancel.CANCEL.value:
        await message.answer("Добавление песни отменено")

    await state.clear()


def choose_end(n: int) -> str:
    n = n % 10
    if n == 1:
        return ""
    elif n in (2, 3, 4):
        return "а"
    else:
        return "ов"
