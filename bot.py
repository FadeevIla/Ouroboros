import secrets
import asyncio
import random
import logging
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from core import environ_map

logger = logging.getLogger(__name__)
BOT_TOKEN = environ_map['TELEGRAM_BOT_TOKEN']

async def start(message: types.Message):
    await message.reply_text("Привет, я бот!")

async def help_command(message: types.Message):
    await message.reply_text('Список команд: /start, /help, /about, /status, /joke, /fact, /quote, /weather, /stats, /poll, /remind, /info, /whatsnew, /stats')

async def about(message: types.Message):
    await message.reply_text('Это бот, который может ответить на различные вопросы.')

async def status(message: types.Message):
    await message.reply_text('Бот работает!')

async def joke(message: types.Message):
    jokes = [
        'Почему компьютер шел в гимнастку? Чтобы улучшить свою скорость!',
        'Почему программист не любит воду? Потому что он боится "отплывать"!',
        'Почему компьютер не может ходить в кино? Потому что он не может купить билет!'
    ]
    await message.reply_text(random.choice(jokes))

async def fact(message: types.Message):
    facts = [
        'Солнце весит 330 000 масс-сон, что примерно в 330 000 раз больше, чем Земля.',
        'Самая большая планета в наше солнечной системы - Юпитер.',
        'Самая дальняя планета от Солнца - Плутон.'
    ]
    await message.reply_text(random.choice(facts))

async def quote(message: types.Message):
    quotes = [
        'Всегда помните, что жизнь коротка, но воспоминания о ней могут быть вечными.',
        'Никогда не сдавайтесь, потому что победа всегда впереди.',
        'Всегда следуйте своему сердцу, потому что оно знает, что правильно.'
    ]
    await message.reply_text(random.choice(quotes))

async def weather(message: types.Message):
    try:
        city = message.text.split()[1]
        api_key = environ_map['OPENWEATHERMAP_API_KEY']
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    weather_description = data['weather'][0]['description']
                    await message.reply_text(f'Погода в {city}: {weather_description}')
                else:
                    await message.reply_text('Ошибка. Проверьте город или ключ от API.')
    except Exception as e:
        logger.error(f'Ошибка при получении погоды: {e}')
        await message.reply_text('Ошибка при получении погоды.')

async def stats(message: types.Message):
    await message.reply_text('Статистика бота.')

async def poll(message: types.Message):
    await message.reply_text('Опрос бота.')

async def remind(message: types.Message):
    await message.reply_text('Напоминание бота.')

async def info(message: types.Message):
    await message.reply_text('Информация о боте.')

async def whatsnew(message: types.Message):
    await message.reply_text('Новости бота.')

async def remind_me(message: types.Message):
    try:
        # код напоминания
        await message.reply_text('Напоминание создано.')
    except Exception as e:
        logger.error(f'Ошибка при создании напоминания: {e}')
        await message.reply_text('Ошибка при создании напоминания.')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])
    dp.register_message_handler(about, commands=['about'])
    dp.register_message_handler(status, commands=['status'])
    dp.register_message_handler(joke, commands=['joke'])
    dp.register_message_handler(fact, commands=['fact'])
    dp.register_message_handler(quote, commands=['quote'])
    dp.register_message_handler(weather, commands=['weather'])
    dp.register_message_handler(stats, commands=['stats'])
    dp.register_message_handler(poll, commands=['poll'])
    dp.register_message_handler(remind, commands=['remind'])
    dp.register_message_handler(info, commands=['info'])
    dp.register_message_handler(whatsnew, commands=['whatsnew'])
    dp.register_message_handler(remind_me, commands=['remindme'])
    executor.start_polling(dp, skip_updates=True)