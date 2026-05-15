import secrets
import asyncio
import random
import logging
import requests

import aiogram
from aiogram import Application, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Update, Message, Poll
from aiogram.filters import Command, CommandStart, CommandHelp, CommandAbout, CommandStatus, CommandJoke, CommandFact, CommandQuote, CommandWeather, CommandStats, CommandPoll, CommandRemind, CommandInfo

logger = logging.getLogger(__name__)
BOT_TOKEN = secrets.environ_map['TELEGRAM_BOT_TOKEN']

class Bot:
    def __init__(self):
        self.app = Application()
        self.storage = MemoryStorage()
        self.bot = Bot(token=BOT_TOKEN)
        self.command_set = [
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
            CommandInfo('info', run=info),
        ]

async def start(update: Update, context: Application):
    await update.message.reply_text("Привет, я бот!")

async def help_command(update: Update, context: Application):
    await update.message.reply_text('Список команд: /start, /help, /about, /status, /joke, /fact, /quote, /weather, /stats, /poll, /remind, /info')

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
    city = update.message.text.split(' ')[1]
    api_key = 'Ваш API ключ'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        await update.message.reply_text(f'Температура в {city}: {data["main"]["temp"]}°C')
    else:
        await update.message.reply_text('Ошибка. Проверьте город или ключ от API.')

async def stats(update: Update, context: Application):
    await update.message.reply_text("Статистика: пользователей - 100")

async def poll(update: Update, context: Application):
    await update.message.reply_text("Опрос: как вы относитесь к боту?")

async def remind(update: Update, context: Application):
    await update.message.reply_text("Напоминание. Встреча на выходных.")

async def info(update: Update, context: Application):
    await update.message.reply_text("Это случайное сообщение")

if __name__ == "__main__":
    import logging
    from logging import basicConfig
    basicConfig(level=logging.INFO)
    import sys
    from aiogram import Bot, Dispatcher, executor, types
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.setup_middleware(aiogram.BackendMiddleware())
    dp.include_router(aiogram.Dispatcher(dp, storage=MemoryStorage()))
    executor.start_polling(dp, skip_updates=True)