from aiogram import Dispatcher
import os


def include_routers(dp: Dispatcher, root="handlers"):
    files = list(filter(lambda x: x.endswith(".py"), os.listdir(root)))
    dp.include_routers(*[__import__(root+"."+file.removesuffix(".py"), fromlist=('rt')).rt for file in files])