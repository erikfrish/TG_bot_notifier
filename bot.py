import logging
# import time
from sys import exit
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import ContentType
from aiogram import F

from core.conf import conf
import core.handlers.message_handlers as message_handlers
from core.handlers.contact import got_true_contact, got_fake_contact
from core.utils.pg_connect import checking_for_new_row
from core.filters.istruecontact import IsTrueContact
from core.utils.commands import set_commands
from core.middlewares import check_registration  # , new_task_checker


async def on_startup(bot: Bot):
    print("запуск бота")
    # await bot.send_message(settings.bots.admin_id, text="Бот запущен!")
    await set_commands(bot)


async def on_shutdown(bot: Bot):
    print("выкл бота")
    # принудительное завершение процесса при выходе из программы
    exit(0)
    # await bot.send_message(settings.bots.admin_id, text="Бот выключен!")


async def start_bot():
    logging.basicConfig(
        level=logging.INFO,
        format="""%(asctime)s - [%(levelname)s] -
        %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"""
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # middleware -- промежуточное ПО,
    # выполняется до или после прохождения фильтра апдейтом
    dp.message.middleware.register(check_registration.if_not_registered())
    # dp.message.middleware.register(counter_middleware.CounterMiddleware())

    # handler -- обработчик сообщений,
    dp.message.register(message_handlers.start_handler,
                        Command(commands=['start', 'run', 'старт']))
    dp.message.register(message_handlers.help_handler,
                        Command(commands=['help', 'хелп']))
    dp.message.register(message_handlers.sticker_echo_handler, F.sticker)
    dp.message.register(message_handlers.echo_handler, F.text)
    dp.message.register(got_true_contact, F.content_type.in_(
        ContentType.CONTACT), IsTrueContact())
    dp.message.register(
        got_fake_contact, F.content_type.in_(ContentType.CONTACT))
    dp.edited_message.register(message_handlers.edited_message_handler)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':

    API_TOKEN = conf.bots.bot_token
    # инициализируем бота
    bot = Bot(token=API_TOKEN, parse_mode='HTML')
    # bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    # инициализируем диспетчер
    dp = Dispatcher(bot=bot)

    loop = asyncio.get_event_loop()
    loop.create_task(checking_for_new_row(bot))
    loop.create_task(start_bot())
    loop.run_forever()
