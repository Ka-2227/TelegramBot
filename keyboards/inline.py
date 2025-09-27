from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎲 Рандомный факт	Удивительное открытие", callback_data="fact_menu")],
            [InlineKeyboardButton(text="🧑‍🎤 Диалог с известной личностью", callback_data="talk_menu")],
            [InlineKeyboardButton(text="🤖 ChatGPT интерфейс	Генерация текста и ответы на вопросы.", callback_data="gpt_menu")],
            [InlineKeyboardButton(text="🧠 Квиз	Проверка и пополнение знаний", callback_data="quiz_menu")],
            [InlineKeyboardButton(text="🤖 Переводчик	Быстрый и точный перевод.", callback_data="translator_menu")],
            [InlineKeyboardButton(text="🎬 Фильмы	Рекомендации", callback_data="recommend_menu")]
        ]
    )

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        """Привет! 🤖 Я твой личный ИИ-помощник и готов сделать твой день интереснее и продуктивнее.
        Выбери действие:""",
        reply_markup=main_menu()
    )