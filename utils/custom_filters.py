from aiogram.types import CallbackQuery
from aiogram.filters import BaseFilter
from typing import Union


class CallbackCommand(BaseFilter):
    """If command then return commands to filter/handler"""
    def __init__(self, command: Union[str, list]):
        self.command = command
    
    async def __call__(self, cq: CallbackQuery) -> bool:
        if isinstance(self.command, list) and cq.data.split() and cq.data.split()[0] in self.command:
            return {'commands': cq.data.split()}
        elif isinstance(self.command, str) and cq.data.split() and cq.data.split()[0] == self.command:
            return {'commands': cq.data.split()}
        else:
            return False
    