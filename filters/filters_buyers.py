from aiogram.dispatcher.filters import BaseFilter
from aiogram.types import Message
import re

import config


def is_phone_number(txt):
    if bool(re.match('8\d{10}$', txt)):
        return True
    return False


class input_gb_filter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        input_data = message.text.lower().split()
        if len(input_data) == 2 and str.isdigit(input_data[1]):
            count = int(input_data[1])
            return 0 < count <= 30 and is_phone_number(input_data[0])
        return False


class is_username(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        username = message.text.lower().split()
        if len(username) == 1:
            return bool(re.match('@.+', username[0]))
        return False


class is_price_order(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        input_data = message.text.lower().split()
        if len(input_data) == 1 and str.isdigit(input_data[0]):
            price = int(input_data[0])
            return 40 <= price < 3000
        return False


class is_price_top_up(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        input_data = message.text.lower().split()
        if len(input_data) == 1 and str.isdigit(input_data[0]):
            price = int(input_data[0])
            return config.min_price_ya_kassa <= price <= config.max_price_Ya_kassa
        return False


class is_link(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        input_data = message.text.lower().split()
        return len(input_data) == 1


class is_telephone_number(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        input_data = message.text.lower().split()
        if len(input_data) == 1 and is_phone_number(input_data[0]):
            return True
        return False


class is_promo(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        input_data = message.text.lower()
        return str.isdigit(input_data) and 4 < len(input_data) < 15
