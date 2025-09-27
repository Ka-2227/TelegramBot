from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI
from config import OPENAI_TOKEN
from keyboards.inline import main_menu

router = Router()
client = AsyncOpenAI(api_key=OPENAI_TOKEN)

quiz_state = {}


def quiz_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Новый вопрос", callback_data="new_quiz")],
            [InlineKeyboardButton(text="❌ Закончить квиз", callback_data="end_quiz")]
        ]
    )


async def get_quiz_question(topic: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"Сгенерируй один вопрос по теме {topic}, строго на русском языке."
            }
        ],
        temperature=0.7,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()


async def check_answer(question: str, answer: str) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Проверь правильность ответа на квиз.\n"
                    f"Вопрос: {question}\n"
                    f"Ответ: {answer}\n"
                    'Скажи только одно слово: "правильно" или "неправильно".'
                )
            }
        ],
        temperature=0,
        max_tokens=10
    )
    return response.choices[0].message.content.strip().lower()


@router.message(Command("quiz"))
@router.callback_query(F.data == "quiz_menu")
async def start_quiz(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    quiz_state[user_id] = {"question": None, "topic": "IT"}  # по умолчанию тема IT

    if isinstance(event, types.Message):
        await event.answer("Добро пожаловать в квиз! 🧩", reply_markup=quiz_keyboard())
    else:
        await event.message.answer("Добро пожаловать в квиз! 🧩", reply_markup=quiz_keyboard())
        await event.answer()



@router.callback_query(F.data == "new_quiz")
async def new_quiz(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    topic = quiz_state[user_id]["topic"]

    question = await get_quiz_question(topic)
    quiz_state[user_id]["question"] = question

    await callback.message.answer(f"❓ Вопрос:\n\n{question}", reply_markup=quiz_keyboard())
    await callback.answer()



@router.message(F.text)
async def quiz_answer(message: types.Message):
    user_id = message.from_user.id


    if user_id not in quiz_state or not quiz_state[user_id].get("question"):
        return

    question = quiz_state[user_id]["question"]
    user_answer = message.text.strip()

    try:
        result = await check_answer(question, user_answer)
        if result == "правильно":
            await message.answer("✅ Правильно! Молодец!", reply_markup=quiz_keyboard())
            quiz_state[user_id]["question"] = None
        else:
            await message.answer("❌ Неправильно! Попробуй ещё.", reply_markup=quiz_keyboard())
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при проверке ответа: {e}", reply_markup=quiz_keyboard())



@router.callback_query(F.data == "end_quiz")
async def end_quiz(callback: types.CallbackQuery):
    quiz_state.pop(callback.from_user.id, None)
    await callback.message.answer("🏁 Квиз завершён!", reply_markup=main_menu())
    await callback.answer()
