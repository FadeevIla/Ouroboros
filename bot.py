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
from telegram.ext import Application, CommandHandler, ContextTypes

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
    user = update.effective_user
    welcome_text = (
        f"🦎 Привет, {user.first_name}!\n\n"
        f"Я — <b>Дарвин</b>, бот, который сам себя улучшает.\n\n"
        f"Каждые несколько часов я анализирую свой код, "
        f"ищу баги и добавляю новые функции. Без участия человека.\n\n"
        f"Доступные команды:\n"
        f"/start — это сообщение\n"
        f"/help — помощь\n"
        f"/status — текущий статус эволюции\n"
        f"/about — о проекте\n\n"
        f"Следи за моей эволюцией: возможно, в следующем цикле "
        f"у меня появится что-то новое! 🧬"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")
    logger.info(f"Пользователь {user.id} запустил бота")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка по командам."""
    help_text = (
        "🦎 <b>Дарвин — самоэволюционирующий бот</b>\n\n"
        "Я автоматически улучшаю свой код каждые несколько часов.\n"
        "Новые команды появляются сами собой!\n\n"
        "<b>Текущие команды:</b>\n"
        "/start — Приветствие\n"
        "/help — Эта справка\n"
        "/status — Статус эволюции\n"
        "/about — О проекте\n\n"
        "<i>Остальные команды... появятся позже. Наверное.</i> 🧬"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус эволюции."""
    # Пробуем прочитать файл памяти
    memory_file = config.get("MEMORY_FILE", "feature_memory.json")
    try:
        import json
        with open(memory_file, "r", encoding="utf-8") as f:
            memory = json.load(f)
        features_count = len(memory.get("features", []))
        commits_count = len(memory.get("commit_history", []))
    except (FileNotFoundError, json.JSONDecodeError):
        features_count = 0
        commits_count = 0

    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    status_text = (
        f"🧬 <b>Статус эволюции Дарвина</b>\n\n"
        f"🕐 Текущее время: {current_time}\n"
        f"🧠 Фич в памяти: <b>{features_count}</b>\n"
        f"📝 Всего коммитов: <b>{commits_count}</b>\n"
        f"📄 Файл бота: <code>{config.get('BOT_FILE_PATH', 'bot.py')}</code>\n"
        f"⏱️ Цикл эволюции: каждые {config.get('CYCLE_INTERVAL', 3600) // 60} мин\n\n"
        f"<i>Следующая мутация может произойти в любой момент...</i> 🦎"
    )
    await update.message.reply_text(status_text, parse_mode="HTML")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о проекте."""
    about_text = (
        "🦎 <b>Дарвин (Darwin Bot)</b>\n\n"
        "Самоэволюционирующий телеграм-бот.\n"
        "Каждые несколько часов он анализирует свой исходный код, "
        "ищет баги и добавляет новые функции с помощью нейросети.\n\n"
        "<b>Как это работает:</b>\n"
        "1. Бот загружает свой код из GitHub\n"
        "2. LLM (Groq) анализирует код на баги\n"
        "3. Если находит — исправляет и пушит\n"
        "4. LLM генерирует новую фичу\n"
        "5. Валидатор проверяет код\n"
        "6. Если всё чисто — пушит новую версию\n\n"
        "<b>Ядро защищено:</b> нейросеть редактирует только этот файл.\n"
        "Модули валидации, памяти и GitHub-операций недоступны для LLM.\n\n"
        "<i>Эволюция в действии. Без Скайнета.</i> 🧬"
    )
    await update.message.reply_text(about_text, parse_mode="HTML")


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
    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("about", about))

    logger.info("✅ Бот готов к запуску!")
    logger.info("📋 Команды: /start, /help, /status, /about")

    # Запускаем поллинг
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()