from utils.custom_filters import CallbackCommand
from utils.database import get_host_port, set_host_port
from utils.keyboard import make_button, make_row, make_row_things
from utils.minecraft import get_info, dict_to_str
from utils.states import Setup
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, BotCommand, InlineQueryResultsButton
from aiogram.fsm.context import FSMContext
from uuid import uuid4
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


@rt.message(Command("server"))
async def cmd_server(message: Message, state: FSMContext):
    data = await state.get_data() or {}
    if "host" in data and "port" in data:
        host, port = data['host'], data['port']
        info = get_info(host, port)
        await message.answer(info, reply_markup=SERVER_SUCCESS)

    elif "host" in data:
        await message.answer("You need set port. You can do it in settings", reply_markup=MENU_BUTTON)

    elif "port" in data:
        await message.answer("You need set host. You can do it in settings", reply_markup=MENU_BUTTON)

    else:
        await message.answer("You need set host and port. You can do it in settings", reply_markup=MENU_BUTTON)


@rt.callback_query(CallbackCommand("server"))
async def callback_server(callback: CallbackQuery, state: FSMContext, commands: list[str]):
    if len(commands) == 2:
        uid = commands[1]
        if get_host_port(uid) is None:
            await callback.bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=make_row_things(["Go to the bot", "Try inline"], [{"url": f"https://t.me/{callback.bot._me.username}"}, {"switch_inline_query_current_chat": ""}]))
            await callback.answer()
            return
        host, port = get_host_port(uid)
        info = get_info(host, port)

        try: await callback.bot.edit_message_text(inline_message_id=callback.inline_message_id, text=info, reply_markup=make_row_things(["Retry", "Go to the bot", "Try inline"], [{"callback": f"server {uid}"}, {"url": f"https://t.me/{callback.bot._me.username}"}, {"switch_inline_query_current_chat": ""}]))
        except: pass

    data = await state.get_data() or {}
    if "host" in data and "port" in data:
        host, port = data['host'], data['port']
        info = get_info(host, port)

        try: await callback.message.edit_text(info, reply_markup=SERVER_SUCCESS)
        except: pass

    elif "host" in data:
        try: await callback.message.edit_text("You need set port. You can do it in settings", reply_markup=MENU_BUTTON)
        except: pass

    elif "port" in data:
        try: await callback.message.edit_text("You need set host. You can do it in settings", reply_markup=MENU_BUTTON)
        except: pass

    else:
        try: await callback.message.edit_text("You need set host and port. You can do it in settings", reply_markup=MENU_BUTTON)
        except: pass

    await callback.answer()


@rt.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext):
    data = await state.get_data() or {}
    string_data = "\n• Host: {}\n• Port: {}".format(data.get('host'), data.get('port'))
    await message.answer(f"Current settigns are: {string_data}", reply_markup=SETTINGS_ROW)
    

@rt.callback_query(CallbackCommand("settings"))
async def callback_settings(callback: CallbackQuery, state: FSMContext, commands: list[str]):
    data = await state.get_data() or {}
    string_data = "\n• Host: {}\n• Port: {}".format(data.get('host'), data.get('port'))
    try: await callback.message.edit_text(f"Current settigns are: {string_data}", reply_markup=SETTINGS_ROW)
    except: pass
    await callback.answer()


@rt.message(Command("setup"))
async def cmd_setup(message: Message, state: FSMContext):
    match message.text.split():
        case [_, "host", host]:
            await state.update_data({"host": message.text})
            await message.answer(f"Host is setted to {message.text}", reply_markup=MENU_BUTTON)
            await state.set_state()

        case [_, "port", port]:
            if port.isdecimal():
                port = int(port)
                await state.update_data({"port": port})
                await message.answer(f"Port is setted to {port}", reply_markup=MENU_BUTTON)
            
            elif port == ".":
                await state.update_data({"port": 25565})
                await message.answer(f"Port is setted to 25565", reply_markup=MENU_BUTTON)
            
            else:
                await message.answer("Input a correct port or just \".\"")
        
        case [_, "host"]:
            await state.set_state(Setup.host)
            await message.answer("Write host…")

        case [_, "port"]:
            await state.set_state(Setup.port)
            await message.answer("Write port… Or input \".\" for default value (25565)")

        case [_]:
            await message.answer("/setup port [port] or /setup host [host]", reply_markup=MENU_BUTTON)
        case _:
            await message.answer("what?", reply_markup=MENU_BUTTON)


@rt.callback_query(CallbackCommand("setup"))
async def callback_setup(callback: CallbackQuery, state: FSMContext, commands: list[str]):
    match commands:
        case [_, "host"]:
            await state.set_state(Setup.host)
            try: await callback.message.edit_text("Write host…")
            except: pass

        case [_, "port"]:
            await state.set_state(Setup.port)
            try: await callback.message.edit_text("Write port… Or input \".\" for default value (25565)")
            except: pass

        case _:
            try: await callback.message.edit_text("what?", reply_markup=MENU_BUTTON)
            except: pass
    await callback.answer()


@rt.message(StateFilter(Setup.host))
async def set_host(message: Message, state: FSMContext):
    await state.update_data({"host": message.text})
    await message.answer(f"Host is setted to {message.text}", reply_markup=MENU_BUTTON)
    await state.set_state()


@rt.message(StateFilter(Setup.port), F.text.len().in_(range(1, 6)))
async def set_port(message: Message, state: FSMContext):
    if message.text.isdecimal():
        port = int(message.text)
        await state.update_data({"port": port})
        await state.set_state()
        await message.answer(f"Port is setted to {port}", reply_markup=MENU_BUTTON)
    
    elif message.text == ".":
        await state.update_data({"port": 25565})
        await state.set_state()
        await message.answer(f"Port is setted to 25565", reply_markup=MENU_BUTTON)
    
    else:
        await message.answer("Input a correct port or just \".\"")


def _get_info(inline, port, host):
    info = get_info(host, port, to_dict=True)
    string_info = dict_to_str(info)
    uid = str(uuid4())
    if info.get('status'):
        article_safe = InlineQueryResultArticle(
            id=uid,
            title=info.get('description'),
            description=string_info,
            input_message_content=InputTextMessageContent(
                message_text=string_info                
            ),
            reply_markup=make_row_things(["Retry", "Go to the bot", "Try inline"], [{"callback": f"server {uid}"}, {"url": f"https://t.me/{inline.bot._me.username}"}, {"switch_inline_query_current_chat": ""}])
        )
    else:
        article_safe = InlineQueryResultArticle(
            id=str(uuid4()),     # status=False, string_status=TURNED_OFF, description=description, version=version, onp=onp, maxp=maxp
            title=info.get('string_status'),
            description=string_info,
            input_message_content=InputTextMessageContent(
                message_text=info.get('string_status')
            ),
            reply_markup=make_row_things(["Retry", "Go to the bot", "Try inline"], [{"callback": f"server {uid}"}, {"url": f"https://t.me/{inline.bot._me.username}"}, {"switch_inline_query_current_chat": ""}])
        )
    set_host_port(uid, host, port)

        # Idea for setting "SAFE MODE" which default will be ON
        # article_unsafe = InlineQueryResultArticle(
        #     id = str(uuid4()),
        #     title = "[UNSAFE] Server offline…",
        #     description = "This article will show server's IP and PORT. Be careful with it!",
        #     input_message_content=InputTextMessageContent(
        #         message_text="I try check server, but it is offline…"
        #     )
        # )
    return [article_safe]


@rt.inline_query()
async def inline_info(inline: InlineQuery, state: FSMContext):
    button = None
    data = await state.get_data() or {}
    if len(inline.query) == 0 and "host" in data and "port" in data:
        host, port = data['host'], data['port']
        article = _get_info(inline, port, host)
    elif len(inline.query) != 0 and inline.query.count(":") == 1 and inline.query.split(":")[1].isdecimal():
        host, port = inline.query.split(":")
        article = _get_info(inline, port, host)
    elif len(inline.query) != 0:
        host = inline.query
        article = _get_info(inline, port)
    else:
        button = InlineQueryResultsButton(text="Set these parameters", start_parameter="settings")
        article = [
            InlineQueryResultArticle(
                id="not_setted",     # status=False, string_status=TURNED_OFF, description=description, version=version, onp=onp, maxp=maxp
                title="Host or port are not setted",
                description="You need set these values in this bot.",
                input_message_content=InputTextMessageContent(
                    message_text="<i>I didn't set host and port in this bot...</i>",
                    parse_mode="html"
                ),
                reply_markup=make_row_things(["Go to the bot", "Try inline"], [{"url": f"https://t.me/{inline.bot._me.username}"}, {"switch_inline_query_current_chat": ""}])
            )
        ]
    
    await inline.answer(article, cache_time=0, is_personal=True, button=button)
