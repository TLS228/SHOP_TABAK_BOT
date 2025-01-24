"""Модуль для тестирования телеграм-бота tabak_bot.py."""

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from unittest.mock import AsyncMock, patch
import asyncio

from tabak_bot import (
    main_menu,
    categories,
    items,
    back_button,
    order_button,
    absent_button,
    user_state,
    start_command,
    show_brands,
    show_items,
    confirm_order,
    order_item,
    item_absent,
    handle_custom_request,
    go_back,
)


@pytest.fixture
def mock_bot():
    """Фикстура для создания мока объекта Bot."""
    return AsyncMock(spec=Bot)


@pytest.fixture
def mock_dp(mock_bot):
    """Фикстура для создания мока объекта Dispatcher."""
    return Dispatcher(storage=MemoryStorage(), bot=mock_bot)


@pytest.fixture
def event_loop():
    """Фикстура для создания и управления event loop."""
    loop = asyncio.new_event_loop()  # Создаем новый event loop
    yield loop
    loop.close()  # Закрываем event loop после завершения теста


@pytest.mark.asyncio
async def test_start_command(mock_bot):
    """Тест для команды /start."""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.text = "/start"
    message.answer = AsyncMock()  # Настраиваем answer как асинхронный метод

    await start_command(message)

    message.answer.assert_called_once_with(
        "Добро пожаловать в магазин 'BlackSmoke'! Выберите категорию товаров:",
        reply_markup=main_menu,
    )
    assert user_state[123] == {"state": "main_menu"}


@pytest.mark.asyncio
async def test_show_brands(mock_bot):
    """Тест для отображения брендов."""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.text = "Табак для кальяна"
    message.answer = AsyncMock()  # Настраиваем answer как асинхронный метод

    await show_brands(message)

    message.answer.assert_called_once_with(
        "Вы выбрали категорию 'Табак для кальяна'. Выберите производителя:",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text=brand) for brand in categories["Табак для кальяна"]],
                [back_button],
            ],
        ),
    )
    assert user_state[123] == {"state": "select_category", "category": "Табак для кальяна"}


@pytest.mark.asyncio
async def test_show_items(mock_bot):
    """Тест для отображения товаров."""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.text = "Adalya"
    message.answer = AsyncMock()  # Настраиваем answer как асинхронный метод
    user_state[123] = {"state": "select_category", "category": "Табак для кальяна"}

    await show_items(message)

    message.answer.assert_called_once_with(
        "Вы выбрали производителя 'Adalya'. Выберите модель или вкус:",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text=item) for item in items["Adalya"]],
                [back_button, absent_button],
            ],
        ),
    )
    assert user_state[123] == {
        "state": "select_brand",
        "brand": "Adalya",
        "category": "Табак для кальяна",
    }


@pytest.mark.asyncio
async def test_confirm_order(mock_bot):
    """Тест для подтверждения заказа."""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.text = "Виноград"
    message.answer = AsyncMock()  # Настраиваем answer как асинхронный метод
    user_state[123] = {"state": "select_brand", "brand": "Adalya", "category": "Табак для кальяна"}

    await confirm_order(message)

    message.answer.assert_called_once_with(
        "Вы выбрали 'Виноград'. Нажмите 'Оформить заказ' для подтверждения.",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[[order_button], [back_button]],
        ),
    )
    assert user_state[123] == {
        "state": "confirm_order",
        "item": "Виноград",
        "brand": "Adalya",
        "category": "Табак для кальяна",
    }


@pytest.mark.asyncio
async def test_order_item(mock_bot):
    """Тест для оформления заказа."""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.text = "Оформить заказ"
    message.answer = AsyncMock()  # Настраиваем answer как асинхронный метод
    user_state[123] = {
        "state": "confirm_order",
        "item": "Виноград",
        "brand": "Adalya",
        "category": "Табак для кальяна",
    }

    await order_item(message)

    message.answer.assert_called_once_with(
        "Ваш заказ оформлен и отправлен владельцу магазина.",
        reply_markup=main_menu,
    )
    assert user_state[123] == {"state": "main_menu"}


@pytest.mark.asyncio
async def test_item_absent(mock_bot):
    """Тест для обработки отсутствующего товара."""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.text = "Отсутствует"
    message.answer = AsyncMock()  # Настраиваем answer как асинхронный метод
    user_state[123] = {"state": "select_brand", "brand": "Adalya", "category": "Табак для кальяна"}

    await item_absent(message)

    message.answer.assert_called_once_with(
        "Пожалуйста, напишите, какой товар вам нужен:",
    )
    assert user_state[123] == {
        "state": "custom_request",
        "brand": "Adalya",
        "category": "Табак для кальяна",
    }


@pytest.mark.asyncio
async def test_handle_custom_request(mock_bot):
    """Тест для обработки пользовательского запроса."""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.text = "Новый товар"
    message.answer = AsyncMock()  # Настраиваем answer как асинхронный метод
    user_state[123] = {"state": "custom_request"}

    # Мокируем bot.send_message
    mock_bot.send_message = AsyncMock()

    # Замокаем os.getenv, чтобы вернуть фиктивный OWNER_CHAT_ID
    with patch("os.getenv", return_value="12345"):
        await handle_custom_request(message, bot=mock_bot)  # Передаем mock_bot в функцию

    # Проверяем, что bot.send_message был вызван с правильными аргументами
    mock_bot.send_message.assert_called_once_with(
        chat_id="12345",
        text="Запрос на товар: Новый товар",
    )

    # Проверяем, что message.answer был вызван
    message.answer.assert_called_once_with(
        "Ваш запрос отправлен владельцу магазина.",
    )

    # Проверяем, что состояние пользователя обновилось
    assert user_state[123] == {"state": "main_menu"}


@pytest.mark.asyncio
async def test_go_back(mock_bot):
    """Тест для возврата в предыдущее меню."""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock()
    message.from_user.id = 123
    message.text = "Назад"
    message.answer = AsyncMock()  # Настраиваем answer как асинхронный метод
    user_state[123] = {
        "state": "confirm_order",
        "brand": "Adalya",
        "category": "Табак для кальяна",
    }

    await go_back(message)

    message.answer.assert_called_once_with(
        "Вы вернулись в меню выбора модели или вкуса для 'Adalya'.",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [KeyboardButton(text=item) for item in items["Adalya"]],
                [back_button, absent_button],
            ],
        ),
    )
    assert user_state[123] == {
        "state": "select_brand",
        "brand": "Adalya",
        "category": "Табак для кальяна",
    }
