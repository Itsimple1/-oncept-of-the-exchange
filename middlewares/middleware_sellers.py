from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

import api_db.sql_bd_buyers


class block_user(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        if await api_db.sql_bd_buyers.is_ban_seller(event.from_user.id):
            return
        return await handler(event, data)
