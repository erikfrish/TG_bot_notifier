import logging
import configparser
import time
from aiogram import Bot, Dispatcher, types
import asyncio
from core.utils.pg_connect import is_user_registered


import json

from core.keyboards.reply import reply_keyboard, loc_tel_poll_keyboard, get_reply_keyboard, get_user_contact_keyboard
# from core.utils.pg_connect import is_user_registered

# config = configparser.ConfigParser()  # создаём объекта парсера conf.ini
# config.read("tg_bot/conf.ini")  # читаем конфиг conf.ini
# API_TOKEN = config['Conf']['API_TOKEN']
# REGULAR_TEXT = config['Conf']['REGULAR_TEXT']
# NOTIFICATION_TEXT = config['Conf']['NOTIFICATION_TEXT']
# HELP_COMMAND = config['Conf']['HELP_COMMAND']

# FIXME перекинуть текст в .env, сделать более содержательным
HELP_COMMAND = """Привет дорогой пользователь!
Я существую, чтобы иногда сообщать тебе о чем-нибудь довольно оперативно, так что не отключай уведомления 😉

Если что, я умею только это, так что крайне интересной беседы, увы, не получится. 
Впрочем, я люблю стикеры, так что самые отбитые можешь присылать😉

Вот мои команды:
/start  -- первое что ты мне напишешь
/help -- расскажу кто я и что умею
/пока это все, но может что еще добавлю
"""


async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_name = message.from_user.first_name
    text = message.text
    logging.info(
        f'{user_id=} {user_full_name=} {time.asctime()} {user_name} {text}')
    print(f'{user_id=} {user_full_name=} {time.asctime()} {user_name} {text}')
    await asyncio.sleep(10)

    # with open("/Users/mac/Developer/GitHub/Project_Diplom/tg_bot/message.json", "w") as o:
    #     o.write(json.dumps(message.dict(), default=str))
    if (not await is_user_registered(message.from_user.id)):
        await message.answer(f"Добрый день, {user_full_name}!\n\nДавайте с вами зарегистрируемся, пришлите свой контакт с помощью кнопки снизу ↓\n\n(нажимая на эту кнопку вы даете согласие на обработку ваших персональных данных)", reply_markup=get_user_contact_keyboard())
        await message.delete()
    else:
        await message.answer(f"{user_full_name}, вы уже зарегистрированы, теперь ожидайте уведомлений \nЕсли нужна справка, используйте команду /help")
        await message.delete()


async def help_handler(message: types.Message, bot: Bot):
    await message.reply(HELP_COMMAND)
    await message.delete()


async def sticker_echo_handler(message: types.sticker, bot: Bot):
    # print("sticker_echo_handler")
    await bot.send_sticker(message.from_user.id, message.sticker.file_id)


async def echo_handler(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    text = message.text
    await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
    print(f'{user_id=} {user_full_name=} {time.asctime()} {text=}')


async def edited_message_handler(message: types.Message, bot: Bot):
    await message.answer("Нельзя редактировать сообщения, это сбивает!")
    await message.delete()
