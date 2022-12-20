import sqlite3

conn = sqlite3.connect('../db/db.db')
cur = conn.cursor()


# order = (1, 12345, "89081685015", 10, 70, str(datetime.time(datetime.now()))[:-7])
# cur.execute("INSERT INTO ordersLot VALUES(?, ?, ?, ?, ?, ?);", order)
# conn.commit()
#cur.execute("UPDATE buyers SET score=1000000 WHERE id_buy = 860893686;")
#cur.execute("UPDATE sellers SET score=1000000 WHERE id_sel = 860893686;")
#conn.commit()
#cur.execute("DELETE FROM ordersGB")
#cur.execute("DELETE FROM waitGB")
#cur.execute("DELETE FROM ordersLot")
#cur.execute("DELETE FROM waitLot")
#cur.execute("DELETE FROM supportBuyers")
#cur.execute("DELETE FROM supportSellers")
#cur.execute("INSERT INTO vip_sellers (id_sel) VALUES(860893686);")
#cur.execute("INSERT INTO vip_buyers (id_buy) VALUES(860893686);")
#cur.execute(f"DELETE FROM block_users WHERE id={860893686}")
#cur.execute("DELETE FROM vip_sellers")
#cur.execute("INSERT INTO dring_up_complete VALUES(?, ?, ?);", (1, 860893686, 900))


print("ordersLot:")
cur.execute("SELECT * FROM ordersLot;")
print(cur.fetchall())


print("waitLot:")
cur.execute("SELECT * FROM waitLot;")
print(cur.fetchall())


print("problemLot:")
cur.execute("SELECT * FROM problemLot;")
print(cur.fetchall())

print("block_buyers:")
cur.execute("SELECT * FROM block_buyers;")
print(cur.fetchall())

print("block_sellers:")
cur.execute("SELECT * FROM block_sellers;")
print(cur.fetchall())

print("buyers:")
cur.execute("SELECT * FROM buyers;")
print(cur.fetchall())

print("sellers:")
cur.execute("SELECT * FROM sellers;")
print(cur.fetchall())

print("complete_orders_lot:")
cur.execute("SELECT * FROM complete_orders_lot;")
print(cur.fetchall())

print("dring_up:")
cur.execute("SELECT * FROM dring_up;")
print(cur.fetchall())

print("history_dring_up:")
cur.execute("SELECT * FROM history_dring_up;")
print(cur.fetchall())

print("history_orders:")
cur.execute("SELECT * FROM history_orders;")
print(cur.fetchall())

print("history_scam_from_sell_orders:")
cur.execute("SELECT * FROM history_scam_orders;")
print(cur.fetchall())

print("support_buy:")
cur.execute("SELECT * FROM supportBuyers;")
print(cur.fetchall())

print("support_sel:")
cur.execute("SELECT * FROM supportSellers;")
print(cur.fetchall())

print("server:")
cur.execute("SELECT * FROM server;")
print(cur.fetchall())

print("solve_problem_lot:")
cur.execute("SELECT * FROM solve_problem_lot;")
print(cur.fetchall())
conn.commit()