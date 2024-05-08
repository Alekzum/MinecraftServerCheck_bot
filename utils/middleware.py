from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import time


t_d = {0: "секунд", 1: "секунду", 2: "секунды", 5: "секунд"}
t_d.update({3:t_d[2], 4:t_d[2], 6:t_d[5], 7:t_d[5], 8:t_d[5], 9:t_d[5]})
seconds_to_str = t_d.copy()

class CooldownMiddleware(BaseMiddleware):
    """If from previous update from user didn't pass *cooldown* seconds, then update will not invoked"""
    def __init__(self, cooldown: float = 0.5):
        self.cooldown = cooldown
        self.times = dict()
    
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        uid = event.from_user.id
        cur_time = time.time()
        delta_time = cur_time - self.times.get(uid, 0)
        if delta_time < self.cooldown:
            if isinstance(event, CallbackQuery):
                remains = self.cooldown - delta_time
                remains_last_d = (remains//1)%10
                await event.answer(f"слишком быстро, подожди чут-чут 🤏, вот прям {remains:.1f} {seconds_to_str[remains_last_d]}")
            return
        else:
            self.times[uid] = cur_time
            return await handler(event, data)
