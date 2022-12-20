import sqlite3
from datetime import datetime

import bot_buyers
import config
import api_db.sql_bd_buyers

num_dring_up = 0
num_support_sellers = 0

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()


# Manage Orders ----------------------------------------------------------------------------------------------------
async def return_orders_for_sellers(id_seller):
    text_return = ''
    cur.execute("SELECT * FROM orders LIMIT 50;")
    result = cur.fetchall()
    if await is_vip_seller(id_seller):
        for line in result:
            text_return += str(line[0]).ljust(13) + str(line[3]).ljust(14) + str(line[4]) + '\n'
    else:
        for line in result:
            text_return += str(line[0]).ljust(13) + str(line[3]).ljust(14) + str(
                int(config.price_sellers * int(line[3]))) + '\n'
    return text_return


async def check_order_no_dell(number):
    cur.execute(f"SELECT * FROM orders WHERE number={number};")
    result = cur.fetchone()
    if result is not None:
        return 1, result
    return 0, 0


async def move_order_to_wait(number, id_buy, link, count, price_buyer, id_seller, price_seller):
    cur.execute(f"SELECT * FROM orders WHERE number={number} and id_buy={id_buy}")
    if cur.fetchone() is not None:
        time_complete = str(datetime.now() + config.limit_sel_complete)[:-7]
        await bot_buyers.send_message_to_buyer(id_buy, 'Ваш заказ принят к исполнению')
        cur.execute(f"DELETE FROM orders WHERE number={number} and id_buy={id_buy}")
        conn.commit()
        cur.execute("INSERT INTO wait_orders VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    (number, id_buy, link, count, price_buyer, id_seller, price_seller, 0, time_complete))
        conn.commit()
        return True
    return False


async def make_condition_complete(number, id_buy):
    cur.execute(f"SELECT * FROM wait_orders WHERE id_buy = {id_buy} and number={number};")
    if cur.fetchall() is not None:
        time_confirmation = str(datetime.now() + config.limit_confirm_buy)[:-7]
        await bot_buyers.send_message_to_buyer(id_buy,
                                'Продавец отметил, что ваш заказ выполнен\nПодтвердите, что лот куплен или не выкуплен')
        cur.execute(f"UPDATE wait_orders SET condition=1 WHERE id_buy = {id_buy} and number={number};")
        cur.execute(f"UPDATE wait_orders SET time = '{time_confirmation}' WHERE id_buy = {id_buy} and number={number};")
        conn.commit()


async def move_wait_to_order(number, id_buyer, link, count, price_buyer):
    cur.execute(f"SELECT * FROM wait_orders WHERE number={number} and id_buy={id_buyer}")
    if cur.fetchone() != None:
        await bot_buyers.send_message_to_buyer(id_buyer,
                                'Продавец отказался от выполнения вашего заказа.\nВаш заказ перемещен в лист ожидания')
        cur.execute(f"DELETE FROM wait_orders WHERE number={number} and id_buy={id_buyer}")
        conn.commit()
        cur.execute("INSERT INTO orders VALUES(?, ?, ?, ?, ?);", (number, id_buyer, link, count, price_buyer))
        conn.commit()
        return True
    return False


async def move_wait_to_wrong(number, id_buyer, price_buy):
    cur.execute(f"SELECT * FROM wait_orders WHERE number={number} and id_buy={id_buyer}")
    if cur.fetchone() != None:
        api_db.sql_bd_buyers.num_orders.append(number)
        await bot_buyers.send_message_to_buyer(id_buyer,
                            'Продавец отметил что в вашем заказе ошибка.\nДеньги за этот заказ вернулись к вам на '
                             'счет.\nПроверьте правильность номера, а также отсутсвие полученного ранее пакета ГБ\nДля '
                             'продолжения просто выберите любую команду')
        await buyer_add_money(id_buyer, price_buy)
        cur.execute(f"DELETE FROM wait_orders WHERE number={number} and id_buy={id_buyer}")
        conn.commit()
        return True
    return False


# DATA USERS -----------------------------------------------------------------------------------------------------------
# SELLERS
async def add_seller(id, name):
    if name is None:
        name = '(username отсутствует)'
    cur.execute(f"SELECT * FROM sellers WHERE id_sel={id};")
    if cur.fetchone() is None:
        cur.execute("INSERT INTO sellers VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", ("@" + name, id, '-', 0, 0, 0, 0, 0, 0))
        conn.commit()


async def seller_add_tel(id, tel):
    cur.execute(f"UPDATE sellers SET tel = {tel}  WHERE id_sel={id};")
    conn.commit()


async def seller_change_username(id_sel, username):
    cur.execute(f"UPDATE sellers SET name = '{username}' WHERE id_sel={id_sel};")
    conn.commit()


async def note_promo_seller(id_seller, promo):
    if id_seller == promo:
        return False
    cur.execute(f"SELECT vip_score FROM sellers WHERE id_sel={id_seller};")
    if cur.fetchone()[0] < 1000:
        cur.execute(f"SELECT id_sel FROM sellers WHERE id_sel={promo};")
        if cur.fetchone()[0] is not None:
            cur.execute(f"UPDATE sellers SET promo = {promo} WHERE id_sel={id_seller};")
            cur.execute(f"UPDATE sellers SET vip_score = vip_score+1 WHERE id_sel={id_seller};")
            cur.execute(f"UPDATE sellers SET vip_score = vip_score+1 WHERE id_sel={promo}")
            cur.execute(f"UPDATE sellers SET count_ref = count_ref+1 WHERE id_sel={promo}")
            conn.commit()
            return True
        cur.execute(f"SELECT id_buy FROM buyers WHERE id_buy={promo};")
        if cur.fetchone()[0] is not None:
            cur.execute(f"UPDATE sellers SET promo = {promo} WHERE id_sel={id_seller};")
            cur.execute(f"UPDATE sellers SET vip_score = vip_score+1 WHERE id_sel={id_seller};")
            cur.execute(f"UPDATE buyers SET vip_score = vip_score+1 WHERE id_buy={promo}")
            cur.execute(f"UPDATE buyers SET count_ref = count_ref+1 WHERE id_sel={promo}")
            conn.commit()
            return True
    return False


async def dring_up(id_seller, amount, requisites):
    global num_dring_up
    cur.execute(f"SELECT score FROM sellers WHERE id_sel={id_seller}")
    score = cur.fetchone()
    if score is not None and score[0] >= amount:
        cur.execute(f"UPDATE sellers SET score = score - {amount} WHERE id_sel={id_seller};")
        cur.execute(f"INSERT INTO dring_up VALUES(?, ?, ?, ?, ?);", (num_dring_up, id_seller, amount, requisites, 0))
        num_dring_up += 1
        conn.commit()
        return True
    return False


async def get_reiting_seller(luck, unluck, skip, wrong, scam):
    return luck - unluck * 2 - 0.5 * skip - 0.3 * wrong - 10 * scam


async def get_num_dring_up():
    cur.execute("SELECT number FROM dring_up;")
    return cur.fetchall()


async def get_inform_about_my_account_seller(id):
    cur.execute(f"SELECT * FROM sellers WHERE id_sel={id};")
    return cur.fetchone()


async def get_seller_count_score(id):
    cur.execute(f"SELECT score FROM sellers WHERE id_sel={id}")
    return cur.fetchone()[0]


async def get_seller_count_luck_buy(id):
    cur.execute(f"SELECT luck_buy FROM sellers WHERE id_sel={id}")
    return cur.fetchone()[0]


async def get_seller_tel(id):
    cur.execute(f"SELECT tel FROM sellers WHERE id_sel={id};")
    return cur.fetchone()[0]


async def get_dring_ups(id_seller):
    text = ''
    cur.execute(f"SELECT * FROM dring_up WHERE id_sel={id_seller};")
    for i in cur.fetchall():
        text += f"№{i[0]}             {i[2]}       в обработке\n"
    cur.execute(f"SELECT * FROM history_dring_up WHERE id_sel={id_seller};")
    for i in cur.fetchall():
        text += f"№{i[0]}             {i[2]}       выполнено\n"
    if text != '':
        return "Выплата  Сумма  Состояние\n" + text
    else:
        return "У вас нет выплат"


async def seller_luck_sell(id):
    cur.execute(f"UPDATE sellers SET luck_sel = luck_sel+1  WHERE id_sel={id};")
    conn.commit()


async def seller_unluck_sell(id):
    cur.execute(f"UPDATE sellers SET unluck_sel = unluck_sel+1 WHERE id_sel={id};")
    conn.commit()


async def seller_skip_sell(id):
    cur.execute(f"UPDATE sellers SET skip_sel = skip_sel+1 WHERE id_sel={id};")
    conn.commit()


async def seller_add_money(id, money):
    cur.execute(f"UPDATE sellers SET score = score+{money}  WHERE id_sel={id};")
    conn.commit()


async def seller_add_money_and_luck_buy(id, money):
    cur.execute(f"UPDATE sellers SET score = score+{money} WHERE id_sel={id};")
    cur.execute(f"UPDATE sellers SET luck_sel = luck_sel+1 WHERE id_sel={id};")
    conn.commit()


async def is_vip_seller(id_seller):
    cur.execute(f"SELECT * FROM vip_sellers WHERE id_sel={id_seller};")
    return cur.fetchone() is not None


async def check_seller(id_sel):
    cur.execute(f"SELECT * FROM sellers WHERE id_sel={id_sel};")
    return cur.fetchone() is None


# BUYERS--------------------------------------------------------------------------------------
async def buyer_add_money(id, money):
    cur.execute(f"UPDATE buyers SET score = score+{money} WHERE id_buy={id};")
    conn.commit()


# Support ------------------------------------------------------------------------------------
async def add_support_cause_seller(id, text):
    global num_support_sellers
    cur.execute("INSERT INTO supportSellers VALUES(?, ?, ?);", (num_support_sellers, id, text))
    num_support_sellers += 1
    conn.commit()


# Server--------------------------------------------------------------------------------------
async def server_is_work():
    cur.execute("SELECT condition_work FROM server")
    return cur.fetchone()[0]


if __name__ == "__main__":
    pass
