from datetime import timedelta

TOKEN_BUYERS = "YOUR TOKEN FOR BUYER"
TOKEN_SELLERS = "YOUR TOKEN FOR SELLER"
TOKEN_MODERATOR = "YOUR TOKEN FOR MODERATOR"

PAYMENTS_TOKEN = 'YOUR PAYMENTS TOKEN'


admin_id = []  # id for using moderator_bot

# management--------------------------------------------------------------------------------------------------
price_sellers = 0.9  # service cost coefficients
price_buyers = 1  # service cost coefficients

min_price_ya_kassa = 60
max_price_Ya_kassa = 1000

min_amount_dring_up = 100

reiting_ban = -5

interval_check = 60  # interval between check for manage database

limit_sel_complete = timedelta(hours=12)  # time for doing
limit_confirm_buy = timedelta(hours=12)  # time for confirm

disaster_time_sel = timedelta(hours=12)
disaster_time_buy = timedelta(hours=12)

ban_sleep = 60  # time between check

# Other-----------------------------------------------------------------------------------------------------------

# sticker for luck order
sticker_happy = ['CAACAgIAAxkBAAEG5HljoJYRddsyi3W60cxYNhIuaEzBTwACWQADrWW8FPS7RxeJ4S0JLAQ',
                 'CAACAgIAAxkBAAEG5H9joJZFHgil90P0X9a2-NuK2-Y6swACswsAAipQUUoso7YJ7GnT1iwE',
                 'CAACAgIAAxkBAAEG5IFjoJZegN8msQnJwZHkyJNJ-z-oPgACHQMAAladvQrFMjBk7XkPEywE']
len_sticker_happy = 3


# constantly function
async def get_reiting_seller(luck, unluck, skip, wrong, scam):
    return luck - unluck * 2 - 0.5 * skip - 0.5 * wrong - 10 * scam


async def get_reiting_buyer(luck, unluck, scam):
    return luck - unluck * 2 - 10 * scam
