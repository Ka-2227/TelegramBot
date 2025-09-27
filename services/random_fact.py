from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI
from config import OPENAI_TOKEN
from keyboards.inline import main_menu


router = Router()
client = AsyncOpenAI(api_key=OPENAI_TOKEN)


async def get_fact_from_gpt():
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты полезный помощник, который знает факты"},
            {"role": "user", "content": "Дай случайный факт."}
        ]
    )
    return response.choices[0].message.content.strip()


def fact_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Ещё факт", callback_data="more_fact")],
            [InlineKeyboardButton(text="🔚 Закончить", callback_data="end_fact")]
        ]
    )

@router.callback_query(F.data == "fact_menu")
async def send_fact(callback: types.CallbackQuery):
    fact = await get_fact_from_gpt()
    await callback.message.answer(f"🔄 {fact}", reply_markup=fact_keyboard())
    await callback.answer()


@router.callback_query(F.data == "more_fact")
async def more_fact(callback: types.CallbackQuery):
    fact = await get_fact_from_gpt()
    await callback.message.answer(f"🔄 {fact}", reply_markup=fact_keyboard())
    await callback.answer()

@router.callback_query(F.data == "end_fact")
async def end_fact(callback: types.CallbackQuery):
    await callback.message.answer("Главное меню", reply_markup=main_menu())
    await callback.answer()



