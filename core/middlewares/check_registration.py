from datetime import datetime
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import Message, TelegramObject, Update
from core.utils.pg_connect import is_user_registered, register_user
from core.keyboards.reply import get_user_contact_keyboard


class if_not_registered(BaseMiddleware):
    def __init__(self) -> None:
        self.registered_flag: bool

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ):
        if event.text == '/start' or event.text == '/run' or event.text == '/старт':
            return await handler(event, data)
        # если юзер незарегистрирован И отправил не контакт или пустой контакт, прошу зарегистрироваться
        if (not await is_user_registered(event.from_user.id)):
            if (event.contact == None):
                await event.answer("Cначала отправь свой контакт!", reply_markup=get_user_contact_keyboard())
            elif (event.contact.user_id != event.from_user.id):
                await event.answer("😂 Хорошая попытка, но нужен именно <b>твой контакт</b>.\nCначала отправь свой контакт! 🤨 ", reply_markup=get_user_contact_keyboard())
            else:
                await register_user(event.contact.user_id, event.from_user.username, event.contact.phone_number)
                return await handler(event, data)
        # если юзер зарегистрирован, можно пропускать регистрацию и переходить к обработчику сообщения
        else:
            # await event.delete(reply_markup=ReplyKeyboardRemove())
            return await handler(event, data)
