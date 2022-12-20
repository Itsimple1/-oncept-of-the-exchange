from aiogram import Router, types
from aiogram.types import Message
from aiogram.types.message import ContentType
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
import api_db.sql_bd_buyers
from filters.filters_buyers import is_price_top_up
import config

router = Router()


class Top_up(StatesGroup):
    wait_input_values = State()
    confirm_input_values = State()
    wait_confirm_paid = State()


@router.message(Top_up.wait_input_values, Text(text="🙁Отмена пополнения🙁", text_ignore_case=True))
async def back_top_up(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Пополнение отменено", reply_markup=keyboard)


@router.message(Top_up.wait_input_values, is_price_top_up())
async def check_price_top_up(message: Message, state: FSMContext):
    await state.set_state(Top_up.confirm_input_values)
    await state.update_data(price=int(message.text.lower().replace(" ", "")))
    kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="🔃Неверная сумма🔃"),
           types.KeyboardButton(text="🙁Отмена пополнения🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer("Подтвердите правильность суммы пополнения", reply_markup=keyboard)


@router.message(Top_up.wait_input_values)
async def unidentified_top_up(message: Message):
    await message.answer(
        f'Вы ввели неправильную сумму пополнения. Введите сумму от {config.min_price_ya_kassa} до "\
        f"{config.max_price_Ya_kassa} целым числом')


@router.message(Top_up.confirm_input_values, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_input_values(message: Message, state: FSMContext):
    await state.set_state(Top_up.wait_confirm_paid)
    if config.PAYMENTS_TOKEN.split(':')[1] == "TEST":
        await message.answer("Тестовый платеж!!!")
    kb = [[types.KeyboardButton(text="🙁Отмена пополнения🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    data = await state.get_data()
    await message.answer("Тестовый платеж!!!")
    PRICE = types.LabeledPrice(label="ГБ", amount=data['price'] * 100)  # в копейках
    await message.answer_invoice(title='Пополнение счета', description='Пополнение счета',
                                 provider_token=config.PAYMENTS_TOKEN, currency="rub",
                                 # photo_url = "https://yandex.ru/images/search?text=%D0%BE%D1%87%D0%B5%D0%BD%D1%8C
                                 # %20%D0%BA%D1%80%D0%B0%D1%81%D0%B8%D0%B2%D1%8B%D0%B5%D0%B7%D0%B5%D0%BC%D0%BB%D0%B8
                                 # &from=tabbar&pos=11&img_url=http%3A%2F%2Fmota.ru%2Fupload%2Fwallpapers%2Fsource
                                 # %2F2014%2F06%2F08%2F13%2F00%2F40404%2F51.jpg&rpt=simage&lr=47", photo_width = 416,
                                 # photo_height= 234, photo_size = 416,
                                 is_flexible=False,
                                 prices=[PRICE],
                                 start_parameter="gb_buy",
                                 payload="test-invoice-payloaad")
    await message.answer("Вы можете отменить пополнение", reply_markup=keyboard)


@router.message(Top_up.confirm_input_values, Text(text="🔃Неверная сумма🔃", text_ignore_case=True))
async def mistake_in_amount(message: Message, state: FSMContext):
    await state.set_state(Top_up.wait_input_values)
    kb = [[types.KeyboardButton(text="🙁Отмена пополнения🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer('Введите сумму пополнения заново', reply_markup=keyboard)


@router.message(Top_up.confirm_input_values, Text(text="🙁Отмена пополнения🙁", text_ignore_case=True))
async def back_top_up(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Пополнение отменено", reply_markup=keyboard)


@router.message(Top_up.confirm_input_values)
async def unidentified_top_up(message: Message):
    await message.answer("Неверная команда!\nПодтвердите или отмените пополнение")


@router.message(Top_up.wait_confirm_paid, content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await api_db.sql_bd_buyers.buyer_add_money(message.from_user.id, data['price'])
    await message.answer(
        f"Платеж на сумму {message.successful_payment.total_amount // 100} рублей прошел успешно!")
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Пополнение прошло успешно!", reply_markup=keyboard)


@router.message(Top_up.wait_confirm_paid, Text(text="🙁Отмена пополнения🙁", text_ignore_case=True))
async def back_top_up(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Пополнение отменено", reply_markup=keyboard)


@router.message(Top_up.wait_confirm_paid)
async def unidentified_top_up(message: Message):
    await message.answer("Неверная команда!\nОплатите пополнение или отмените его")
