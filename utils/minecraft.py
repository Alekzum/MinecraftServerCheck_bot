from socket import gaierror
from .my_types import MinecraftResultDict
from typing import Literal, Union, Callable
import traceback
import logging
import httpx
import time


logger = logging.getLogger(__name__)

TURNED_OFF = "🔴 Server is offline"
TURNED_ON = "🟢 Server is online"
REFUSED = TURNED_OFF + "\nConnection is refused…"
TIMEOUT = TURNED_OFF + "\nConnection is timedout…"
NOT_EXISTS = TURNED_OFF + "\nMaybe this server doesn't exists?"
UNEXCEPTED = TURNED_OFF + "\nUnknown server's status..."
UNEXCEPTED_LAMBDA: Callable[[Exception], str] = lambda ex: TURNED_OFF + "\nUnknown server's status...\nDetailed error: " + repr(ex)

RESULT_DICT = dict[Literal['status', 'string_status', 'description', 'version', 'maxp', 'onp', 'response_time', 'players'], Union[bool, str, str, str, int, int, float, list[str]]]  # Players are optional

client = httpx.AsyncClient(base_url="https://api.mcsrvstat.us/3/", timeout=30)

async def get_stats(host, port):
    start_time = time.time()

    stats = (await client.get(f"{host}")).json()
    # exit(str(stats))

    end_time = time.time()
    response_time = end_time - start_time
    stats['time'] = response_time
    return stats


def get_cur_time() -> str:
    current_time = time.strftime("%d.%m.%Y, %H:%M:%S%zUTC")
    return f"\n\n• {current_time}"

def parse_stats(stats: dict) -> tuple[bool, str |tuple[int, int, str, str, list[str], float]]:
    placeholder_list = [":rofl:",":roflan_pominki:"]
    try:
        if stats['online']:
            players = stats.get("players")
            maxp, onp = players['max'], players['online']
            version = stats['protocol']['name']
            description = "    MOTD: \n" + "\n".join(stats.get('motd', {}).get('clean', placeholder_list)) + "\n    INFO: \n" + "\n".join(stats.get('info', {}).get('clean', placeholder_list))
            players_list: list[str] | list = [x.get("name") for x in stats['players'].get('list', [{}]) if x and x.get("name")]
        else:
            maxp = onp = 0
            players_list = None
            version = description = "Unknown"
        response_time = stats['time']
    except KeyError as ex:
        error = traceback.format_exc()
        logger.warning(error + "\n" + f"Dict is {stats}!")
        # exit(f"Dict is {stats}!")
        return (False, repr(ex))
    # players_list = players_list or placeholder_list
    return (True, (maxp, onp, version, description, players_list, response_time))


def _format_message(stats) -> str:
    success, result = parse_stats(stats)
    if not success:
        return f"Ошибка при получении информации: {result}"
    maxp, onp, version, description, players_list, response_time = result
    # Fix for aternos
    if maxp == 0:
        result = "\n".join([TURNED_OFF, f"👥 Players count: {onp}/{maxp}", f"🪧 Description: \n{description}", f"🔢 Current version {version}", f"⌚ Response time: {response_time:.2f}"])
    else:
        pp = ("\n" + "\n".join(players_list)) if players_list else "(DIDN'T PROVIDED, aka :roflan_pominki:)"
    
        result = "\n".join([TURNED_ON, f"👥 Players count: {onp}/{maxp}", f"   Players: {pp}", f"🪧 Description: \n{description}", f"🔢 Current version {version}", f"⌚ Response time: {response_time:.2f}"])
    return result


def _format_message_dict(stats) -> MinecraftResultDict:
    success, result = parse_stats(stats)
    if not success:
        return MinecraftResultDict(False, TURNED_OFF, f"Ошибка при получении информации: {result}")
    maxp, onp, version, description, players_list, response_time = result
    # Fix for aternos
    if maxp == 0:
        result = MinecraftResultDict(status=False, string_status=TURNED_OFF, description=description, version=version, maxp=maxp, onp=onp, response_time=response_time, players=None)
    
    elif players_list is not None:
        pp = players_list
        result = MinecraftResultDict(status=True, string_status=TURNED_ON, description=description, version=version, maxp=maxp, onp=onp, response_time=response_time, players=pp)
    
    else:
        result = MinecraftResultDict(status=False, string_status=TURNED_OFF, description=description, version=version, maxp=maxp, onp=onp, response_time=response_time, players=None)
    result.update(string_status=result['string_status'] + get_cur_time())
    return result


def dict_to_str(d: MinecraftResultDict) -> str:
    current_time = time.strftime("%Y.%m.%d, %H:%M:%S%zUTC")
    """Because I can do it, it will be"""
    maxp = d.get('maxp', 0)
    onp = d.get('onp', 0)
    version = d.get('version', ":rofl:")
    description = "\n".join(d.get('description'))
    players_list: list[str] | None = d.get('players')
    response_time = d.get('response_time') or 1337.1337
    
    # Fix for aternos
    if maxp == 0:
        result = "\n".join([TURNED_OFF, f"🪧 Description: \n{description}", f"🔢 Current version {version}", f"👥 Players count: {onp}/{maxp}", f"⌚ Response time: {response_time:.2f}"])
    
    elif players_list is not None:
        pp = "\n".join(players_list)
        result = "\n".join([TURNED_ON, f"🪧 Description: \n{description}", f"🔢 Current version {version}", f"👥 Players count: {onp}/{maxp}", "", pp, "", f"⌚ Response time: {response_time:.2f}"])

    else:
        result = "\n".join([TURNED_ON, f"🪧 Description: \n{description}", f"🔢 Current version {version}", f"👥 Players count: {onp}/{maxp}", f"⌚ Response time: {response_time:.2f}"])

    return result + f"\n• {current_time}"


async def get_info_dict(host: str, port=25565) -> MinecraftResultDict | str:
    """Return string for some server in dict (or string)"""

    try:
        stats = await get_stats(host, port)
    except ConnectionRefusedError:
        result = MinecraftResultDict(status=False, string_status=REFUSED, description=None, version=None, maxp=None, onp=None, players=None, response_time=None)
    except:
        result = MinecraftResultDict(status=False, string_status=TIMEOUT, description=None, version=None, maxp=None, onp=None, players=None, response_time=None)
    else:
        result = _format_message_dict(stats)
        
    return result


async def get_info_str(host: str, port=25565) -> str:
    """Return info for some server"""

    try:
        stats = await get_stats(host, port)
    except ConnectionRefusedError:
        result = REFUSED
    except (TimeoutError, httpx.ConnectTimeout) as ex:
        result = TIMEOUT
    except gaierror as ex:
        result = NOT_EXISTS
    except Exception as ex:
        result = UNEXCEPTED_LAMBDA(ex)
        logger.warning(f"{host}:{port}. {ex!r}")
    else:
        result = _format_message(stats)
        
    return result + get_cur_time()


async def get_info_tuple(host: str, port=25565) -> tuple[str, bool]:
    """Return info for some server and boolean status"""
    status = False
    try:
        stats = await get_stats(host, port)
    except ConnectionRefusedError:
        result = REFUSED
    except TimeoutError as ex:
        result = TIMEOUT
    except gaierror as ex:
        result = NOT_EXISTS
    except Exception as ex:
        result = UNEXCEPTED_LAMBDA(ex)
        exception = traceback.format_exc()
        logger.warning(f"{host}:{port}.\n{exception}\n")
    else:
        result = _format_message(stats)
        status = True
        
    return (result + get_cur_time(), status)