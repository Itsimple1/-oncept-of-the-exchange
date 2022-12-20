import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.storage.base import StorageKey

import config
from handlers_sellers import username_change, support, Redemption, menu, dring_up, registration
from middlewares.middleware_sellers import block_user

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()

# Enabling logs---------------------------------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)

# Bot assignment--------------------------------------------------------------------------------------------------------
bot = Bot(token=config.TOKEN_SELLERS)
dp = Dispatcher()

# Connecting filters and middleware-------------------------------------------------------------------------------------
dp.message.filter(F.chat.type == "private")
dp.message.outer_middleware(block_user())


async def init_state():
    print("init_state_seller")
    cur.execute("SELECT * FROM wait_orders WHERE condition=0;")
    lines = cur.fetchall()
    for line in lines:
        user_id = line[5]
        state_with: FSMContext = FSMContext(
            bot=bot,  # объект бота
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=StorageKey(
                chat_id=user_id,  # если юзер в ЛС, то chat_id=user_id
                user_id=user_id,
                bot_id=bot.id))
        await state_with.set_state(Redemption.Sell.wait_confirm_complete)
        await state_with.update_data(num=line[0], id_buy=line[1], link=line[2], price=line[3], price_buy=line[4])


async def send_message_to_seller(id_sell, text, keyboard=0):
    if keyboard != 0:
        await bot.send_message(id_sell, text=text, reply_markup=keyboard)
    else:
        await bot.send_message(id_sell, text)


async def send_sticker_to_seller(id_sell, code_sticker):
    await bot.send_sticker(chat_id=id_sell, sticker=code_sticker)


async def main():
    dp.include_router(username_change.router)
    dp.include_router(Redemption.router)
    dp.include_router(support.router)
    dp.include_router(registration.router)
    dp.include_router(dring_up.router)
    dp.include_router(menu.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(init_state())
    asyncio.run(main())
