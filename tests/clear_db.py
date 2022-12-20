import sqlite3
import time
from datetime import datetime, timedelta

conn = sqlite3.connect('../db/db.db')
cur = conn.cursor()


# cur.execute("DELETE FROM sellers")
# cur.execute("DELETE FROM buyers")
# cur.execute("DELETE FROM vip_sellers")
# cur.execute("DELETE FROM vip_sellers")
cur.execute("UPDATE buyers SET luck_buy = 100 WHERE id_buy = 860893686")
cur.execute("UPDATE sellers SET luck_sel = 100 WHERE id_sel = 860893686")
conn.commit()