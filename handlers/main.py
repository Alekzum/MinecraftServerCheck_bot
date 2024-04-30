from utils.custom_filters import CallbackCommand
from utils.database import get_host_port, set_host_port
from utils.keyboard import make_button, make_row, make_row_things, make_keyboard
from utils.minecraft import get_info, dict_to_str
from utils.states import Setup
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, BotCommand, InlineQueryResultsButton
from aiogram.fsm.context import FSMContext
from uuid import uuid4
import asyncio
import logging
import time


logger = logging.getLogger(__name__)
rt = Router()
MENU_BUTTON = button = make_button("Menu", "menu")
IN_MENU_ROW = make_row(["Get server's state", "Settings"], ["server", "settings"])
SERVER_SUCCESS = make_row(("Menu", "Retry"), ("menu", "server"))
SETTINGS_ROW = make_row(["Setup host", "Setup port", "Go to the menu"], ["setup host", "setup port", "menu"])


@rt.callback_query(CallbackCommand("auto_update"))
async def callback_auto_update(callback: CallbackQuery, state: FSMContext, commands: list[str]):
    result = None
    match commands:
        case [_, uid]:
            await callback.answer("Started auto_update!")
            time_start = time.time()
            time_current = time.time()
            while time_current - time_start <= 600:
                cb = callback.model_copy(update={'data': f"server {uid} auto_update"})
                success = await callback_server(cb, state, ['server', uid, 'auto_update'])
                if not success:
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
        info = await get_info(host, port)
        await message.answer(info, reply_markup=SERVER_SUCCESS)

    elif "host" in data:
        await message.answer("You need set port. You can do it in settings", reply_markup=MENU_BUTTON)

    elif "port" in data:
        await message.answer("You need set host. You can do it in settings", reply_markup=MENU_BUTTON)

    else:
        await message.answer("You need set host and port. You can do it in settings", reply_markup=MENU_BUTTON)


@rt.callback_query(CallbackCommand("server"))
async def callback_server(callback: CallbackQuery, state: FSMContext, commands: list[str]):
    if len(commands) == 3:
        current_time = time.strftime("%Y.%m.%d, %H:%M:%S%zUTC")
        uid = commands[1]
        if get_host_port(uid) is None:
            await callback.bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=make_row_things(["Go to the bot", "Try inline"], [{"url": f"https://t.me/{callback.bot._me.username}"}, {"switch_inline_query_current_chat": ""}]))
            await callback.answer("UID doesn't exists")
            return False
        
        host, port = get_host_port(uid)
        info = await get_info(host, port) + f"\n\n{current_time}"
        KEYBOARD = make_keyboard([["Go to the bot", "Try inline"]], [[{"url": f"https://t.me/{callback.bot._me.username}"}, {"switch_inline_query_current_chat": ""}]])

        try: await callback.bot.edit_message_text(inline_message_id=callback.inline_message_id, text=info, reply_markup=KEYBOARD)
        except: pass
        return True
        
    elif len(commands) == 2:
        uid = commands[1]
        if get_host_port(uid) is None:
            await callback.bot.edit_message_reply_markup(inline_message_id=callback.inline_message_id, reply_markup=make_row_things(["Go to the bot", "Try inline"], [{"url": f"https://t.me/{callback.bot._me.username}"}, {"switch_inline_query_current_chat": ""}]))
            await callback.answer()
            return
        host, port = get_host_port(uid)
        info = await get_info(host, port)
        KEYBOARD = make_keyboard([["Enable autocheck (only for 10 minutes)","Retry"],["Go to the bot", "Try inline"]], [[{"callback": f"auto_update {uid}"},{"callback": f"server {uid}"}],[{"url": f"https://t.me/{callback.bot._me.username}"}, {"switch_inline_query_current_chat": ""}]])

        try: await callback.bot.edit_message_text(inline_message_id=callback.inline_message_id, text=info, reply_markup=KEYBOARD)
        except: pass
    
    else:
        data = await state.get_data() or {}
        if "host" in data and "port" in data:
            host, port = data['host'], data['port']
            info = await get_info(host, port)

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
    return


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


async def _get_info(*, inline=None, host="", port=25565):
    if inline is None or host == "":
        return
    info = await get_info(host, port, to_dict=True)
    string_info = dict_to_str(info)
    uid = str(uuid4())
    KEYBOARD = make_keyboard([["Enable autocheck (only for 5 minutes)","Retry"],["Go to the bot", "Try inline"]], [[{"callback": f"auto_update {uid}"},{"callback": f"server {uid}"}],[{"url": f"https://t.me/{inline.bot._me.username}"}, {"switch_inline_query_current_chat": ""}]])
    if info.get('status'):
        article_safe = InlineQueryResultArticle(
            id=uid,
            title=info.get('description'),
            description=string_info,
            input_message_content=InputTextMessageContent(
                message_text=string_info                
            ),
            reply_markup=KEYBOARD
        )
    else:
        article_safe = InlineQueryResultArticle(
            id=str(uuid4()),     # status=False, string_status=TURNED_OFF, description=description, version=version, onp=onp, maxp=maxp
            title=info.get('string_status').splitlines()[0],
            description="\n".join(info.get('string_status').splitlines()[1:]),
            input_message_content=InputTextMessageContent(
                message_text=info.get('string_status')
            ),
            reply_markup=KEYBOARD
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
        article = await _get_info(inline=inline, port=port, host=host)
    elif len(inline.query) != 0 and inline.query.count(":") == 1 and inline.query.split(":")[1].isdecimal():
        host, port = inline.query.split(":")
        article = await _get_info(inline=inline, port=port, host=host)
    elif len(inline.query) != 0 and inline.query.count(":") == 0:
        host = inline.query
        article = await _get_info(inline=inline, host=host)
    else:
        button = InlineQueryResultsButton(text="Set these parameters", start_parameter="settings")
        article = [
            InlineQueryResultArticle(
                id="not_setted",
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
