from typing import Literal, Union, Optional
from mctools import PINGClient
import traceback
import logging


LOGGER = logging.getLogger(__name__)
TURNED_OFF = "🔴 Server is offline"
TURNED_ON = "🟢 Server is online"
REFUSED = TURNED_OFF + "\nConnection is refused…"
TIMEOUT = TURNED_OFF + "\nConnection is timedout…"
RESULT_DICT = dict[Literal['status', 'string_status', 'description', 'version', 'maxp', 'onp', 'response_time', 'players'], Union[bool, str, int]]  # Players are optional


def parse_stats(stats) -> dict:
    try:
        maxp = stats['players']['max']
        onp = stats['players']['online']
        version = stats['version']['name']
        description = stats['description']
        players_list: list[str, str] = list(sorted(map(lambda p: p[0], stats['players'].get('sample') or [])))
        response_time = stats['time']
    except KeyError:
        error = traceback.format_exc()
        LOGGER.warning(error + "\n" + f"Dict is {stats}!")
        exit(f"Dict is {stats}!")
    return maxp, onp, version, description, players_list, response_time


def _format_message(stats) -> str:
    maxp, onp, version, description, players_list, response_time = parse_stats(stats)
    # Fix for aternos
    if maxp == 0:
        result = "\n".join([TURNED_OFF, f"🪧 Description: {description}", f"🔢 Current version {version}", f"👥 Players count: {onp}/{maxp}", f"⌚ Response time: {response_time:.2f}"])
    else:
        pp = "\n".join(players_list)
    
        result = "\n".join([TURNED_ON, f"🪧 Description: {description}", f"🔢 Current version {version}", f"👥 Players count: {onp}/{maxp}", "", pp, "", f"⌚ Response time: {response_time:.2f}"])
    return result


def _format_message_dict(stats) -> RESULT_DICT:
    maxp, onp, version, description, players_list, response_time = parse_stats(stats)
    # Fix for aternos
    if maxp == 0:
        result = dict(status=False, string_status=TURNED_OFF, description=description, version=version, onp=onp, maxp=maxp, response_time=response_time)
    
    elif players_list is not None:
        pp = players_list
        result = dict(status=True, string_status=TURNED_ON, description=description, version=version, players=pp, maxp=maxp, onp=onp, response_time=response_time)
    
    else:
        result = dict(status=False, string_status=TURNED_OFF, description=description, version=version, maxp=maxp, onp=onp, response_time=response_time)
    return result


def dict_to_str(d: RESULT_DICT) -> str:
    """Because I can do it, it will be"""
    ms = d.get('ping')
    maxp = d.get('maxp')
    onp = d.get('onp')
    version = d.get('version')
    description = d.get('description')
    players_list: str = d.get('players')
    response_time = d.get('response_time') or 0.0
    
    # Fix for aternos
    if maxp == 0:
        result = "\n".join([TURNED_OFF, f"🪧 Description: {description}", f"🔢 Current version {version}", f"👥 Players count: {onp}/{maxp}", f"⌚ Response time: {response_time:.2f}"])
    
    elif players_list is not None:
        pp = "\n".join(players_list)
        result = "\n".join([TURNED_ON, f"🪧 Description: {description}", f"🔢 Current version {version}", f"👥 Players count: {onp}/{maxp}", "", pp, "", f"⌚ Response time: {response_time:.2f}"])

    else:
        result = "\n".join([TURNED_ON, f"🪧 Description: {description}", f"🔢 Current version {version}", f"👥 Players count: {onp}/{maxp}", f"⌚ Response time: {response_time:.2f}"])

    return result


async def get_info(host: str, port=25565, to_dict=False) -> RESULT_DICT:
    """Return string for some server in dict"""

    client = PINGClient(host, port, format_method=PINGClient.REMOVE)
    try:
        stats = client.get_stats()
    except ConnectionRefusedError:
        result = {"status": False, "string_status": REFUSED} if to_dict else REFUSED
    except:
        result = {"status": False, "string_status": TIMEOUT} if to_dict else TIMEOUT
    else:
        result = _format_message_dict(stats) if to_dict else _format_message(stats)
    # try:
        # stats = clean_stats(client.get_stats())
        # print(stats)
        # result = _format_message_dict(stats) if to_dict else _format_message(stats)
    
    # except Exception as ex:
        # print(repr(ex))
        # result = dict(status=False, string_status=TURNED_OFF) if to_dict else TURNED_OFF
    return result
