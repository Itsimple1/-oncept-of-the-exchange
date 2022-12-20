import asyncio
import datetime
import sqlite3
import time
import random

import bot_buyers
import bot_sellers
import config
import api_db

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()


async def init_check_state():
    cur.execute("SELECT * FROM wait_orders WHERE condition=0")
    lines = cur.fetchall()
    time_disaster = str(datetime.datetime.now() + config.disaster_time_sel)[:-7]
    for line in lines:
        await bot_buyers.send_message_to_buyer(line[1],
                                               f'🤖Сервер был перезапущен. У продавца есть '
                                               f'{config.disaster_time_sel} на выполнение вашего заказа')
        await bot_sellers.send_message_to_seller(line[5],
                                                 f'🤖Сервер был перезапущен. У вас есть {config.disaster_time_sel}'
                                                 f' на выполнение заказа')
        cur.execute(f"UPDATE wait_orders SET time = '{time_disaster}' WHERE number={line[0]} and id_buy = {line[1]};")
        conn.commit()
    cur.execute("SELECT * FROM wait_orders WHERE condition=1")
    lines = cur.fetchall()
    time_disaster = str(datetime.datetime.now() + config.disaster_time_buy)[:-7]
    for line in lines:
        await bot_buyers.send_message_to_buyer(line[1],
                                               f'🤖Сервер был перезапущен. У вас есть {config.disaster_time_buy}'
                                               f' чтобы подтвердить выполнение заказа')
        cur.execute(f"UPDATE wait_orders SET time = '{time_disaster}' WHERE number={line[0]} and id_buy = {line[1]};")
        conn.commit()


async def add_skip_order_seller(id_seller):
    cur.execute(f"SELECT * FROM sellers WHERE id_sel={id_seller}")
    if cur.fetchone() is not None:
        cur.execute(f"UPDATE sellers SET skip_sel=skip_sel+1 WHERE id_sel={id_seller}")
        conn.commit()


async def move_wait_to_order_time(number, id_buyer, link, price, price_buyer, id_seller):
    cur.execute(f"SELECT * FROM wait_orders WHERE number={number} and id_buy={id_buyer}")
    if cur.fetchone()[0]:
        await bot_buyers.send_message_to_buyer(id_buyer,
                                               'Время выполнения заказа для продавца вышло. Ваш заказ перемещен '
                                               'в лист ожидания')
        await bot_sellers.send_message_to_seller(id_seller,
                                                 'Время выполнения вышло\nЧтобы продолжить пользоваться ботом '
                                                 'нажмите любую кнопку')
        cur.execute(f"DELETE FROM wait_orders WHERE number={number} and id_buy={id_buyer}")
        cur.execute("INSERT INTO orders_orders VALUES(?, ?, ?, ?, ?);", (number, id_buyer, link, price, price_buyer))
        conn.commit()
        await add_skip_order_seller(id_seller)


async def move_wait_to_history_orders(number, id_buyer):
    cur.execute(f"SELECT * FROM wait_orders WHERE number={number} and id_buy={id_buyer}")
    if cur.fetchone()[0]:
        await bot_buyers.send_message_to_buyer(id_buyer, 'Время подтверждения выполнения вышло')
        await api_db.sql_bd_buyers.move_wait_to_history(number, id_buyer)


async def check_time_in_wait():
    time_now = str(datetime.datetime.now())[:-7]
    time_now = datetime.datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S")
    cur.execute("SELECT * FROM wait_orders WHERE condition=0")
    result = cur.fetchall()
    if len(result) > 0:
        for i in result:
            time_order = i[8]
            time_order = datetime.datetime.strptime(time_order, "%Y-%m-%d %H:%M:%S")
            if time_now > time_order:
                await move_wait_to_order_time(i[0], i[1], i[2], i[3], i[4], i[5])

    time_now = str(datetime.datetime.now())[:-7]
    time_now = datetime.datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S")
    cur.execute("SELECT * FROM wait_orders WHERE condition=1")
    result = cur.fetchall()
    if len(result) > 0:
        for i in result:
            time_order = i[8]
            time_order = datetime.datetime.strptime(time_order, "%Y-%m-%d %H:%M:%S")
            if time_now > time_order:
                await move_wait_to_history_orders(i[0], i[1])


async def check_complete_order():
    cur.execute("SELECT * FROM complete_orders")
    lines = cur.fetchall()
    for line in lines:
        if line[6] == 'ok':
            await bot_sellers.send_message_to_seller(line[4],
                                                     f"Заказ (на {line[2]}руб) подтвержден"
                                                     f" пользователем\nНа ваш счет зачислено {line[5]}руб\n"
                                                     f"Спасибо за выполнение❤")
            code = config.sticker_happy[random.randint(0, config.len_sticker_happy - 1)]
            await bot_sellers.send_sticker_to_seller(line[4], code)
            cur.execute(f"DELETE FROM complete_orders WHERE number={line[0]} and id_buy={line[1]}")
            conn.commit()
    cur.execute("SELECT * FROM solve_problem_orders")
    lines = cur.fetchall()
    for line in lines:
        if line[7] == 'buy':
            await bot_buyers.send_message_to_buyer(line[1],
                                                   f"По вашему заказу (на сумму {line[4]}руб) "
                                                   f"модератор подтвердил обман со стороны продавца\nНа ваш счет были "
                                                   f"возварщены деньги {line[4]}руб\nПросим прощения за "
                                                   f"доставленные неудобства")
            await bot_sellers.send_message_to_seller(line[5],
                                                     f"В заказе (на сумму {line[6]}руб) "
                                                     f"возникли проблемы\nМодератор "
                                                     f"вынес решение в пользу покупателя. Вам вынесено "
                                                     f"предупреждение. Если ваш рейтинг опуститься ниже "
                                                     f"{config.reiting_ban}, вас забанят🙁")
        elif line[7] == 'sell':
            await bot_buyers.send_message_to_buyer(line[1],
                                                   f"По вашему заказу (на сумму {line[4]}руб) "
                                                   f"модератор отметил, что лот был выкуплен\nВам вынесено "
                                                   f"предупреждение. Если ваш рейтинг опуститься ниже "
                                                   f"{config.reiting_ban}, вас забанят🙁")
            await bot_sellers.send_message_to_seller(line[5],
                                                     f"Заказ (на сумму{line[3]}руб) подтвержден")
            code = config.sticker_happy[random.randint(0, config.len_sticker_happy - 1)]
            await bot_sellers.send_sticker_to_seller(line[5], code)
        cur.execute(f"DELETE FROM solve_problem_orders WHERE number={line[0]} and id_buy={line[1]}")
        conn.commit()


async def ban_in_real_time():
    cur.execute("SELECT * FROM buyers;")
    for i in cur.fetchall():
        if await api_db.sql_bd_buyers.get_rating_buyer(i[4], i[5], i[6]) <= config.reiting_ban:
            await api_db.sql_bd_buyers.complete_ban_buyer(i[1])
        else:
            await api_db.sql_bd_buyers.unlock_buyer(i[1])
    cur.execute("SELECT * FROM sellers;")
    for i in cur.fetchall():
        if await api_db.sql_bd_sellers.get_reiting_seller(i[4], i[5], i[6], i[7], i[8]) <= config.reiting_ban:
            await api_db.sql_bd_buyers.complete_ban_seller(i[1])
        else:
            await api_db.sql_bd_buyers.unlock_seller(i[1])


async def main():
    await init_check_state()
    while True:
        await check_time_in_wait()
        await check_complete_order()
        await ban_in_real_time()
        time.sleep(config.interval_check)


if __name__ == "__main__":
    asyncio.run(main())
