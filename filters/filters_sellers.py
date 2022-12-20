from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message
import sqlite3

import config

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()


class is_one_digit(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        input_data = message.text.lower().split()
        if len(input_data) == 1 and str.isdigit(input_data[0]):
            count = int(input_data[0])
            return 0 < count < 10000
        return False


class order_no_in_wait_gb(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        cur.execute(f"SELECT * FROM waitGB WHERE id_sel={message.from_user.id} and condition=0")
        return cur.fetchone() is None


class order_no_in_wait_orders(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        cur.execute(f"SELECT * FROM wait_orders WHERE id_sel={message.from_user.id} and condition=0")
        return cur.fetchone() is None


class is_amount(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        amount = message.text.lower().split()
        if len(amount) == 1 and str.isdigit(amount[0]):
            amount = int(amount[0])
            cur.execute(f"SELECT score FROM sellers WHERE id_sel={message.from_user.id}")
            score = cur.fetchone()
            return score != None and score[0] >= amount >= config.min_amount_dring_up
        return False
