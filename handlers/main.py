from utils.custom_filters import CallbackCommand
from utils.database import get_host_port, set_host_port
from utils.keyboard import make_button, make_row, make_row_things, make_keyboard
from utils.minecraft import get_info_str
from utils.states import Setup
from utils.types import MainGetInfo, MainInfo
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, ChosenInlineResult, InlineQueryResultsButton, User
from aiogram.fsm.context import FSMContext
from uuid import uuid4
import asyncio
import logging
import time


logger = logging.getLogger(__name__)
rt = Router()
TIMEOUT = 60  # Minutes
MENU_BUTTON = button = make_button("Menu", "menu")
IN_MENU_ROW = make_row(["Get server's state", "Settings"], ["server", "settings"])
SERVER_SUCCESS = make_row(("Menu", "Retry"), ("menu", "server"))
SERVER_FAIL = lambda username: make_row_things(["Go to the bot", "Try inline"], [{"url": f"https://t.me/{username}"}, {"switch_inline_query_current_chat": ""}])
SettingsRow = lambda data: make_keyboard(
    [["Setup host", "Setup port"], [("Turn " + ("off" if data.get('safe_mode', True) else "on") + " safe mode"), "Go to the menu"]], 
    [[{"callback": "setup host"}, {"callback": "setup port"}], [{"callback": "setup safe_mode"}, {"callback": "menu"}]])


@rt.callback_query(CallbackCommand("auto_update"))
async def callback_auto_update(callback: CallbackQuery, state: FSMContext, commands: list[str]):
    result = None
    match commands:
        case [_, uid, ("s" | "u") as sm]:
            await callback.answer("Started auto_update!")
            time_start = time.time()
            time_current = time.time()
            while time_current - time_start <= TIMEOUT*60:
                cb = callback.model_copy(update={'data': f"server {uid} a{sm}"})
                success = await callback_server(cb, state, ['server', uid, "a"+sm])
                if not success:
                    logger.warning("IDK WHAT HAPPENED")
                    break
                time_current = time.time()
                await asyncio.sleep(5)

        case _:
            result = "What?"
            await callback.answer(result)


@rt.message(Command("server"))
async def cmd_server(message: Message, state: FSMContext):
    data = await state.get_data() or {}
    if "host" in data and "port" in data:
        host, port = data['host'], data['port']
        info = await _get_info(message, host, port)
        result = info.unsafe.message_text
        await message.answer(result, reply_markup=SERVER_SUCCESS)

    elif "host" in data:
        await message.answer("You need set port. You can do it in settings", reply_markup=MENU_BUTTON)

    elif "port" in data:
        await message.answer("You need set host. You can do it in settings", reply_markup=MENU_BUTTON)

    else:
        await message.answer("You need set host and port. You can do it in settings", reply_markup=MENU_BUTTON)

async def uid_is_invalid(callback, bot: Bot, uid):
    try: await callback.answer()
    except: pass

    if get_host_port(uid) is None:
        try: await bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=SERVER_FAIL(bot._me.username))
        except: pass
        return True
    return False
    

@rt.callback_query(CallbackCommand("server"))
async def callback_server(callback: CallbackQuery, state: FSMContext, commands: list[str]):
    current_time = time.strftime("%Y.%m.%d, %H:%M:%S%zUTC")
    message: Message = callback.message
    bot = callback.bot
    username = callback.bot._me.username
    match commands:
        case ['server', uid, 'as']:
            uid = commands[1]
            if await uid_is_invalid(callback, bot, uid):
                return False
            info = await _get_info(callback, *get_host_port(uid), uid)
            try: await bot.edit_message_text(inline_message_id=callback.inline_message_id, text=info.safe.message_text, reply_markup=SERVER_FAIL(username))
            except: pass
            
        case ['server', uid, 'au']:
            uid = commands[1]
            if await uid_is_invalid(callback, bot, uid):
                return False
            info = await _get_info(callback, *get_host_port(uid), uid)

            try: await bot.edit_message_text(inline_message_id=callback.inline_message_id, text=info.unsafe.message_text, reply_markup=SERVER_FAIL(username))
            except: pass
        
        case ['server', uid, 'safe' | 's']:
            uid = commands[1]
            if await uid_is_invalid(callback, bot, uid):
                return False
            info = await _get_info(callback, *get_host_port(uid), uid)
            try: await bot.edit_message_text(inline_message_id=callback.inline_message_id, text=info.safe.message_text, reply_markup=info.safe.reply_markup)
            except: pass
            
        case ['server', uid, 'unsafe' | 'u']:
            uid = commands[1]
            if await uid_is_invalid(callback, bot, uid):
                return False
            info = await _get_info(callback, *get_host_port(uid), uid)

            try: await bot.edit_message_text(inline_message_id=callback.inline_message_id, text=info.unsafe.message_text, reply_markup=info.unsafe.reply_markup)
            except: pass
        
        case ['server', uid, _]:
            logger.warning(str(commands))

        case ['server']:
            data = await state.get_data() or {}
            host, port = str(data.get('host')), str(data.get('port'))
            match [host, port]:
                case ["None", "None"]:
                    try: await message.edit_text("You need set host and port. You can do it in settings", reply_markup=MENU_BUTTON)
                    except: pass

                case ["None", _]:
                    try: await message.edit_text("You need set host. You can do it in settings", reply_markup=MENU_BUTTON)
                    except: pass
                
                case [__builtins__, "None"]:
                    try: await message.edit_text("You need set port. You can do it in settings", reply_markup=MENU_BUTTON)
                    except: pass

                case [_, _]:
                    info = await _get_info(callback, host, port)
                    try: await message.edit_text(info.unsafe.message_text, reply_markup=info.unsafe.reply_markup)
                    except: pass
                
        case _:
            await callback.answer("What?")
    return True


safe_mode_string = {True: "✅", False: "🚫"}
def format_settings(data): return "\n• Host: {}\n• Port: {}\n• Safe mode: {}".format(data.get('host'), data.get('port'), safe_mode_string[bool(data.get('safe_mode', True))])

@rt.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext):
    data = await state.get_data() or {}
    string_data = format_settings(data)
    await message.answer(f"Current settings are: {string_data}", reply_markup=SettingsRow(data))
    

@rt.callback_query(CallbackCommand("settings"))
async def callback_settings(callback: CallbackQuery, state: FSMContext, commands: list[str]):

    data = await state.get_data() or {}
    string_data = format_settings(data)
    try: await callback.message.edit_text(f"Current settings are: {string_data}", reply_markup=SettingsRow(data))
    except: pass
    try: await callback.answer()
    except: pass


@rt.message(Command("setup"))
async def cmd_setup(message: Message, state: FSMContext):

    match message.text.split():
        case [_, "host", host]:
            await state.update_data({"host": host})
            await message.answer(f"Host is setted to {host}", reply_markup=MENU_BUTTON)
            await state.set_state()

        case [_, "port", port_str]:
            if port_str.isdecimal():
                port = int(port_str)
                await state.update_data({"port": port})
                await message.answer(f"Port is setted to {port}", reply_markup=MENU_BUTTON)
            
            elif port_str == ".":
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

        case [_, "safe_mode"]:
            await state.update_data(safe_mode=(not(await state.get_data()).get("safe_mode", True)))
            data = await state.get_data() or {}
            string_data = format_settings(data)
            try: await callback.message.edit_text(f"Current settings are: {string_data}", reply_markup=SettingsRow(data))
            except: pass

            try: await callback.answer()
            except: pass
        
        case _:
            try: await callback.message.edit_text("what?", reply_markup=MENU_BUTTON)
            except: pass
    
    try: await callback.answer()
    except: pass


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


async def _get_info(smth_with_bot=None, host="", port: str|int=25565, uid=str(uuid4())) -> MainGetInfo:
    if smth_with_bot is None or host == "":
        raise ValueError("First argument need to be not None, but something with atribute bot")
    bot: Bot = smth_with_bot.bot
    if isinstance(port, str): port=int(port)
    info = await get_info_str(host, port)
    KEYBOARD_SAFE = make_keyboard([[f"Enable autocheck ({TIMEOUT} minutes)","Retry"],["Go to the bot", "Try inline"]], [[{"callback": f"auto_update {uid} s"},{"callback": f"server {uid} safe"}],[{"url": f"https://t.me/{bot._me.username}"}, {"switch_inline_query_current_chat": ""}]])
    KEYBOARD_UNSAFE = make_keyboard([[f"Enable autocheck ({TIMEOUT} minutes)","Retry"],["Go to the bot", "Try inline"]], [[{"callback": f"auto_update {uid} u"},{"callback": f"server {uid} unsafe"}],[{"url": f"https://t.me/{bot._me.username}"}, {"switch_inline_query_current_chat": ""}]])
    
    string_status = info.splitlines()[0]

    title_safe = ("[SAFE] " + string_status)
    title_unsafe = "[UNSAFE] " + string_status
    
    desc_safe = ("This atricle isn't showing server's IP and port" + "\n" + "\n".join(info.splitlines()[1:]))
    desc_unsafe = "This atricle is showing server's IP and port" + "\n" + "\n".join(info.splitlines()[1:])

    msg_safe = info
    msg_unsafe = msg_safe + "\n" + f"• Server: <code>{host}:{port}</code>"
    return MainGetInfo(MainInfo(title_safe, desc_safe, msg_safe, KEYBOARD_SAFE), MainInfo(title_unsafe, desc_unsafe, msg_unsafe, KEYBOARD_UNSAFE))


async def _get_info_article(smth_with_bot=None, host="", port: str|int=25565, safe_mode=True, uid=str(uuid4())) -> list[InlineQueryResultArticle]:
    info = await _get_info(smth_with_bot, host, port, uid)
    safe, unsafe = info.safe, info.unsafe
    article_safe = InlineQueryResultArticle(id="_".join([uid, host.replace(".", "--"), str(port), "s"]), title=safe.title, description=safe.description, input_message_content=InputTextMessageContent(message_text=safe.message_text), reply_markup=safe.reply_markup)
    result = [article_safe]
    if not safe_mode:
        article_unsafe = InlineQueryResultArticle(id="_".join([uid, host.replace(".", "--"), str(port), "us"]), title=unsafe.title, description=unsafe.description, input_message_content=InputTextMessageContent(message_text=unsafe.message_text), reply_markup=unsafe.reply_markup)
        result.append(article_unsafe)
    return result


@rt.chosen_inline_result()
async def cir_info(cir: ChosenInlineResult, state: FSMContext):
    if cir.result_id.count("_") == 3:
        uid, host, port, safe_str = cir.result_id.split("_")
        host = host.replace("--", ".")
        set_host_port(uid, host, int(port))


@rt.inline_query()
async def inline_info(inline: InlineQuery, state: FSMContext):
    uid = str(uuid4()).replace("-", "")[:16]
    button = None
    data = await state.get_data() or {}
    safe_mode = data.get('safe_mode', True)
    if len(inline.query) == 0 and "host" in data and "port" in data:
        host, port = data['host'], data['port']
        article = await _get_info_article(inline, port=port, host=host, safe_mode=safe_mode, uid=uid)

    elif len(inline.query) != 0 and inline.query.count(":") == 1 and inline.query.split(":")[1].isdecimal():
        host, port = inline.query.split(":")
        article = await _get_info_article(inline, host=host, port=port, safe_mode=safe_mode, uid=uid)

    elif len(inline.query) != 0 and inline.query.count(":") == 0:
        host = inline.query
        article = await _get_info_article(inline, host=host, safe_mode=safe_mode, uid=uid)

    else:
        button = InlineQueryResultsButton(text="Set these parameters", start_parameter="settings")
        article = [
            InlineQueryResultArticle(
                id="not_setted",
                title="Host or port are not setted",
                description="You need set these values in this bot.",
                input_message_content=InputTextMessageContent(
                    message_text="<i>I didn't set host and port in this bot...</i>",
                ),
                reply_markup=make_row_things(["Go to the bot", "Try inline"], [{"url": f"https://t.me/{inline.bot._me.username}"}, {"switch_inline_query_current_chat": ""}])
            )
        ]
    
    await inline.answer(article, cache_time=0, is_personal=True, button=button)  # type: ignore  # I try fix this but idk what is wrong...  i love mypy <3
