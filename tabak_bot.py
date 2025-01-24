"""Telegram-бот для магазина табака."""

import os
import asyncio

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Инициализация бота, диспетчера и роутера
token = os.getenv("API_TOKEN")
if token is None:
    raise ValueError("API_TOKEN не установлен")
bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="Табак для кальяна"),
         KeyboardButton(text="Кальяны")],
        [KeyboardButton(text="Снюс"),
         KeyboardButton(text="Жидкости для электронных сигарет")],
        [KeyboardButton(text="Электронные сигареты")]
    ]
)

# Словари для хранения данных
categories = {
    "Табак для кальяна": ["Adalya", "Al Fakher", "Tangiers"],
    "Кальяны": ["Khalil Mamoon", "Amy", "Hoob Hookahs"],
    "Снюс": ["Siberia", "General", "Odens"],
    "Жидкости для электронных сигарет": [
        "Nasty Juice", "Dinner Lady", "Element", "Just Juice", "IVG"
    ],
    "Электронные сигареты": ["Elf Bar", "Voopoo", "Geekvape"]
}

items = {
    "Adalya": ["Виноград", "Арбуз с мятой", "Манго", "Ананас"],
    "Al Fakher": ["Апельсин", "Лимон с мятой", "Малина", "Вишня"],
    "Tangiers": ["Лавандовый чай", "Черничный пирог", "Гуава", "Персик"],
    "Khalil Mamoon": ["Mini Kamanja Oxide", "Halazone Black", "Beast Black"],
    "Amy": ["SS 20", "4-Star 460", "Deluxe 053"],
    "Hoob Hookahs": ["Enzo", "Cyber", "subAtom"],
    "Siberia": ["Мята", "Лесные ягоды", "Ледяной кофе", "Сливочная ваниль"],
    "General": ["Цитрус", "Эвкалипт", "Зимние специи", "Сладкая лакрица"],
    "Odens": ["Ментол", "Дыня", "Вишневый лед", "Тропический коктейль"],
    "Nasty Juice": [
        "Кислый яблочный сорбет", "Манго с холодком",
        "Малина-лимон", "Дыня со льдом"
    ],
    "Dinner Lady": [
        "Лимонный пирог", "Клубничный йогурт",
        "Ванильный крем", "Черничный тарт"
    ],
    "Element": [
        "Малиновый морс", "Апельсиновый микс",
        "Жвачка", "Тропический пунш"
    ],
    "Just Juice": [
        "Личи-гуава", "Персиковый чай", "Ледяная маракуйя", "Виноградный микс"
    ],
    "IVG": [
        "Энергетический коктейль", "Лесные ягоды",
        "Арбузное мороженое", "Клубничный лед"
    ],
    "Elf Bar": ["BC5000", "600 Lux", "CR500"],
    "Voopoo": ["Drag X", "Argus P1", "Vinci Pod"],
    "Geekvape": ["Aegis Legend 2", "Wenax H1", "Obelisk 65"]
}

# Кнопки
back_button = KeyboardButton(text="Назад")
order_button = KeyboardButton(text="Оформить заказ")
absent_button = KeyboardButton(text="Отсутствует")

# Хранилище состояний пользователя
user_state = {}


@router.message(Command("start"))
async def start_command(message: Message):
    """Обработка команды /start и отображение главного меню."""
    await message.answer(
        "Добро пожаловать в магазин 'BlackSmoke'! Выберите категорию товаров:",
        reply_markup=main_menu
    )
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID пользователя.")
        return
    user_state[user_id] = {"state": "main_menu"}


@router.message(F.text == "Назад")
async def go_back(message: Message):
    """Обработка нажатия кнопки 'Назад' и возврат в предыдущее меню."""
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID пользователя.")
        return
    current_state = user_state.get(user_id, {}).get("state", "main_menu")

    if current_state == "confirm_order":
        brand = user_state[user_id]["brand"]
        items_keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text=item) for item in items[brand]],
                [back_button, absent_button]
            ]
        )
        await message.answer(
            f"Вы вернулись в меню выбора модели или вкуса для '{brand}'.",
            reply_markup=items_keyboard
        )
        user_state[user_id]["state"] = "select_brand"
    elif current_state == "select_brand":
        category = user_state[user_id]["category"]
        brands_keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text=brand) for brand in categories[category]],
                [back_button]
            ]
        )
        await message.answer(
            f"Вы вернулись в меню категории '{category}'.",
            reply_markup=brands_keyboard
        )
        user_state[user_id]["state"] = "select_category"
    elif current_state == "select_category":
        await message.answer(
            "Вы вернулись в главное меню.",
            reply_markup=main_menu
        )
        user_state[user_id] = {"state": "main_menu"}


@router.message(F.text.in_(categories.keys()))
async def show_brands(message: Message):
    """Отображение доступных брендов для выбранной категории."""
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID пользователя.")
        return
    category = message.text
    user_state[user_id] = {"state": "select_category",
                           "category": category if category else ""}
    brands_keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text=brand) for brand in categories[category]],
            [back_button]
        ]
    )
    await message.answer(
        f"Вы выбрали категорию '{category}'. Выберите производителя:",
        reply_markup=brands_keyboard
    )


@router.message(
    F.text.in_([brand for sublist in categories.values() for brand in sublist])
)
async def show_items(message: Message):
    """Отображение доступных товаров для выбранного бренда."""
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID пользователя.")
        return
    user = user_state.get(user_id)
    if user:
        category = user.get("category")
        brand = message.text
        if category:
            user_state[user_id].update(
                {"state": "select_brand", "brand": brand if brand else ""}
            )
            items_keyboard = ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [KeyboardButton(text=item) for item in items[brand]],
                    [back_button, absent_button]
                ]
            )
            await message.answer(
                f"Вы выбрали производителя '{brand}'. "
                f"Выберите модель или вкус:",
                reply_markup=items_keyboard
            )
        else:
            await message.answer(
                "Произошла ошибка. Пожалуйста, выберите категорию заново.",
                reply_markup=main_menu
            )
            user_state[user_id] = {"state": "main_menu"}
    else:
        await message.answer(
            "Произошла ошибка. Пожалуйста, начните сначала.",
            reply_markup=main_menu
        )
        user_state[user_id] = {"state": "main_menu"}


@router.message(
    F.text.in_(
        [item for sublist in items.values() for item in sublist]
    )
)
async def confirm_order(message: Message):
    """Подтверждение выбранного товара и запрос на оформление заказа."""
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID пользователя.")
        return
    user = user_state.get(user_id)
    if user:
        brand = user.get("brand")
        item = message.text
        if brand:
            user_state[user_id].update(
                {"state": "confirm_order", "item": item if item else ""}
            )
            order_keyboard = ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[[order_button], [back_button]]
            )
            await message.answer(
                f"Вы выбрали '{item}'."
                f" Нажмите 'Оформить заказ' для подтверждения.",
                reply_markup=order_keyboard
            )
        else:
            await message.answer(
                "Произошла ошибка. Пожалуйста, выберите производителя заново.",
                reply_markup=main_menu
            )
            user_state[user_id] = {"state": "main_menu"}
    else:
        await message.answer(
            "Произошла ошибка. Пожалуйста, начните сначала.",
            reply_markup=main_menu
        )
        user_state[user_id] = {"state": "main_menu"}


@router.message(F.text == "Оформить заказ")
async def order_item(message: Message):
    """Оформление заказа и отправка его владельцу магазина."""
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID пользователя.")
        return
    user = user_state.get(user_id)
    if user and "category" in user and "brand" in user and "item" in user:
        category = user["category"]
        brand = user["brand"]
        item = user["item"]
        order_details = (
            (
                f"Заказ:\n"
                f"Категория: {category}\n"
                f"Производитель: {brand}\n"
                f"Модель/Вкус: {item}"
            )
        )
        owner_chat_id = os.getenv('OWNER_CHAT_ID')
        if owner_chat_id is None:
            await message.answer(
                "Произошла ошибка: не удалось получить ID владельца.")
            return
        await bot.send_message(chat_id=owner_chat_id, text=order_details)
        await message.answer(
            "Ваш заказ оформлен и отправлен владельцу магазина.",
            reply_markup=main_menu
        )
        user_state[user_id] = {"state": "main_menu"}
    else:
        await message.answer(
            "Пожалуйста, выберите категорию и производителя товара перед "
            "оформлением заказа.",
            reply_markup=main_menu
        )
        user_state[user_id] = {"state": "main_menu"}


@router.message(F.text == "Отсутствует")
async def item_absent(message: Message):
    """Обработка нажатия кнопки 'Отсутствует' и запрос на уточнение товара."""
    await message.answer("Пожалуйста, напишите, какой товар вам нужен:")
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID пользователя.")
        return
    user_state[user_id] = user_state.get(user_id, {})
    user_state[user_id]["state"] = "custom_request"


@router.message(
    lambda message: user_state.get(
        message.from_user.id, {}).get("state") == "custom_request"
        )
async def handle_custom_request(message: Message, bot: Bot):
    """Обработка пользовательского запроса на отсутствующий товар."""
    owner_chat_id = os.getenv('OWNER_CHAT_ID')
    if owner_chat_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID владельца.")
        return
    await bot.send_message(
        chat_id=owner_chat_id,
        text=f"Запрос на товар: {message.text}"
    )
    await message.answer("Ваш запрос отправлен владельцу магазина.")
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer(
            "Произошла ошибка: не удалось получить ID пользователя.")
        return
    user_state[user_id] = {"state": "main_menu"}


async def main():
    """Основная точка входа для запуска бота."""
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
