from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from openai import AsyncOpenAI
from config import OPENAI_TOKEN
from keyboards.inline import main_menu

router = Router()
client = AsyncOpenAI(api_key=OPENAI_TOKEN)

translator_state = {}


LANGUAGES = {
    "en": "Английский",
    "de": "Немецкий",
    "zh": "Китайский",
    "ru": "Русский"
}


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"lang_{code}")]
            for code, name in LANGUAGES.items()
        ] + [[InlineKeyboardButton(text="🔚 Закончить", callback_data="end_translator")]]
    )


def translator_keyboard(current_lang: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🌍 Сменить язык (сейчас: {LANGUAGES.get(current_lang, '❓')})", callback_data="change_lang")],
            [InlineKeyboardButton(text="🔚 Закончить", callback_data="end_translator")]
        ]
    )


@router.message(Command("translator"))
@router.callback_query(F.data == "translator_menu")
async def start_translator(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    translator_state[user_id] = {"language": None}

    if isinstance(event, types.Message):
        await event.answer("Выберите язык для перевода:", reply_markup=language_keyboard())
    else:
        await event.message.answer("Выберите язык для перевода:", reply_markup=language_keyboard())
        await event.answer()


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang_code = callback.data.split("_", 1)[1]
    translator_state[user_id]["language"] = lang_code

    await callback.message.answer(
        f"✅ Язык перевода установлен: {LANGUAGES[lang_code]}\n\nОтправьте текст для перевода:",
        reply_markup=translator_keyboard(lang_code)
    )
    await callback.answer()


@router.callback_query(F.data == "change_lang")
async def change_language(callback: types.CallbackQuery):
    await callback.message.answer("Выберите новый язык:", reply_markup=language_keyboard())
    await callback.answer()



@router.message(F.text)
async def translate_text(message: types.Message):
    user_id = message.from_user.id

    # Если переводчик не активен → выходим
    if user_id not in translator_state or not translator_state[user_id].get("language"):
        return

    lang = translator_state[user_id]["language"]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Ты переводчик. Переводи все сообщения строго на {LANGUAGES[lang]} язык."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )

        translation = response.choices[0].message.content.strip()
    except Exception as e:
        translation = f"⚠️ Ошибка перевода: {e}"

    await message.answer(translation, reply_markup=translator_keyboard(lang))



@router.callback_query(F.data == "end_translator")
async def end_translator(callback: types.CallbackQuery):
    translator_state.pop(callback.from_user.id, None)
    await callback.message.answer("Переводчик завершён 👋", reply_markup=main_menu())
    await callback.answer()
