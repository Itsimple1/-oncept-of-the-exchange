from datetime import timedelta

# TOKEN_BUYERS = "YOUR TOKEN FOR BUYER"
# TOKEN_SELLERS = "YOUR TOKEN FOR SELLER"
# TOKEN_MODERATOR = "YOUR TOKEN FOR MODERATOR"
#
# PAYMENTS_TOKEN = 'YOUR PAYMENTS TOKEN'

TOKEN_BUYERS = "5025951113:AAGwPq9CTUDMZ0G0Buak5r6svGU_dy6ulVc"
TOKEN_SELLERS = "5812803045:AAFYTFwR0donuWCIQe-WPIX1eij3Y13MBy8"
TOKEN_MODERATOR = "5927335689:AAFXvEnHaek8VJz61x5-ueYbCT-Pv9jLI6Y"

PAYMENTS_TOKEN = '381764678:TEST:44955'


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
