# bot.py — Стартовый код для Дарвина
"""
Минимальный телеграм-бот. Этот файл редактируется нейросетью.
"""
import os
import sys
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

# 🔧 Автозагрузка .env файла
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # На GitHub Actions переменные приходят из secrets

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent))

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Импорты из защищённого ядра
from core.config import load_config
from core.logger import setup_logging

# ============================================================
# НАСТРОЙКА
# ============================================================

# Загружаем конфиг
config = load_config()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "твой_токен_бота")

# Настраиваем логирование
logger, _ = setup_logging()
logger.info("🚀 Запуск Darwin Telegram Bot")


# ============================================================
# КОМАНДЫ БОТА
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение."""
    try:
        user = update.effective_user
        welcome_text = (
            f"🦎 Привет, {user.first_name}!\n\n"
            f"Я — <b>Дарвин</b>, бот, который сам "
            f"обучается и улучшается каждый день.\n\n"
            f"Мои команды:\n"
            f"/start - начать общение\n"
            f"/help - помощь\n"
            f"/status - статус бота\n"
            f"/about - информация о боте\n"
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь."""
    try:
        help_text = (
            f"🤔 Помощь:\n"
            f"/start - начать общение\n"
            f"/help - помощь\n"
            f"/status - статус бота\n"
            f"/about - информация о боте\n"
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)
    except Exception as e:
        logger.error(f"Ошибка в команде /help: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус бота."""
    try:
        status_text = (
            f"📊 Статус бота:\n"
            f"Он работает и готов к общению!"
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=status_text)
    except Exception as e:
        logger.error(f"Ошибка в команде /status: {e}")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о боте."""
    try:
        about_text = (
            f"🤖 Информация о боте:\n"
            f"Я — <b>Дарвин</b>, бот, который сам "
            f"обучается и улучшается каждый день.\n\n"
            f"Мои команды:\n"
            f"/start - начать общение\n"
            f"/help - помощь\n"
            f"/status - статус бота\n"
            f"/about - информация о боте\n"
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=about_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в команде /about: {e}")

# ============================================================
# ЗАПУСК БОТА
# ============================================================

def main():
    """Точка входа."""
    if BOT_TOKEN == "твой_токен_бота":
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        logger.error("   Добавь токен в secrets GitHub: Settings → Secrets → TELEGRAM_BOT_TOKEN")
        sys.exit(1)

    logger.info("🔧 Создание приложения...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("about", about))

    logger.info("✅ Бот готов к запуску!")
    logger.info("📋 Команды: /start, /help, /status, /about")

    # Запускаем поллинг
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main()