from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Bot
import json


async def got_true_contact(message: Message, bot: Bot, phone: str):
    await message.answer(f'Ты отправил <b>свой</b> контакт {phone}.', parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
    # with open("/Users/mac/Developer/GitHub/Project_Diplom/tg_bot/my_contact_message.json", "w") as o:
    #     o.write(json.dumps(message.dict(), default=str))


async def got_fake_contact(message: Message, bot: Bot):
    await message.answer('Ты отправил <b>не свой</b> контакт.\nНо какая уже разница, просто жди сообщений', parse_mode='HTML')
