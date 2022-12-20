import config
import sqlite3

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()


# Moderator-------------------------------------------------------------------------------------------------------------
async def get_moderator_order():
    cur.execute("SELECT * FROM problem_orders LIMIT 1")
    return cur.fetchone()


async def move_to_solved_problem_orders(number, id_buy, link, count_price, price_buy, id_sel, price_sel, choose):
    cur.execute("INSERT INTO solve_problem_orders VALUES(?, ?, ?, ?, ?, ?, ?, ?);",
                (number, id_buy, link, count_price, price_buy, id_sel, price_sel, choose))
    cur.execute(f"DELETE FROM problem_orders WHERE number={number} and id_buy={id_buy} and id_sel={id_sel}")
    conn.commit()
    if choose == "buy":
        cur.execute("INSERT INTO history_scam_orders VALUES(?, ?, ?, ?, ?, ?, ?);",
                    (number, id_buy, link, count_price, price_buy, id_sel, price_sel))
        cur.execute(f"UPDATE buyers SET unluck_buy = unluck_buy - 1  WHERE id_buy={id_buy};")
        conn.commit()
        await buyer_add_money_and_luck_buy(id_buy, price_buy)
        await seller_scam(id_sel)
    else:
        await add_statistic(price_buy, price_sel)
        cur.execute("INSERT INTO history_orders VALUES(?, ?, ?, ?, ?, ?, ?);",
                    (number, id_buy, link, count_price, price_buy, id_sel, price_sel))
        cur.execute(f"UPDATE sellers SET unluck_sel = unluck_sel - 1  WHERE id_sel={id_sel};")
        conn.commit()
        await seller_add_money_and_luck_sell(id_sel, price_sel)
        await buyer_scam(id_buy)
    return cur.fetchone()


# ModeratorDringUp-----------------------------------------------------------------------------------------------------------
async def get_moderator_dring_up(id_moder):
    cur.execute("SELECT * FROM dring_up LIMIT 1")
    result = cur.fetchone()
    if result is not None:
        cur.execute(f"UPDATE dring_up SET id_moderator = {id_moder} WHERE number={result[0]} and id_sel={result[1]}")
        conn.commit()
        return result
    return result


async def get_history_orders(id_sel):
    cur.execute(f"SELECT number, id_sel, price_sel FROM history_orders WHERE id_sel={id_sel}")
    return cur.fetchall()


async def move_to_complete_dring_up(number, id_sel, amount, requisites, history_orders):
    cur.execute("INSERT INTO history_dring_up VALUES(?, ?, ?, ?);", (number, id_sel, amount, requisites))
    cur.execute(f"DELETE FROM dring_up WHERE number={number} and id_sel={id_sel}")
    conn.commit()
    for i in history_orders:
        cur.execute(f"DELETE FROM history_orders WHERE number={i[0]} and id_buy={i[1]} and id_sel={id_sel}")
    conn.commit()


# Statistics-------------------------------------------------------------------------------------------------------------
async def get_statistic_info():
    cur.execute("SELECT * FROM statistic")
    statistic = cur.fetchone()
    if statistic is not None:
        return f"Общее число продаж: {statistic[0]}\nСумма покупок: {statistic[1]}\nСумма продаж: {statistic[2]}\n" \
               f"Прибыльный оборот: {statistic[3]} "
    return "Возникла неизвестаня ошибка"


# Users------------------------------------------------------------------------------------------------------------------
async def dop_info_buy(id_buy):
    text_return = 'Информация о покупателе:\n'
    cur.execute(f"SELECT * FROM buyers WHERE id_buy = {id_buy}")
    data = cur.fetchone()
    text_return += f"👨‍💻Пользователь: {data[0]}\n📞Телефон: {data[2]}\n💰Баланс: {data[3]} рублей\n\n"
    text_return += f"Статистика аккаунта:\nУспешных покупок: {data[4]}\nНеудачных покупок: {data[5]}\nСкам: {data[6]}"
    return text_return


async def dop_info_sell(id_sel):
    text_return = 'Информация о продавце:\n'
    cur.execute(f"SELECT * FROM sellers WHERE id_sel = {id_sel}")
    data = cur.fetchone()
    text_return += f"👨‍💻Пользователь: {data[0]}\n📞Телефон: {data[2]}\n💰Баланс: {data[3]} рублей\n📈Рейтинг: " \
                   f"{await config.get_reiting_seller(data[4], data[5], data[6], data[7], data[8])}\n\n "
    text_return += f"Статистика аккаунта:\nУспешных продаж: {data[4]}\nНеудачных продаж: {data[5]}\nВсего пропусков: "\
                   f"{data[6]}\nОтмечено ошибок {data[7]}\nСкам: {data[8]} "
    return text_return


async def complete_ban_user(id):
    cur.execute(f"SELECT * FROM block_users WHERE id={id}")
    if cur.fetchone() is None:
        cur.execute(f"INSERT INTO block_users (id) VALUES({id});")
        cur.execute(f"UPDATE buyers SET ban=1 WHERE id_buy={id};")
        cur.execute(f"UPDATE sellers SET ban=1 WHERE id_sel={id};")
        conn.commit()


# Buyers----------------------------------------------------------------------------------------------------------------
async def buyer_add_money_and_luck_buy(id, money):
    cur.execute(f"UPDATE buyers SET luck_buy = luck_buy+1  WHERE id_buy={id};")
    cur.execute(f"UPDATE buyers SET score = score+{money}  WHERE id_buy={id};")
    conn.commit()


async def buyer_scam(id_buy):
    cur.execute(f"UPDATE buyers SET scam = scam + 1 WHERE id_buy={id_buy};")
    conn.commit()


# Sellers---------------------------------------------------------------------------------------------------------------
async def seller_add_money_and_luck_sell(id, money):
    cur.execute(f"UPDATE sellers SET score = score+{money}  WHERE id_sel={id};")
    cur.execute(f"UPDATE sellers SET luck_sel = luck_sel+1  WHERE id_sel={id};")
    conn.commit()


async def seller_scam(id_sel):
    cur.execute(f"UPDATE sellers SET scam = scam + 1 WHERE id_sel={id_sel};")
    conn.commit()


# Support----------------------------------------------------------------------------------------------------------------
async def get_support_request_buy():
    cur.execute("SELECT * FROM supportBuyers LIMIT 1")
    return cur.fetchone()


async def get_support_request_sel():
    cur.execute("SELECT * FROM supportSellers LIMIT 1")
    return cur.fetchone()


async def del_support_requerst_buy(number, id):
    cur.execute(f"DELETE FROM supportBuyers WHERE id_buy = {id} and number={number};")
    conn.commit()


async def del_support_requerst_sel(number, id):
    cur.execute(f"DELETE FROM supportSellers WHERE id_sel = {id} and number={number};")
    conn.commit()


# Statistic ------------------------------------------------------------------------------------
async def add_statistic(price_buy, price_sel):
    cur.execute("UPDATE statistic SET count_sell = count_sell + 1")
    cur.execute(f"UPDATE statistic SET amount_buy = amount_buy + {price_buy}")
    cur.execute(f"UPDATE statistic SET amount_sell = amount_sell + {price_sel}")
    cur.execute("UPDATE statistic SET turnover = amount_buy - amount_sell")
    conn.commit()


if __name__ == "__main__":
    pass
