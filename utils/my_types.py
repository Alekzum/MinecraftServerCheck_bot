from aiogram.types import InlineKeyboardMarkup
from typing import TypedDict
from dataclasses import dataclass


class MinecraftResultDict(TypedDict):
    status: bool
    string_status: str
    description: str | None
    version: str | None
    maxp: int | None
    onp: int | None
    response_time: float | None
    players: list[str] | None


@dataclass
class MainInfo():
    title: str
    description: str
    message_text: str
    reply_markup: InlineKeyboardMarkup


@dataclass
class MainGetInfo():
    safe: MainInfo
    unsafe: MainInfo
    status: bool