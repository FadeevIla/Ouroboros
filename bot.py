import secrets
import asyncio
from aiogram import Application, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Update, Message, Poll
from aiogram.filters import Command, CommandStart, CommandHelp, CommandAbout, CommandStatus, CommandJoke, CommandFact, CommandQuote, CommandWeather, CommandStats, CommandPoll, CommandRemind, CommandStats
from aiogram.utils.command import CommandSet
from aiogram.utils.command import Command

logger = logging.getLogger(__name__)
BOT_TOKEN = secrets.environ_map['TELEGRAM_BOT_TOKEN']

class Bot:
    def __init__(self):
        self.app = Application()
        self.storage = MemoryStorage()
        self.bot = Bot(token=BOT_TOKEN)
        self.command_set = CommandSet([
            CommandStart('start', run=start),
            CommandHelp('help', run=help_command),
            CommandAbout('about', run=about),
            CommandStatus('status', run=status),
            CommandJoke('joke', run=joke),
            CommandFact('fact', run=fact),
            CommandQuote('quote', run=quote),
            CommandWeather('weather', run=weather),
            CommandStats('stats', run=stats),
            CommandPoll('poll', run=poll),
            CommandRemind('remind', run=remind),
            Command('start', run=start),
            Command('help', run=help_command),
            Command('status', run=status),
            Command('about', run=about),
            Command('joke', run=joke),
            Command('fact', run=fact),
            Command('quote', run=quote),
            Command('weather', run=weather),
            Command('stats', run=stats),
            Command('poll', run=poll),
            Command('remind', run=remind),
        ])

        self.app.command_handlers.update(self.command_set.commands)
        self.app.answerers.update(self.command_set.answerers)

    async def main(self):
        if BOT_TOKEN == "твой_токен_бота":
            logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
            logger.error("   Добавь токен в secrets GitHub: Settings → Secrets → TELEGRAM_BOT_TOKEN")
            sys.exit(1)

        logger.info("🔧 Создание приложения...")
        await self.app.start()

        logger.info("✅ Бот готов к запуску!")
        logger.info("📋 Команды: /start, /help, /status, /about, /joke, /fact, /quote, /weather, /stats, /poll, /remind")

        # Запускаем поллинг
        try:
            async with self.app:
                await self.app.run_polling()
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")

async def start(update: Update):
    await update.message.reply_sticker("CAADAgAD1AoAApg0OgAe8w3xW4j7iA") # стикерпак с сообщением

async def help_command(update: Update, context: Application):
    await update.message.reply_text("Список доступных команд:\n"
                                    "/start - начать работу\n"
                                    "/help - помощь\n"
                                    "/status - описание команд\n"
                                    "/about - информация о пользователе\n"
                                    "/joke - случайный шутка\n"
                                    "/fact - рандомная информация\n"
                                    "/quote - цитата дня\n"
                                    "/weather - прогноз погоды\n"
                                    "/stats - статистика\n"
                                    "/poll - опрос\n"
                                    "/remind - напомнить")

async def about(update: Update, context: Application):
    await update.message.reply_text(f"Возраст: {update.from_user.age}\n"
                                   f"ID: {update.from_user.id}")

async def status(update: Update, context: Application):
    await update.message.reply_text("Текущая информация пользователя")

async def joke(update: Update, context: Application):
    await update.message.reply_text("Шутка. Приглашение к танцам в 2:00 ночи в пятницу")

async def fact(update: Update, context: Application):
    await update.message.reply_text("Факт о человеке. В 1955 году человек впервые ступил на луну")

async def quote(update: Update, context: Application):
    await update.message.reply_text("Цитата дня. «Деньги, так деньги, а деньги не для того, чтобы их положить под подушку».")

async def weather(update: Update, context: Application):
    await update.message.reply_text("Прогноз погоды. В городе сейчас дождь")

async def polling(update: Update, context: Application):
    await update.message.reply_text("Опрос: какие цветы вы любите?")

async def stats(update: Update, context: Application):
    await update.message.reply_text("Статистика. Пользователь находится в статистике")

async def remind(update: Update, context: Application):
    await update.message.reply_text("Напоминание. Встреча на выходных.")

if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.main())