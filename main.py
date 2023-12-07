from cfg import *
from handlers import r as router
import asyncio
import platform
from aiohttp import web
import logging
from aiogram import Bot, Dispatcher
from aiogram.types.input_file import FSInputFile
from aiogram.webhook.aiohttp_server import *
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
import sys


async def dropWebhook(bot):
    await bot.delete_webhook()


async def setWebhook(bot):
    await bot.dropWebhook()
    await bot.set_webhook(url = WEBHOOK_URL + WEBHOOK_PATH, drop_pending_updates = True, certificate=FSInputFile(SSL_CERT))


def main() -> None:
    bot, dp = prepBot()
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


async def main_poll():
    bot,dp = prepBot()
    await dropWebhook(bot)
    await dp.start_polling(bot)


def prepBot():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    return bot,dp


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if platform.system() in ('Darwin','Windows'):
        asyncio.run(main_poll())
    else:
        main()
