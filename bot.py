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

async def help_command(message: types.Message):
    await message.reply('Список команд: /start, /help, /fight, /travel, /inventory, /level, /paradox, /quest, /trade, /report')

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
    player_state[message.chat.id]['paradox'] += 1
    await message.reply(f'У вас {player_state[message.chat.id]["paradox"]} парадоксов!')

async def quest(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    quests = ['Исправление временной аномалии', 'Поиск реликвии']
    quest = random.choice(quests)
    await message.reply(f'Вы получили задание: {quest}!')
    await message.reply('Что вы хотите сделать? 1 - принять задание, 2 - отказаться')
    action = (await bot.wait_for_message(chat_id=message.chat.id, timeout=60)).text
    if action == '1':
        await message.reply('Вы приняли задание!')
        player_state[message.chat.id]['experience'] += 100
    elif action == '2':
        await message.reply('Вы отказались от задания!')

async def trade(message: types.Message):
    if message.chat.id not in player_state:
        await message.reply('Вы не начали приключение. Нажмите /start, чтобы начать.')
        return
    relicts = ['Реликвия 1', 'Реликвия 2', 'Реликвия 3']
    relict = random.choice(relicts)
    await message.reply(f'Вам предлагают купить {relict}!')
    await message.reply('Что вы хотите сделать? 1 - купить, 2 - отказаться')
    action = (await bot.wait_for_message(chat_id=message.chat.id, timeout=60)).text
    if action == '1':
        if player_state[message.chat.id]['experience'] >= 100:
            player_state[message.chat.id]['experience'] -= 100
            player_state[message.chat.id]['inventory'].append(relict)
            await message.reply(f'Вы купили {relict}!')
        else:
            await message.reply('У вас недостаточно опыта для покупки реликвии!')
    elif action == '2':
        await message.reply('Вы отказались от предложения!')

async def report(message: types.Message):
    if message.chat.id == CHAT_ID:
        await message.reply('Введите ваш отчет:')
        report_text = (await bot.wait_for_message(chat_id=message.chat.id, timeout=60)).text
        # сохранить отчет
        with open('report.txt', 'a') as f:
            f.write(report_text + '\n')
        await message.reply('Ваш отчет принят!')
    else:
        await message.reply('Вы не имеете права отправлять отчеты!')

dp.register_message_handler(start, commands=['start'])
dp.register_message_handler(help_command, commands=['help'])
dp.register_message_handler(fight, commands=['fight'])
dp.register_message_handler(travel, commands=['travel'])
dp.register_message_handler(inventory, commands=['inventory'])
dp.register_message_handler(level, commands=['level'])
dp.register_message_handler(paradox, commands=['paradox'])
dp.register_message_handler(quest, commands=['quest'])
dp.register_message_handler(trade, commands=['trade'])
dp.register_message_handler(report, commands=['report'])

if __name__ == '__main__':
    executor.start_polling(dp)