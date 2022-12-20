import subprocess
import sqlite3

conn = sqlite3.connect('db/db.db')
cur = conn.cursor()


def stop_server():
    cur.execute("UPDATE server SET condition_work=0;")
    conn.commit()
    print("server stoped\n")


def add_vip_seller(id_sel):
    cur.execute("INSERT INTO vip_sellers VALUES(id);", id_sel)
    conn.commit()
    print(f"user {id_sel} added in vip user\n")


def complete_ban_buyer(id_buy):
    cur.execute(f"SELECT * FROM block_buyers WHERE id={id_buy}")
    if cur.fetchone() is None:
        cur.execute(f"INSERT INTO block_buyers (id) VALUES({id_buy});")
        conn.commit()
        print(f"user {id_buy} added in block\n")


def complete_ban_seller(id_sel):
    cur.execute(f"SELECT * FROM block_sellers WHERE id={id_sel}")
    if cur.fetchone() is None:
        cur.execute(f"INSERT INTO block_sellers (id) VALUES({id_sel});")
        conn.commit()
        print(f"user {id_sel} added in block\n")


def get_statistic_info():
    cur.execute("SELECT * FROM statistic")
    statistic = cur.fetchone()
    if statistic is not None:
        return f"Общее число продаж: {statistic[0]}\nСумма покупок: {statistic[1]}\nСумма продаж: {statistic[2]}\n" \
               f"Прибыльный оборот: {statistic[3]}\n "
    return "Возникла неизвестаня ошибка\n"


print('server')

files = ["bot_buyers.py", "bot_sellers.py", "moderator_bot.py",
         "main_proverka_order.py"]
for file in files:
    subprocess.Popen(args=["start", "python", file], shell=True, stdout=subprocess.PIPE)

cur.execute("UPDATE server SET condition_work=1;")
conn.commit()

while True:
    command = input()
    if command == "stop_server":
        stop_server()
    elif "add_vip_user" in command:
        id = command.split()[1]
        if str.isdigit(id):
            add_vip_seller(id)
    elif "ban_buyer" in command:
        id = command.split()[1]
        if str.isdigit(id):
            complete_ban_buyer(id)
    elif "ban_seller" in command:
        id = command.split()[1]
        if str.isdigit(id):
            complete_ban_seller(id)
    elif command == "statistic":
        print(get_statistic_info())
    else:
        print("Неизвестная команда")
