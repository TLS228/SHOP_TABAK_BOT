import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio


# Инициализация бота, диспетчера и роутера
bot = Bot(token=os.getenv("API_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Главное меню
main_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="Табак для кальяна"), KeyboardButton(text="Сигариллы"), KeyboardButton(text="Сигары")],
        [KeyboardButton(text="Папиросы"), KeyboardButton(text="Кальяны"), KeyboardButton(text="Стики")],
        [KeyboardButton(text="Электронные сигареты")]
    ]
)

# Марки электронных сигарет
ecigs_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="HQD"), KeyboardButton(text="Juul"), KeyboardButton(text="Elf Bar")],
        [KeyboardButton(text="Назад")]
    ]
)

# Модели HQD
hqd_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="HQD Cuvie"), KeyboardButton(text="HQD King")],
        [KeyboardButton(text="Назад")]
    ]
)

# Хранилище состояний пользователя
user_state = {}

@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Добро пожаловать в магазин табачной продукции! Выберите категорию:", reply_markup=main_menu)
    user_state[message.from_user.id] = "main_menu"

@router.message(F.text == "Назад")
async def go_back(message: Message):
    current_state = user_state.get(message.from_user.id, "main_menu")

    if current_state == "ecigs_menu":
        await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)
        user_state[message.from_user.id] = "main_menu"
    elif current_state == "hqd_menu":
        await message.answer("Вы вернулись в меню электронных сигарет.", reply_markup=ecigs_menu)
        user_state[message.from_user.id] = "ecigs_menu"

@router.message(F.text == "Электронные сигареты")
async def show_ecigs_menu(message: Message):
    await message.answer("Выберите марку электронных сигарет:", reply_markup=ecigs_menu)
    user_state[message.from_user.id] = "ecigs_menu"

@router.message(F.text == "HQD")
async def show_hqd_menu(message: Message):
    await message.answer("Выберите модель HQD:", reply_markup=hqd_menu)
    user_state[message.from_user.id] = "hqd_menu"

@router.message(F.text.in_(["HQD Cuvie", "HQD King"]))
async def show_hqd_model(message: Message):
    await message.answer(f"Вы выбрали {message.text}. Чем могу помочь дальше?")

@router.message(F.text.in_(["Табак для кальяна", "Сигариллы", "Сигары", "Папиросы", "Кальяны", "Стики"]))
async def show_category(message: Message):
    await message.answer(f"Вы выбрали {message.text}. Эта категория пока не настроена.")

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
