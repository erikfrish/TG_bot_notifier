from datetime import datetime
from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import Message, TelegramObject, Update
from core.utils.pg_connect import is_user_registered, register_user
from core.utils.pg_connect import checking_for_new_row2


class new_task_checker(BaseMiddleware):
    def __init__(self) -> None:
        self.on_off_flag: bool = False

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ):
        if self.on_off_flag == True:
            return await handler(event, data)
        else:
            self.on_off_flag = True
            while True:
                await checking_for_new_row2()

            return await handler(event, data)
