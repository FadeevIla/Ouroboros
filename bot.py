import secrets
import asyncio
import random
import logging
import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def start(message: types.Message):
    await message.reply("Привет, я бот!")

async def help_command(message: types.Message):
    await message.reply('Список команд: /start, /help, /fight')

async def fight(message: types.Message):
    player_health = 100
    enemy_health = 100
    while player_health > 0 and enemy_health > 0:
        await message.reply(f'Ваше здоровье: {player_health}, Здоровье врага: {enemy_health}')
        action = await message.reply('Что вы хотите сделать? 1 - атаковать, 2 - защититься')
        if action.text == '1':
            enemy_health -= 20
            player_health -= 10
        elif action.text == '2':
            player_health += 10
        else:
            await message.reply('Недопустимое действие')
            break
    if player_health > 0:
        await message.reply('Вы победили!')
    else:
        await message.reply('Вы проиграли!')

dp.register_message_handler(start, commands=['start'])
dp.register_message_handler(help_command, commands=['help'])
dp.register_message_handler(fight, commands=['fight'])

if __name__ == '__main__':
    executor.start_polling(dp)