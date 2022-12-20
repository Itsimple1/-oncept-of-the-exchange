import asyncio
import logging
import sqlite3

from aiogram import types, Bot, Dispatcher, F
from aiogram.dispatcher.fsm.storage.base import StorageKey
from aiogram.dispatcher.fsm.context import FSMContext

import api_db.sql_bd_buyers
import config
from handlers_buyers import menu, top_up, support, registration, Redemption, username_change
from middlewares.middleware_buyers import block_user

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()

# Enabling logs---------------------------------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)

# Bot assignment--------------------------------------------------------------------------------------------------------
bot = Bot(token=config.TOKEN_BUYERS)
dp = Dispatcher()

# Connecting filters and middleware-------------------------------------------------------------------------------------
dp.message.filter(F.chat.type == "private")
dp.message.outer_middleware(block_user())


async def send_message_to_buyer(id_buy, text, keyboard=0):
    if keyboard != 0:
        await bot.send_message(id_buy, text=text, reply_markup=keyboard)
    else:
        await bot.send_message(id_buy, text)


async def send_sticker_to_buyer(id_buy, code_sticker):
    await bot.send_sticker(chat_id=id_buy, sticker=code_sticker)


async def init_state():
    print("init_state")
    cur.execute("SELECT * FROM orders;")
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
        await state_with.set_state(Redemption.Order.awaiting_transfer)
        await state_with.update_data(num=line[0])
    cur.execute("SELECT * FROM wait_orders;")
    lines = cur.fetchall()
    for line in lines:
        user_id = line[1]
        chat_id = line[1]
        state_with: FSMContext = FSMContext(
            bot=bot,  # объект бота
            storage=dp.storage,  # dp - экземпляр диспатчера
            key=StorageKey(
                chat_id=chat_id,  # если юзер в ЛС, то chat_id=user_id
                user_id=user_id,
                bot_id=bot.id))
        await state_with.set_state(Redemption.Order.awaiting_transfer)
        await state_with.update_data(num=line[0])


async def main():
    dp.include_router(Redemption.router)
    dp.include_router(support.router)
    dp.include_router(registration.router)
    dp.include_router(username_change.router)
    dp.include_router(top_up.router)
    dp.include_router(menu.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


if __name__ == "__main__":
    asyncio.run(api_db.sql_bd_buyers.start_bd_api())
    asyncio.run(init_state())
    asyncio.run(main())
