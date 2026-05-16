import secrets
import asyncio
import random
import logging
import requests

import aiogram
from aiogram import Application, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Update, Message, Poll
from aiogram.filters import Command
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

logger = logging.getLogger(__name__)
BOT_TOKEN = secrets.environ_map['TELEGRAM_BOT_TOKEN']

async def start(update: Update, context: Application):
    await update.message.reply_text("Привет, я бот!")

async def help_command(update: Update, context: Application):
    await update.message.reply_text('Список команд: /start, /help, /about, /status, /joke, /fact, /quote, /weather, /stats, /poll, /remind, /info, /whatsnew')

async def about(update: Update, context: Application):
    await update.message.reply_text('Это бот, который может ответить на различные вопросы.')

async def status(update: Update, context: Application):
    await update.message.reply_text('Бот работает!')

async def joke(update: Update, context: Application):
    jokes = [
        'Почему компьютер шел в гимнастку? Чтобы улучшить свою скорость!',
        'Почему программист не любит воду? Потому что он боится "отплывать"!',
        'Почему компьютер не может ходить в кино? Потому что он не может купить билет!'
    ]
    await update.message.reply_text(random.choice(jokes))

async def fact(update: Update, context: Application):
    facts = [
        'Солнце весит 330 000 масс-сон, что примерно в 330 000 раз больше, чем Земля.',
        'Самая большая планета в наше солнечной системы - Юпитер.',
        'Самая дальняя планета от Солнца - Плутон.'
    ]
    await update.message.reply_text(random.choice(facts))

async def quote(update: Update, context: Application):
    quotes = [
        'Всегда помните, что жизнь коротка, но воспоминания о ней могут быть вечными.',
        'Никогда не сдавайтесь, потому что победа всегда впереди.',
        'Всегда следуйте своему сердцу, потому что оно знает, что правильно.'
    ]
    await update.message.reply_text(random.choice(quotes))

async def weather(update: Update, context: Application):
    try:
        city = update.message.text.split()[1]
        api_key = secrets.environ_map['OPENWEATHERMAP_API_KEY']
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_description = data['weather'][0]['description']
            await update.message.reply_text(f'Погода в {city}: {weather_description}')
        else:
            await update.message.reply_text('Ошибка. Проверьте город или ключ от API.')
    except Exception as e:
        logger.error(f'Ошибка при получении погоды: {e}')
        await update.message.reply_text('Ошибка. Проверьте город или ключ от API.')

async def stats(update: Update, context: Application):
    await update.message.reply_text("Статистика. Это могла бы быть любая информация о статистике.")

async def poll(update: Update, context: Application):
    await update.message.reply_text("Опрос. Это могла бы быть любая информация об опросе.")

async def remind(update: Update, context: Application):
    await update.message.reply_text("Напоминание. Встреча на выходных.")

async def info(update: Update, context: Application):
    await update.message.reply_text("Это случайное сообщение")

async def whatsnew(update: Update, context: Application):
    news = [
        'Новая функция бота: теперь можно получать стоимостные сообщения.',
        'Было исправлено несколько ошибок, теперь бот работает более стабильно.',
        'Добавлена поддержка новых языков.'
    ]
    await update.message.reply_text(random.choice(news))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.startup.register(start)
    dp.message_handler(Command("help"), help_command)
    dp.message_handler(Command("about"), about)
    dp.message_handler(Command("status"), status)
    dp.message_handler(Command("joke"), joke)
    dp.message_handler(Command("fact"), fact)
    dp.message_handler(Command("quote"), quote)
    dp.message_handler(Command("weather"), weather)
    dp.message_handler(Command("stats"), stats)
    dp.message_handler(Command("poll"), poll)
    dp.message_handler(Command("remind"), remind)
    dp.message_handler(Command("info"), info)
    dp.message_handler(Command("whatsnew"), whatsnew)
    executor.start_polling(dp, skip_updates=True)