import sqlite3

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()

num_problem_orders = 0
num_support_buyers = 0
num_history_orders = 0

num_orders = [i for i in range(10000, 0, -1)]


# Main database api -------------------------------------------------------------------------
async def start_bd_api():
    global num_orders
    print("Start database")
    cur.execute("SELECT number FROM orders;")
    one_table = cur.fetchall()
    for i in one_table:
        del num_orders[-i[0]]
    cur.execute("SELECT number FROM wait_orders;")
    one_table = cur.fetchall()
    for i in one_table:
        del num_orders[-i[0]]


# Manage Orders --------------------------------------------------------------------------
async def add_orders(id_buy, link, count, price):
    global num_orders
    per_num = num_orders[-1]
    cur.execute("INSERT INTO orders VALUES(?, ?, ?, ?, ?);", (per_num, id_buy, link, count, price))
    conn.commit()
    # print("add_orderst: Orders has added\n")
    return per_num


async def check_order_no_dell_one(number, id_buy):
    cur.execute(f"SELECT * FROM orders WHERE id_buy={id_buy} and number={number};")
    result = cur.fetchall()
    if len(result) > 0:
        return True
    return False


async def check_wait_orders(number, id_buy):
    cur.execute(f"SELECT * FROM wait_orders WHERE number={number} and id_buy={id_buy};")
    result = cur.fetchone()
    if result is not None:
        cur.execute(f"DELETE FROM wait_orders WHERE number={number} and id_buy={id_buy}")
        conn.commit()
        return 1, result
    return 0, 0


async def check_order_in_wait_no_del_cond_0(number, id_buy):
    cur.execute(f"SELECT * FROM wait_orders WHERE number={number} and id_buy={id_buy} and condition=0;")
    return cur.fetchone() is not None


async def check_order_in_wait_no_del_cond_1(number, id_buy):
    cur.execute(f"SELECT * FROM wait_orders WHERE number={number} and id_buy={id_buy} and condition=1;")
    return cur.fetchone() is not None


async def move_wait_to_history(num, id_buyer):
    global num_orders, num_history_orders
    cur.execute(f"SELECT * FROM wait_orders WHERE id_buy={id_buyer} and condition=1 and number = {num}")
    result = cur.fetchone()
    if result is not None:
        await add_statistic(result[4], result[6])
        result = result
        cur.execute(f"DELETE FROM wait_orders WHERE id_buy={id_buyer} and number = {num}")
        cur.execute(f"INSERT INTO complete_orders VALUES(?, ?, ?, ?, ?, ?, ?);",
                    (result[0], result[1], result[3], result[4], result[5], result[6], 'ok'))
        cur.execute(f"INSERT INTO history_orders VALUES(?, ?, ?, ?, ?, ?, ?);",
                    (num_history_orders, result[1], result[2], result[3], result[4], result[5], result[6]))
        conn.commit()
        await seller_add_money_and_luck_sell(result[5], result[6])
        num_orders.append(result[0])


async def move_wait_to_problem_orders(num, id_buyer):
    global num_orders, num_problem
    cur.execute(f"SELECT * FROM wait_orders WHERE id_buy={id_buyer} and condition=1 and number={num}")
    result = cur.fetchone()
    if result is not None:
        cur.execute(f"DELETE FROM wait_orders WHERE id_buy={id_buyer} and number={num}")
        cur.execute(f"INSERT INTO problem_orders VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (num_problem, result[1], result[2], result[3], result[4], result[5], result[6]))
        await seller_unluck_sell(result[5])
        await buyer_unluck_buy(id_buyer)
        conn.commit()
        num_problem += 1
        num_orders.append(result[0])


# DATA USERS --------------------------------------------------------------------------------
async def get_ban_user():
    cur.execute("SELECT * FROM block_users")
    return cur.fetchall()


# BUYERS----------------------------------------------------------------------------------------------------------------
async def add_buyer(id_buy, name):
    if name is None:
        name = '(username отсутствует)'
    cur.execute(f"SELECT * FROM buyers WHERE id_buy={id_buy};")
    if cur.fetchone() is None:
        cur.execute("INSERT INTO buyers VALUES(?, ?, ?, ?, ?, ?, ?);", ("@" + name, id_buy, '-', 0, 0, 0, 0))
        conn.commit()


async def complete_ban_buyer(id_buy):
    cur.execute(f"SELECT * FROM block_buyers WHERE id={id_buy}")
    if cur.fetchone() is None:
        cur.execute(f"INSERT INTO block_buyers (id) VALUES({id_buy});")
        conn.commit()


async def unlock_buyer(id_buy):
    cur.execute(f"SELECT * FROM block_buyers WHERE id={id_buy}")
    if cur.fetchone() is not None:
        cur.execute(f"DELETE FROM block_buyers WHERE id = {id_buy};")
        conn.commit()


async def is_ban_buyer(id_buy):
    cur.execute(f"SELECT * FROM block_buyers WHERE id={id_buy}")
    return cur.fetchone() is not None


async def buyer_add_tel(id_buy, tel):
    cur.execute(f"UPDATE buyers SET tel = {tel}  WHERE id_buy={id_buy};")
    conn.commit()


async def buyer_change_username(id_buy, username):
    cur.execute(f"UPDATE buyers SET name = '{username}' WHERE id_buy={id_buy};")
    conn.commit()


async def get_rating_buyer(luck, unluck, scam):
    return luck - unluck * 2 - 10 * scam


async def get_vip_buyers():
    cur.execute("SELECT * FROM vip_buyers")
    return cur.fetchall()


async def get_inform_about_my_account_buyer(id_buy):
    cur.execute(f"SELECT * FROM buyers WHERE id_buy={id_buy};")
    return cur.fetchone()


async def get_buyer_tel(id_buyer):
    cur.execute(f"SELECT tel FROM buyers WHERE id_buy={id_buyer};")
    return cur.fetchone()[0]


async def buyer_luck_buy(id_buy):
    cur.execute(f"UPDATE buyers SET luck_buy = luck_buy+1  WHERE id_buy={id_buy};")
    conn.commit()


async def buyer_add_money(id_buy, money):
    cur.execute(f"UPDATE buyers SET score = score+{money}  WHERE id_buy={id_buy};")
    conn.commit()


async def buyer_add_money_and_luck_buy(id_buy, money):
    cur.execute(f"UPDATE buyers SET luck_buy = luck_buy+1  WHERE id_buy={id_buy};")
    cur.execute(f"UPDATE buyers SET score = score+{money}  WHERE id_buy={id_buy};")
    conn.commit()


async def buyer_unluck_buy(id_buy):
    cur.execute(f"UPDATE buyers SET unluck_buy = unluck_buy + 1  WHERE id_buy={id_buy};")
    conn.commit()


async def buyer_use_with_score(id_buy, money):
    cur.execute(f"SELECT score FROM buyers WHERE id_buy={id_buy};")
    result = cur.fetchone()
    if result and result[0] >= money:
        cur.execute(f"UPDATE buyers SET score = {result[0] - money} WHERE id_buy = {id_buy}")
        conn.commit()
        # print("pay with score")
        return result, result[0] - money
    return 0, result[0]


async def check_buyer(id_buy):
    cur.execute(f"SELECT * FROM buyers WHERE id_buy={id_buy};")
    return cur.fetchone() is None


# SELLERS---------------------------------------------------------------------------------------------------------------
async def complete_ban_seller(id_sel):
    cur.execute(f"SELECT * FROM block_sellers WHERE id={id_sel}")
    if cur.fetchone() is None:
        cur.execute(f"INSERT INTO block_sellers (id) VALUES({id_sel});")
        conn.commit()


async def unlock_seller(id_sel):
    cur.execute(f"SELECT * FROM block_sellers WHERE id={id_sel}")
    if cur.fetchone() is not None:
        cur.execute(f"DELETE FROM block_sellers WHERE id = {id_sel};")
        conn.commit()


async def is_ban_seller(id_sel):
    cur.execute(f"SELECT * FROM block_sellers WHERE id={id_sel}")
    return cur.fetchone() is not None


async def seller_add_money(id_sel, money):
    cur.execute(f"UPDATE sellers SET score = score+{money}  WHERE id_sel={id_sel};")
    conn.commit()


async def seller_add_money_and_luck_sell(id, money):
    cur.execute(f"UPDATE sellers SET score = score+{money}  WHERE id_sel={id};")
    cur.execute(f"UPDATE sellers SET luck_sel = luck_sel+1  WHERE id_sel={id};")
    conn.commit()


async def seller_luck_sell(id):
    cur.execute(f"UPDATE sellers SET luck_sel = luck_sel+1  WHERE id_sel={id};")
    conn.commit()


async def seller_unluck_sell(id):
    cur.execute(f"UPDATE sellers SET unluck_sel = unluck_sel+1 WHERE id_sel={id};")
    conn.commit()


# Support ------------------------------------------------------------------------------------
async def add_support_cause_buyers(id, text):
    global num_support_buyers
    cur.execute("INSERT INTO supportBuyers VALUES(?, ?, ?);", (num_support_buyers, id, text))
    num_support_buyers += 1
    conn.commit()
    # print("add_support: support_cause has added")


# Statistic ------------------------------------------------------------------------------------
async def add_statistic(price_buy, price_sel):
    cur.execute("UPDATE statistic SET count_sell = count_sell + 1")
    cur.execute(f"UPDATE statistic SET amount_buy = amount_buy + {price_buy}")
    cur.execute(f"UPDATE statistic SET amount_sell = amount_sell + {price_sel}")
    cur.execute("UPDATE statistic SET turnover = amount_buy - amount_sell")
    conn.commit()


# Server--------------------------------------------------------------------------------------
async def server_is_work():
    cur.execute("SELECT condition_work FROM server")
    return cur.fetchone()[0]
