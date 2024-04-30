from handlers.main import cmd_settings
from utils.custom_filters import CallbackCommand
from utils.keyboard import make_button, make_row
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.fsm.context import FSMContext
import logging


logger = logging.getLogger(__name__)
rt = Router()
MENU_BUTTON = button = make_button("Menu", "menu")
IN_MENU_ROW = make_row(["Get server's state", "Settings"], ["server", "settings"])
SERVER_SUCCESS = make_row(("Menu", "Retry"), ("menu", "server"))
SETTINGS_ROW = make_row(["Setup host", "Setup port", "Go to the menu"], ["setup host", "setup port", "menu"])


@rt.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    if data is None:
        await state.set_data({})
    
    args = message.text.split(" ")
    match args:
        case ['/start', 'settings']:
            msg = message.model_copy(update={'text': '/settings'})
            await cmd_settings(msg, state)
            return
        case ['/start']:
            pass
        case _:
            logger.warn(f"Args for start are {args}")
            return
    
    await message.bot.set_my_commands([
        BotCommand(command="start", description="Start message"),
        BotCommand(command="menu", description="Just menu"),
        BotCommand(command="settings", description="Go to the settings"),
        BotCommand(command="server", description="Check info about server"),
        BotCommand(command="setup", description="Change server's host and port"),
        BotCommand(command="cancel", description="Stop write info (like host or port)"),
    ])

    await message.answer("Hello!", reply_markup=MENU_BUTTON)


@rt.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.set_state()
    await message.answer("Сancelled.", MENU_BUTTON)


@rt.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    data = await state.get_data() or {}
    if "host" in data and "port" in data:
        result_text = f'You can check server "{data["host"]}:{data["port"]}"'

    elif "host" in data:
        result_text = "You need set port. You can do it in settings"

    elif "port" in data:
        result_text = "You need set host. You can do it in settings"

    else:
        result_text = "You need set host and port. You can do it in settings"
    await message.answer("You are in the menu.\n"+result_text, reply_markup=IN_MENU_ROW)


@rt.callback_query(CallbackCommand("menu"))
async def callback_menu(callback: CallbackQuery, state: FSMContext,):
    data = await state.get_data() or {}
    if "host" in data and "port" in data:
        result_text = f'You can check server "{data["host"]}:{data["port"]}"'

    elif "host" in data:
        result_text = "You need set port. You can do it in settings"

    elif "port" in data:
        result_text = "You need set host. You can do it in settings"

    else:
        result_text = "You need set host and port. You can do it in settings"
    try: await callback.message.edit_text("You are in the menu.\n"+result_text, reply_markup=IN_MENU_ROW)
    except: pass
    await callback.answer()
