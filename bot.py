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
        player_state[message.chat.id] = {'health': 100, 'inventory': [], 'level': 1, 'experience': 0, 'paradox': 0}
    await message.reply("Привет, я бот!")

async def help_command(message: types.Message):
    await message.reply('Список команд: /start, /help, /fight, /travel, /inventory, /level, /paradox')

async def fight(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    player_health = player_state[message.chat.id]['health']
    enemy_health = 100
    while player_health > 0 and enemy_health > 0:
        await message.reply(f'Ваше здоровье: {player_health}, Здоровье врага: {enemy_health}')
        await message.reply('Что вы хотите сделать? 1 - атаковать, 2 - защититься')
        action = (await bot.wait_for_message(chat_id=message.chat.id, timeout=60)).text
        if action == '1':
            enemy_health -= 20
            player_health -= 10
        elif action == '2':
            player_health += 10
        else:
            await message.reply('Недопустимое действие')
            break
    if player_health > 0:
        await message.reply('Вы победили!')
        player_state[message.chat.id]['experience'] += 100
        if player_state[message.chat.id]['experience'] >= 1000:
            player_state[message.chat.id]['level'] += 1
            player_state[message.chat.id]['experience'] = 0
            await message.reply(f'Вы повысили уровень до {player_state[message.chat.id]["level"]}')
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
        action = (await bot.wait_for_message(chat_id=message.chat.id, timeout=60)).text
        if action == '1':
            await message.reply('Вы победили зверя!')
        elif action == '2':
            await message.reply('Вы убежали!')
    elif event == 'Найденная реликвия':
        await message.reply('Вы нашли реликвию!')
        player_state[message.chat.id]['inventory'].append('Реликвия')

async def inventory(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    await message.reply(f'Ваш инвентарь: {player_state[message.chat.id]["inventory"]}')

async def level(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    await message.reply(f'Ваш уровень: {player_state[message.chat.id]["level"]}')

async def paradox(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    player_state[message.chat.id]['paradox'] += 1
    await message.reply('Вы создали парадокс!')
    if player_state[message.chat.id]['paradox'] > 5:
        await message.reply('Парадокс привел к непредвиденным последствиям!')
        player_state[message.chat.id]['health'] -= 20
        await message.reply(f'Ваше здоровье: {player_state[message.chat.id]["health"]}')

dp.register_message_handler(start, commands=['start'])
dp.register_message_handler(help_command, commands=['help'])
dp.register_message_handler(fight, commands=['fight'])
dp.register_message_handler(travel, commands=['travel'])
dp.register_message_handler(inventory, commands=['inventory'])
dp.register_message_handler(level, commands=['level'])
dp.register_message_handler(paradox, commands=['paradox'])

if __name__ == '__main__':
    executor.start_polling(dp)