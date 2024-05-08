from aiogram_sqlite_storage.sqlitestore import SQLStorage  # type: ignore
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from utils.config import TOKEN
from utils.scripts import include_routers
from utils.middleware import CooldownMiddleware
import asyncio


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="html"))
dp = Dispatcher(storage=SQLStorage())
include_routers(dp)

dp.message.middleware(CooldownMiddleware())
dp.callback_query.middleware(CooldownMiddleware())

asyncio.run(dp.start_polling(bot))
