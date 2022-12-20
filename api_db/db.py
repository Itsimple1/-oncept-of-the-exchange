import sqlite3

conn = sqlite3.connect('../db/db.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS buyers(
   name TEXT, 
   id_buy INT PRIMARY KEY,
   tel TEXT,
   score INT,
   luck_buy INT,
   unluck_buy INT,
   scam INT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS sellers(
   name Text, 
   id_sel INT PRIMARY KEY,
   tel TEXT,
   score INT,
   luck_sel INT,
   unluck_sel INT,
   skip_sel INT,
   wrong INT,
   scam INT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS orders(
   number INT,
   id_buy INT,
   link TEXT,
   price INT,
   price_buy INT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS wait_orders(
    number INT,
   id_buy INT,
   link TEXT,
   count INT,
   price_buy INT,
   id_sel INT,
   price_sel INT,
   condition INT,
   time TEXT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS problem_orders(
    number INT,
   id_buy INT,
   link TEXT,
   count INT,
   price_buy INT,
   id_sel INT,
   price_sel INT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS solve_problem_orders(
    number INT,
   id_buy INT,
   link TEXT,
   count INT,
   price_buy INT,
   id_sel INT,
   price_sel INT,
   verdict TEXT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS supportBuyers(
   number INT,
   id_buy INT,
   request TEXT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS supportSellers(
   number INT,
   id_sel INT,
   request TEXT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS vip_sellers(
   id_sel INT PRIMARY KEY);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS block_buyers(
   id INT PRIMARY KEY);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS block_sellers(
   id INT PRIMARY KEY);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS complete_orders(
   number INT, 
   id_buy INT,
   price_lot INT,
   price_buy INT,
   id_sel INT,
   price_sel INT,
   verdict TEXT);
""")

cur.execute("""CREATE TABLE IF NOT EXISTS dring_up(
   number INT,
   id_sel INT,
   amount INT,
   requisites TEXT,
   id_moderator INT);
""")

cur.execute("""CREATE TABLE IF NOT EXISTS history_dring_up(
   number INT,
   id_sel INT,
   amount INT,
   requisites TEXT);
""")

cur.execute("""CREATE TABLE IF NOT EXISTS history_orders(
   number INT, 
   id_buy INT,
   link INT,
   price_lot INT,
   price_buy INT,
   id_sel INT,
   price_sel INT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS history_scam_orders(
   number INT, 
   id_buy INT,
   link INT,
   price_lot INT,
   price_buy INT,
   id_sel INT,
   price_sel INT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS statistic(
   count_sell INT,
   amount_buy INT,
   amount_sell INT,
   turnover INT);
""")
cur.execute("""CREATE TABLE IF NOT EXISTS server(
   condition_work INT);
""")
cur.execute("INSERT INTO statistic VALUES(?, ?, ?, ?);", (0, 0, 0, 0))
cur.execute("INSERT INTO server (condition_work) VALUES(1);")
conn.commit()


