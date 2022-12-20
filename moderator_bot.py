import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.storage.base import StorageKey

import api_db
import config
from handlers_moderator import moder_support_sel, menu, moder_support_buy, moder_dring_up, moderator_order
from middlewares.middleware_moderator import access

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()

# Enabling logs---------------------------------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)

# Bot assignment--------------------------------------------------------------------------------------------------------
bot = Bot(token=config.TOKEN_MODERATOR)
dp = Dispatcher()

# Connecting filters and middleware-------------------------------------------------------------------------------------
dp.message.filter(F.chat.type == "private")
dp.message.outer_middleware(access())


async def init_state():
    print("init_state_moderator")
    cur.execute("SELECT * FROM dring_up WHERE id_moderator!=0;")
    lines = cur.fetchall()
    for line in lines:
        user_id = line[1]
        state_with: FSMContext = FSMContext(
            bot=bot,  # объект бота
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=StorageKey(
                chat_id=user_id,  # если юзер в ЛС, то chat_id=user_id
                user_id=user_id,
                bot_id=bot.id))
        await state_with.set_state(moder_dring_up.Moder_dring_up.wait_for_processing)
        await state_with.update_data(number=line[0], id_sel=line[1], amount=line[2], requisites=line[3],
                                     history_orders=await api_db.sql_bd_moderator.get_history_orders(line[1]))


async def main():
    dp.include_router(moder_support_sel.router)
    dp.include_router(moder_support_buy.router)
    dp.include_router(moderator_order.router)
    dp.include_router(moder_dring_up.router)
    dp.include_router(menu.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(init_state())
    asyncio.run(main())
