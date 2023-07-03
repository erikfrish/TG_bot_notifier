# FIXME пока что это шлак


import asyncio
from aiogram import types, Dispatcher 
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.handler import CancelHandler, current_handler

from typing import Callable, Awaitable, Dict, Any
from psycopg_pool import AsyncConnectionPool

from aiogram.types import TelegramObject
# from core.utils.dbconnect import Request

from aiogram import BaseMiddleware
from aiogram.middlewares import exceptions


_PREFIXES = ['error: ', '[error]: ', 'bad request: ', 'conflict: ', 'not found: ']


def _clean_message(text):
    for prefix in _PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):]
    return (text[0].upper() + text[1:]).strip()


class TelegramAPIError(Exception):
    def __init__(self, message=None):
        super(TelegramAPIError, self).__init__(_clean_message(message))
        
class Throttled(TelegramAPIError):
    def __init__(self, **kwargs):
        from ..dispatcher.storage import DELTA, EXCEEDED_COUNT, KEY, LAST_CALL, RATE_LIMIT, RESULT
        self.key = kwargs.pop(KEY, '<None>')
        self.called_at = kwargs.pop(LAST_CALL, time.time())
        self.rate = kwargs.pop(RATE_LIMIT, None)
        self.result = kwargs.pop(RESULT, False)
        self.exceeded_count = kwargs.pop(EXCEEDED_COUNT, 0)
        self.delta = kwargs.pop(DELTA, 0)
        self.user = kwargs.pop('user', None)
        self.chat = kwargs.pop('chat', None)




def rate_limit():
    # TODO document why this method is empty
    pass
 
 
class ThrottlingMiddleware (BaseMiddleware):
    def __init__(self, limit: int = 5):
        BaseMiddleware.__init__(self)
        self.rate_limit = limit

    async def on_process_message (self, msg: types.Message, data: dict):
        # handler = current handler.get ()
        dp = Dispatcher.get_current()
        
        try:
            await dp.throttle (key='antiflood_message', rate=self.rate_limit)
        except Throttled as _t:
            await self.msg_throttle(msg, _t)
            raise CancelHandler()
        
    async def msg_throttle(self, msg: types.Message, throttled: Throttled):
        delta = throttled. rate - throttled.delta
        if throttled. exceeded_count <= 3:
            await msg. reply( 'слыш остынь мэн')
        await asyncio.sleep(delta)