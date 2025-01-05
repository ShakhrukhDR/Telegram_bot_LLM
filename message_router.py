import requests
from aiogram import Router
from aiogram.types import Message
from html import escape
import logging

# Создаем роутер
router = Router()

# URL локального сервера модели
MODEL_SERVER_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Флаг для отслеживания первого сообщения от пользователя
user_states = {}

@router.message()
async def handle_message(message: Message):
    """Обработчик всех сообщений от пользователя."""
    user_id = message.from_user.id

    # Если пользователь впервые обращается к боту
    if user_id not in user_states:
        user_states[user_id] = {"greeted": True}
        await message.answer("Привет! Что тебя интересует?")
        return

    try:
        # Отправляем запрос к локальной модели
        logging.info(f"Отправка запроса к модели: {message.text}")
        response = requests.post(
            MODEL_SERVER_URL,
            json={
                "model": "hermes-3-llama-3.2-3b:2",
                "messages": [{"role": "user", "content": message.text}]
            },
            timeout=10  # Таймаут для запроса
        )

        # Проверяем статус ответа
        if response.status_code == 200:
            data = response.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Нет ответа")
            
            # Экранируем текст, чтобы избежать ошибок с тегами
            escaped_reply = escape(reply)
            await message.answer(escaped_reply, parse_mode="HTML")
        else:
            logging.error(f"Ошибка модели: {response.status_code}, {response.text}")
            await message.answer(f"Ошибка модели: {response.status_code}")
    except requests.exceptions.Timeout:
        logging.error("Истек таймаут подключения к модели.")
        await message.answer("Сервер модели временно недоступен. Попробуйте позже.")
    except Exception as e:
        # Обработка других ошибок
        logging.error(f"Произошла ошибка при обработке сообщения: {e}")
        await message.answer(f"Произошла ошибка: {str(e)}")
