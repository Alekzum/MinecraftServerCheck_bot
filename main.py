from aiogram_sqlite_storage.sqlitestore import SQLStorage
from aiogram import Bot, Dispatcher
from utils.config import TOKEN
from utils.scripts import include_routers
import asyncio


bot = Bot(token=TOKEN)
dp = Dispatcher(storage=SQLStorage())
include_routers(dp)

asyncio.run(dp.start_polling(bot))