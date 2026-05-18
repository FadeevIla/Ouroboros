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
CHAT_ID = 123456789  

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

player_state = {}

async def start(message: types.Message):
    if message.chat.id not in player_state:
        player_state[message.chat.id] = {'health': 100, 'inventory': [], 'level': 1, 'experience': 0, 'paradox': 0}
    await message.reply("Привет, я бот!")
    await message.reply("Вы теперь можете путешествовать во времени. Нажмите /travel, чтобы начать свое приключение.")

async def help_command(message: types.Message):
    await message.reply('Список команд: /start, /help, /fight, /travel, /inventory, /level, /paradox, /quest, /trade')

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
    events = ['Встреча с исторической личностью', 'Открытие скрытой реликвии', 'Участие в историческом событии']
    event = random.choice(events)
    await message.reply(f'Вы столкнулись с {event}!')

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
    await message.reply(f'Ваша парадоксальная энергия: {player_state[message.chat.id]["paradox"]}')

async def quest(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    await message.reply('Вы получили квест!')
    player_state[message.chat.id]['inventory'].append('Квестовый предмет')
    await message.reply(f'Ваш инвентарь: {player_state[message.chat.id]["inventory"]}')

async def trade(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    await message.reply('Вы можете обменять 5 артефактов на парадоксальную энергию.')
    action = (await bot.wait_for_message(chat_id=message.chat.id, timeout=60)).text
    if action == 'обменять':
        if len(player_state[message.chat.id]['inventory']) >= 5:
            player_state[message.chat.id]['paradox'] += 1
            player_state[message.chat.id]['inventory'] = player_state[message.chat.id]['inventory'][5:]
            await message.reply(f'Ваша парадоксальная энергия: {player_state[message.chat.id]["paradox"]}')
        else:
            await message.reply('У вас недостаточно артефактов')
    else:
        await message.reply('Обмен отменен')

dp.register_message_handler(start, commands=['start'])
dp.register_message_handler(help_command, commands=['help'])
dp.register_message_handler(fight, commands=['fight'])
dp.register_message_handler(travel, commands=['travel'])
dp.register_message_handler(inventory, commands=['inventory'])
dp.register_message_handler(level, commands=['level'])
dp.register_message_handler(paradox, commands=['paradox'])
dp.register_message_handler(quest, commands=['quest'])
dp.register_message_handler(trade, commands=['trade'])

if __name__ == '__main__':
    executor.start_polling(dp)