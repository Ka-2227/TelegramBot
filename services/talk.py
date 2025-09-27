from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI
from config import OPENAI_TOKEN
from keyboards.inline import main_menu
from storage.storage import PERSONALITIES

router = Router()
client = AsyncOpenAI(api_key=OPENAI_TOKEN)


user_personality = {}  # Временное хранилище выбранной личности


def personalities_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Альберт Эйнштейн", callback_data="pers_einstein")],
            [InlineKeyboardButton(text="🍏 Стив Джобс", callback_data="pers_jobs")],
            [InlineKeyboardButton(text="📖 Чынгыз Айтматов", callback_data="pers_chyngyz")],
            [InlineKeyboardButton(text="🚬 Уинстон Черчилль", callback_data="pers_churchill")],
            [InlineKeyboardButton(text="🔄 Случайный человек", callback_data="pers_random")],
            [InlineKeyboardButton(text="🔚 Закончить", callback_data="end_talk")]
        ]
    )

def talk_controls():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="talk_menu")],
            [InlineKeyboardButton(text="🔚 Закончить", callback_data="end_talk")]
        ]
    )


@router.callback_query(F.data == "talk_menu")
@router.message(Command("talk"))
async def cmd_talk(event: types.Message | types.CallbackQuery):

    if isinstance(event, types.Message):
        await event.answer("Выбери личность для диалога:", reply_markup=personalities_keyboard())
    else:
        await event.message.answer("Выбери личность для диалога:", reply_markup=personalities_keyboard())
        await event.answer()


@router.callback_query(F.data.startswith("pers_"))
async def set_personality(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    key = callback.data.split("_")[1]

    user_personality[user_id] = PERSONALITIES[key]

    await callback.message.answer(
        f"Ты выбрал {key.capitalize()}!\nМожешь начать диалог 🗣️",
        reply_markup=talk_controls()
    )
    await callback.answer()


@router.message()
async def talk_with_personality(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_personality:
        return  # Игнорируем сообщение, если личность не выбрана

    prompt = user_personality[user_id]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message.text}
        ],
        max_tokens=500
    )
    answer = response.choices[0].message.content.strip()

    await message.answer(answer, reply_markup=talk_controls())

@router.callback_query(F.data == "back_to_menu")
async def back_to_personalities(callback: types.CallbackQuery):
    """Возврат к выбору личности"""
    await callback.message.answer("Выбери личность для диалога:", reply_markup=personalities_keyboard())
    await callback.answer()


@router.callback_query(F.data == "end_talk")
async def end_talk(callback: types.CallbackQuery):
    """Завершение диалога"""
    user_personality.pop(callback.from_user.id, None)
    await callback.message.answer("Диалог завершён 👋", reply_markup=main_menu())
    await callback.answer()
