import random

from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types.message import ContentType

import config
from filters.filters_buyers import is_link, is_price_order
import api_db.sql_bd_buyers

router = Router()


class Order(StatesGroup):
    wait_link_value = State()
    wait_price_value = State()
    wait_confirmation = State()
    wait_paid = State()
    wait_confirm_paid = State()
    awaiting_transfer = State()
    confirm_getting = State()
    confirm_problem = State()


@router.message(Order.wait_link_value, is_link())
async def lot_wait_link(message: Message, state: FSMContext):
    await state.set_state(Order.wait_price_value)
    link = message.text.lower().split()[0]
    await state.update_data(link=link)
    kb = [[types.KeyboardButton(text="🙁Отмена покупки🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Пришлите сумму продукта💰", reply_markup=keyboard)


@router.message(Order.wait_link_value, Text(text="🙁Отмена покупки🙁", text_ignore_case=True))
async def back_buy_wait_link(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Покупка отменена", reply_markup=keyboard)


@router.message(Order.wait_link_value)
async def unrecognized_command_wait_link(message: Message):
    await message.answer(text="Неправильная ссылка\nВведите ссылку на продукт")


@router.message(Order.wait_price_value, is_price_order())
async def check_price(message: Message, state: FSMContext):
    await state.set_state(Order.wait_confirmation)
    price = int(message.text.lower().split()[0])
    kb = [[types.KeyboardButton(text="💾Подтверждение данных💾"), types.KeyboardButton(text="🙁Отмена покупки🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await state.update_data(price=price, price_buy=int(price * config.price_buyers))
    await message.answer(
        f"Подтвердите правильность данных\nВы хотите купить продукт на сумму {price} рублей\nСумма оплаты "
        f"{int(price * config.price_buyers)} руб\n\nПодтвердите правильность ссылки и цены, иначе не получиться "
        "осуществить правильное взаимодействие",
        reply_markup=keyboard)


@router.message(Order.wait_price_value, Text(text="🙁Отмена покупки🙁", text_ignore_case=True))
async def back_buy_wait_price(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Покупка отменена", reply_markup=keyboard)


@router.message(Order.wait_price_value)
async def unrecognized_command_wait_price(message: Message):
    await message.answer(text="Неверные данные. Укажите верную стоимость продукта")


@router.message(Order.wait_confirmation, Text(text="💾Подтверждение данных💾", text_ignore_case=True))
async def confirm_data(message: Message, state: FSMContext):
    await state.set_state(Order.wait_paid)
    price = await state.get_data()
    price = price['price_buy']
    if config.min_price_ya_kassa < price <= config.max_price_Ya_kassa:
        kb = [[types.KeyboardButton(text="💵Оплатить💵"), types.KeyboardButton(text="💵Оплатить со счета💵"),
               types.KeyboardButton(text="🙁Отмена покупки🙁")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Выберите услугу")
        await message.answer(
            text="Вы подтвердили данные\nНажмите `оплатить` чтобы прейти к оплате картой\nНажмите `оплатить со "
                 "счета`, чтобы оплатить с вашего счета",
            reply_markup=keyboard)
    else:
        kb = [[types.KeyboardButton(text="💵Оплатить со счета💵"), types.KeyboardButton(text="🙁Отмена покупки🙁")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Выберите услугу")
        await message.answer(
            text="Данные подтверждены. Цена меньше минимальной, поэтому оплата вохможно только со счета. Нажмите "
                 "оплатить ниже, чтобы оплатить с вашего счета",
            reply_markup=keyboard)


@router.message(Order.wait_confirmation, Text(text="🙁Отмена покупки🙁", text_ignore_case=True))
async def back_buy_wait_confirm(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        text="Покупка отменена",
        reply_markup=keyboard
    )


@router.message(Order.wait_confirmation)
async def unrecognized_command_wait_confirm(message: types.Message):
    await message.answer("Не распознанная команда. Подтвердите заказ или отмените его")


# Оплата ------------------------------------------------------------------------------
@router.message(Order.wait_paid, Text(text="💵Оплатить💵", text_ignore_case=True))
async def pay(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not (config.max_price_Ya_kassa >= data['price_buy'] >= config.min_price_ya_kassa):
        await message.answer(text='Сумма оплаты не корректна')
        return
    await state.set_state(Order.wait_confirm_paid)
    if config.PAYMENTS_TOKEN.split(':')[1] == "TEST":
        await message.answer("Тестовый платеж!!!")
    PRICE = types.LabeledPrice(label="Оплата продукта", amount=data['price_buy'] * 100)  # в копейках
    await message.answer_invoice(title='Оплата продукта', description='Оплата продукта',
                                 provider_token=config.PAYMENTS_TOKEN, currency="rub",
                                 # photo_url = "https://yandex.ru/images/search?text=%D0%BE%D1%87%D0%B5%D0%BD%D1%8C
                                 # %20%D0%BA%D1%80%D0%B0%D1%81%D0%B8%D0%B2%D1%8B%D0%B5%D0%B7%D0%B5%D0%BC%D0%BB%D0%B8
                                 # &from=tabbar&pos=11&img_url=http%3A%2F%2Fmota.ru%2Fupload%2Fwallpapers%2Fsource
                                 # %2F2014%2F06%2F08%2F13%2F00%2F40404%2F51.jpg&rpt=simage&lr=47", photo_width = 416,
                                 # photo_height= 234, photo_size = 416,
                                 is_flexible=False,
                                 prices=[PRICE],
                                 start_parameter="min_redmption",
                                 payload="test-invoice-payloaad")


@router.message(Order.wait_paid, Text(text="💵Оплатить со счета💵", text_ignore_case=True))
async def pay_with_score(message: types.Message, state: FSMContext):
    data = await state.get_data()
    flag, balans = await api_db.sql_bd_buyers.buyer_use_with_score(message.from_user.id, data['price_buy'])
    if flag:
        await state.set_state(Order.awaiting_transfer)
        kb = [[types.KeyboardButton(text="🙂Заказ выполнен🙂"), types.KeyboardButton(text="Заказ не выполнен🙁")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Выберите пункт")
        num = await api_db.sql_bd_buyers.add_orders(message.from_user.id, data['link'], data['price'],
                                                    data['price_buy'])
        await state.update_data(num=num)
        await message.answer(f"Платеж прошел успешно💵\nВаш заказ ожидает своего исполнителя👨🏻‍💻\nВаш баланс: {balans}💰",
                             reply_markup=keyboard)
    else:
        if not (config.max_price_Ya_kassa >= data['price_buy'] >= config.min_price_ya_kassa):
            await state.clear()
            kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
                   types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                                 input_field_placeholder="Выберите услугу")
            await message.answer(f"Недостаточно средств\nВаш баланс: {balans}💰", reply_markup=keyboard)
        else:
            await state.set_state(Order.wait_paid)
            kb = [[types.KeyboardButton(text="💵Оплатить💵"), types.KeyboardButton(text="🙁Отмена покупки🙁")]]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                                 input_field_placeholder="Выберите услугу")
            await message.answer("Недостаточно средств", reply_markup=keyboard)


@router.message(Order.wait_paid, Text(text="🙁Отмена покупки🙁", text_ignore_case=True))
async def back_buy_wait_paid(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Платеж отменен", reply_markup=keyboard)


@router.message(Order.wait_paid)
async def unrecognized_command_wait_paid(message: Message):
    await message.answer(text="Неверные входные данные. Оплатите или отмените заказ")


@router.message(Order.wait_confirm_paid, content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message, state: FSMContext):
    await state.set_state(Order.awaiting_transfer)
    await message.answer(
        f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел"
        " успешно!")
    kb = [[types.KeyboardButton(text="🙂Заказ выполнен🙂"), types.KeyboardButton(text="🙁Заказ не выполнен🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    data = await state.get_data()
    num = await api_db.sql_bd_buyers.add_orders(message.from_user.id, data['link'], data['price'],
                                                data['price_buy'])
    await state.update_data(num=num)
    await message.answer(
        "Ваш заказ ожидает своего исполнителя. Пожайлуста подождите, обычно это занимает немного времени."
        "\nЕсли в течении 6 часов заказ так и не был выполнен, обратитесь в поддержку",
        reply_markup=keyboard)


@router.message(Order.wait_confirm_paid, Text(text="🙁Отмена покупки🙁", text_ignore_case=True))
async def back_buy_wait_confirm_paid(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Покупка отменена", reply_markup=keyboard)


@router.message(Order.awaiting_transfer, Text(text="🙂Заказ выполнен🙂", text_ignore_case=True))
async def order_complete(message: types.Message, state: FSMContext):
    num = await state.get_data()
    num = num['num']
    if await api_db.sql_bd_buyers.check_order_in_wait_no_del_cond_1(num, message.from_user.id):
        await state.set_state(Order.confirm_getting)
        kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="❌Вернуться к ожиданию❌")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Выберите услугу")
        await message.answer(text="Подтвердите получение или вернитесь к ожиданию", reply_markup=keyboard)
    elif await api_db.sql_bd_buyers.check_order_in_wait_no_del_cond_0(num, message.from_user.id):
        kb = [[types.KeyboardButton(text="🙂Заказ выполнен🙂"), types.KeyboardButton(text="🙁Заказ не выполнен🙁")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Выберите услугу")
        await message.answer(text="Ваш заказ находится в процессе выполнения продавцом", reply_markup=keyboard)
    else:
        if await api_db.sql_bd_buyers.check_order_no_dell_one(num, message.from_user.id):
            kb = [[types.KeyboardButton(text="🙂Заказ выполнен🙂"), types.KeyboardButton(text="🙁Заказ не выполнен🙁")], ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                                 input_field_placeholder="Выберите услугу")
            await message.answer(text='Ваш заказ находится еще в листе ожидания', reply_markup=keyboard)
        else:
            await state.clear()
            kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
                   types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                                 input_field_placeholder="Выберите услугу")
            await message.answer(text='Вы можете продолжить покупки', reply_markup=keyboard)


@router.message(Order.awaiting_transfer, Text(text="🙁Заказ не выполнен🙁", text_ignore_case=True))
async def order_not_complete(message: types.Message, state: FSMContext):
    num = await state.get_data()
    num = num['num']
    if await api_db.sql_bd_buyers.check_order_in_wait_no_del_cond_1(num, message.from_user.id):
        await state.set_state(Order.confirm_problem)
        kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="❌Вернуться к ожиданию❌")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Выберите услугу")
        await message.answer(text="Подтвердите, что заказ не выполнен или вернитесь к ожиданию", reply_markup=keyboard)
    elif await api_db.sql_bd_buyers.check_order_in_wait_no_del_cond_0(num, message.from_user.id):
        await message.answer(text="Ваш заказ находится в процессе выполнения продавцом")
    else:
        if await api_db.sql_bd_buyers.check_order_no_dell_one(num, message.from_user.id):
            await message.answer(text='Ваш заказ находится еще в листе ожидания')
        else:
            await state.clear()
            kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
                   types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                                 input_field_placeholder="Выберите услугу")
            await message.answer(text='Вы можете продолжить покупки', reply_markup=keyboard)


@router.message(Order.awaiting_transfer)
async def unrecognized_command_awaiting(message: types.Message):
    kb = [[types.KeyboardButton(text="🙂Заказ выполнен🙂"), types.KeyboardButton(text="🙁Заказ не выполнен🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(
        "Во время ожидания подтверждения заказа вы не можете пользоваться ботом, пока заказ не выполнен.\n"
        "Подтвердите получение или обратитесь в поддержку, если заказ не выкупили в течении 6 часов после начала "
        "выполнения",
        reply_markup=keyboard)


@router.message(Order.confirm_getting, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_complete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await api_db.sql_bd_buyers.move_wait_to_history(data['num'], message.from_user.id)
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await api_db.sql_bd_buyers.buyer_luck_buy(str(message.from_user.id))
    await message.answer(text="Спасибо за покупку. Были рады вам помочь)❤", reply_markup=keyboard)
    await message.reply_sticker(sticker=config.sticker_happy[random.randint(0, config.len_sticker_happy - 1)])


@router.message(Order.confirm_getting, Text(text="❌Вернуться к ожиданию❌", text_ignore_case=True))
async def back_await(message: types.Message, state: FSMContext):
    await state.set_state(Order.awaiting_transfer)
    kb = [[types.KeyboardButton(text="🙂Заказ выполнен🙂"), types.KeyboardButton(text="🙁Заказ не выполнен🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Вы возвращены к ожиданию", reply_markup=keyboard)


@router.message(Order.confirm_getting)
async def unrecognized_command_confirm_get(message: types.Message):
    await message.answer(text="Подтвердите получение или вернитесь к ожиданию")


@router.message(Order.confirm_problem, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_problem(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await api_db.sql_bd_buyers.move_wait_to_problem_orders(data['num'], message.from_user.id)
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        "Ваша проблема перемещена в обработку модераторами👨🏻‍💻👨🏻‍💻\nВремя обработки может занять до 24 "
        "часов⌚\nВы можете продолжить пользоваться ботом",
        reply_markup=keyboard)


@router.message(Order.confirm_problem, Text(text="❌Вернуться к ожиданию❌", text_ignore_case=True))
async def back_await(message: types.Message, state: FSMContext):
    await state.set_state(Order.awaiting_transfer)
    kb = [[types.KeyboardButton(text="🙂Заказ выполнен🙂"), types.KeyboardButton(text="🙁Заказ не выполнен🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Вы возвращены к ожиданию", reply_markup=keyboard)


@router.message(Order.confirm_problem)
async def unrecognized_command_problem(message: types.Message):
    await message.answer(text="Подтвердите, что заказ не выполнен или вернитесь к ожиданию")
