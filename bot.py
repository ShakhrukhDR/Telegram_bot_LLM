import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import message_router

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

async def main():
    """Основной асинхронный цикл работы бота."""
    # Получение токена из переменных окружения
    token = os.getenv("BOT_TOKEN")
    if not token:
        logging.error("Токен бота не найден! Убедитесь, что файл .env настроен корректно.")
        return

    # Создаем объект бота
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    
    # Удаляем старые вебхуки
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Вебхуки успешно удалены.")
    except Exception as e:
        logging.error(f"Ошибка удаления вебхука: {e}")

    # Создаем диспетчер
    dp = Dispatcher()
    dp.include_router(message_router.router)

    # Запуск polling
    try:
        logging.info("Запуск polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {e}")
    finally:
        await bot.session.close()
        logging.info("Сессия бота закрыта.")

if __name__ == "__main__":
    asyncio.run(main())

