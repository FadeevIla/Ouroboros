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

player_state = {}

async def start(message: types.Message):
    if message.chat.id not in player_state:
        player_state[message.chat.id] = {'health': 100, 'inventory': []}
    await message.reply("Привет, я бот!")

async def help_command(message: types.Message):
    await message.reply('Список команд: /start, /help, /fight, /travel')

async def fight(message: types.Message):
    player_health = player_state[message.chat.id]['health']
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

async def travel(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    epochs = ['Древний Египет', 'Средние века', 'Будущее']
    epoch = random.choice(epochs)
    await message.reply(f'Вы путешествуете в {epoch}!')
    events = ['Встреча с исторической фигурой', 'Нападение дикого зверя', 'Найденная реликвия']
    event = random.choice(events)
    if event == 'Встреча с исторической фигурой':
        await message.reply('Вы встретили знаменитую личность!')
    elif event == 'Нападение дикого зверя':
        await message.reply('На вас напал дикой зверь! Что вы делаете? 1 - атаковать, 2 - убежать')
        action = await message.reply('Выберите действие:')
        if action.text == '1':
            await message.reply('Вы победили зверя!')
        elif action.text == '2':
            await message.reply('Вы убежали!')
    elif event == 'Найденная реликвия':
        relic = random.choice(['Священный Грааль', 'Золотой идол', 'Древний свиток'])
        await message.reply(f'Вы нашли {relic}!')
        player_state[message.chat.id]['inventory'].append(relic)
        await message.reply(f'Ваш инвентарь: {player_state[message.chat.id]["inventory"]}')

dp.register_message_handler(start, commands=['start'])
dp.register_message_handler(help_command, commands=['help'])
dp.register_message_handler(fight, commands=['fight'])
dp.register_message_handler(travel, commands=['travel'])

if __name__ == '__main__':
    executor.start_polling(dp)