from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI
from config import OPENAI_TOKEN
from keyboards.inline import main_menu

router = Router()
client = AsyncOpenAI(api_key=OPENAI_TOKEN)


user_context = {}

def recommendations_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎬 Фильмы", callback_data="rec_movies")],
            [InlineKeyboardButton(text="📚 Книги", callback_data="rec_books")],
            [InlineKeyboardButton(text="🎵 Музыка", callback_data="rec_music")],
            [InlineKeyboardButton(text="🔚 Закончить", callback_data="end_rec")]
        ]
    )

def genre_keyboard(category: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Экшен", callback_data=f"genre_{category}_action")],
            [InlineKeyboardButton(text="Комедия", callback_data=f"genre_{category}_comedy")],
            [InlineKeyboardButton(text="Драма", callback_data=f"genre_{category}_drama")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="recommend_menu")]
        ]
    )

async def get_recommendations(category: str, genre: str, dislikes: list):
    try:
        filter_text = ""
        if dislikes:
            filter_text = f"Не включай эти произведения: {', '.join(dislikes)}."

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты эксперт по рекомендациям фильмов, книг и музыки."},
                {"role": "user", "content": f"Дай 5 рекомендаций в категории '{category}' жанра '{genre}'. {filter_text}"}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Ошибка: {e}"


@router.callback_query(F.data == "recommend_menu")
async def send_recommendations_menu(callback: types.CallbackQuery):
    await callback.message.answer("Выберите категорию:", reply_markup=recommendations_keyboard())
    await callback.answer()


@router.callback_query(F.data.in_(["rec_movies", "rec_books", "rec_music"]))
async def select_category(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    await callback.message.answer(f"Вы выбрали категорию: {category}. Теперь выберите жанр:", reply_markup=genre_keyboard(category))
    await callback.answer()


@router.callback_query(F.data.startswith("genre_"))
async def select_genre(callback: types.CallbackQuery):
    _, category, genre = callback.data.split("_")

    user_context[callback.from_user.id] = {
        "category": category,
        "genre": genre,
        "dislikes": []
    }

    recs = await get_recommendations(category, genre, [])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Ещё рекомендации", callback_data="rec_dislike")],
            [InlineKeyboardButton(text="🔚 Закончить", callback_data="end_rec")]
        ]
    )

    await callback.message.answer(f"📌 Рекомендации ({category}, {genre}):\n\n{recs}", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "rec_dislike")
async def dislike(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_context:
        await callback.message.answer("⚠️ Сначала выберите категорию и жанр.")
        return

    ctx = user_context[user_id]
    ctx["dislikes"].append("последний набор рекомендаций")

    recs = await get_recommendations(ctx["category"], ctx["genre"], ctx["dislikes"])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Ещё рекомендации", callback_data="rec_dislike")],
            [InlineKeyboardButton(text="🔚 Закончить", callback_data="end_rec")]
        ]
    )

    await callback.message.answer(f"🔄 Новые рекомендации ({ctx['category']}, {ctx['genre']}):\n\n{recs}", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "end_rec")
async def end_recommendations(callback: types.CallbackQuery):
    user_context.pop(callback.from_user.id, None)
    await callback.message.answer("Возврат в главное меню", reply_markup=main_menu())
    await callback.answer()
