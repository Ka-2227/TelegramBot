from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI
from config import OPENAI_TOKEN
from keyboards.inline import main_menu

router = Router()
client = AsyncOpenAI(api_key=OPENAI_TOKEN)

active_chat = {}


chat_controls = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔚 Закончить", callback_data="end_chat")]
    ]
)

@router.callback_query(F.data == "chat_menu")
@router.message(Command("chat"))
async def start_chat(message: types.Message):
    user_id = message.from_user.id
    active_chat[user_id] = True  # Включаем режим диалога

    await message.answer(
        "Чат режим активирован! 🗣️\nМожешь писать любые сообщения, а я буду отвечать.",
        reply_markup=chat_controls
    )


@router.message()
async def chat_handler(message: types.Message, answer=None):
    user_id = message.from_user.id


    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты дружелюбный помощник для свободного общения."},
            {"role": "user", "content": message.text}
        ],
        max_tokens=500
    )
    await message.answer(answer, reply_markup=chat_controls)


@router.callback_query(lambda c: c.data == "end_chat")
@router.message(Command("end"))
async def end_chat(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    active_chat.pop(user_id, None)

    if isinstance(event, types.Message):
        await event.answer("Чат завершён 👋", reply_markup=main_menu())
    else:
        await event.message.answer("Чат завершён 👋", reply_markup=main_menu())
        await event.answer()
