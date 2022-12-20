from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

import config
import api_db.sql_bd_sellers
from filters.filters_sellers import is_one_digit, order_no_in_wait_orders

router = Router()


class Sell(StatesGroup):
    get_orders = State()
    choose_order = State()
    order_confirmation = State()
    wait_confirm_complete = State()
    confirm_wrong = State()
    confirm_cannot_complete = State()
    confirm_comlete = State()


@router.message(Sell.get_orders, Text(text="📝Получить список📝", text_ignore_case=True))
async def get_list(message: Message, state: FSMContext):
    text = await api_db.sql_bd_sellers.return_orders_for_sellers(message.from_user.id)
    if text == '':
        await state.clear()
        kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
               types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(text="На данный момент нет заказов", reply_markup=keyboard)
    else:
        await state.set_state(Sell.choose_order)
        kb = [[types.KeyboardButton(text="❌Отмена продажи❌")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Введите номер заказа")
        await message.answer(text="Номер  Цена заказа   Цена\n" + text)
        await message.answer(text="Выберите заказ, и отправьте его номер", reply_markup=keyboard)


@router.message(Sell.get_orders, Text(text="❌Отмена продажи❌", text_ignore_case=True))
async def back_sell(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        text="Продажа отменена",
        reply_markup=keyboard)


@router.message(Sell.get_orders)
async def unidentified_command(message: Message):
    await message.answer(text="Неверная команда. Получите список или отмените продажу.")


@router.message(Sell.choose_order, is_one_digit())
async def check_is_digit(message: Message, state: FSMContext):
    num = int(message.text.lower())
    flag, data = await api_db.sql_bd_sellers.check_order_no_dell(num)
    if flag:
        await state.set_state(Sell.order_confirmation)
        kb = [[types.KeyboardButton(text="✔Подтвердить заказ✔"), types.KeyboardButton(text="❌Отмена продажи❌")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        if await api_db.sql_bd_sellers.is_vip_seller(message.from_user.id):
            await state.update_data(num=data[0], id_buy=data[1], link=data[2], price=data[3], price_buy=data[4],
                                    price_sel=data[4])
            await message.answer(
                f"Вы выбрали заказ номер {data[0]}.\nВыкуп заказа ценой {data[3]} рублей.\nВы получите {data[4]} руб",
                reply_markup=keyboard)
        else:
            await state.update_data(num=data[0], id_buy=data[1], link=data[2], price=data[3], price_buy=data[4],
                                    price_sel=int(data[3] * config.price_sellers))
            await message.answer(
                f"Вы выбрали заказ номер {data[0]}.\nВыкуп заказа ценой {data[3]} рублей.\nВы получите "
                f"{int(data[3] * config.price_sellers)} руб",
                reply_markup=keyboard)
    else:
        kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📝О проекте📝"),
               types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            "Заказ не существует, или уже был забронирован другим пользователем. Выберите другой или отмените покупку",
            reply_markup=keyboard)


@router.message(Sell.choose_order, Text(text="❌Отмена продажи❌", text_ignore_case=True))
async def back_sell(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        text="Продажа отменена",
        reply_markup=keyboard)


@router.message(Sell.choose_order)
async def unidentified_command(message: Message):
    await message.answer(text="Неверный номер. Выберите заказ, и отправьте его номер или отменити продажу")


@router.message(Sell.order_confirmation, Text(text="✔Подтвердить заказ✔", text_ignore_case=True))
async def confirm_order(message: Message, state: FSMContext):
    data = await state.get_data()
    flag = await api_db.sql_bd_sellers.move_order_to_wait(data['num'], data['id_buy'], data['link'],
                                                              data['price'], data['price_buy'],
                                                              message.from_user.id,
                                                              int(data['price'] * config.price_sellers))
    if flag:
        await state.set_state(Sell.wait_confirm_complete)
        kb = [[types.KeyboardButton(text="✅Выполнил✅"), types.KeyboardButton(text="🙃Ошибка🙃"),
               types.KeyboardButton(text="😕Не могу выполнить😕")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Выберите услугу")
        await message.answer(
            text=f"Вы подтвердили заказ. Выполните заказ на {data['price']} рублей.\nСсылка: \n{data['link']}\n\n"
                 f"После выкупа нажмите выполнил, для завершения заказа.",
            reply_markup=keyboard)
    else:
        await state.set_state(Sell.get_orders)
        kb = [[types.KeyboardButton(text="🗒Получить список🗒"), types.KeyboardButton(text="❌Отмена продажи❌")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(text="Заказ уже был забронирован другим пользователем.\nПожйлуста, выберите другой.",
                             reply_markup=keyboard)


@router.message(Sell.order_confirmation, Text(text="❌Отмена продажи❌", text_ignore_case=True))
async def back_order(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(
        text="Продажа отменена",
        reply_markup=keyboard)


@router.message(Sell.order_confirmation)
async def unidentified_command(message: Message):
    await message.answer(text="Подтвердите заказ или отмените продажу")


@router.message(
    Sell.wait_confirm_complete or Sell.confirm_cannot_complete or Sell.confirm_wrong
    or Sell.confirm_comlete, order_no_in_wait_orders())
async def skip_order(message: types.Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📝📄О проекте📄📝"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(text="В следующий раз будьте быстрее) Вы можете продолжать пользоваться ботом.",
                         reply_markup=keyboard)


@router.message(Sell.wait_confirm_complete, Text(text="✅Выполнил✅", text_ignore_case=True))
async def complete_order(message: types.Message, state: FSMContext):
    await state.set_state(Sell.confirm_comlete)
    kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="🔃Вернуться🔃")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(text="Подтвердите что вы выполнили заказ,иначе вернитесь к выполнению", reply_markup=keyboard)


@router.message(Sell.wait_confirm_complete, Text(text="🙃Ошибка🙃", text_ignore_case=True))
async def mistake_in_order(message: types.Message, state: FSMContext):
    await state.set_state(Sell.confirm_wrong)
    kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="🔃Вернуться🔃")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(
        text="Подтвердите, что пользователь ошибся в указании номера телефона, или же он уже имеет ранее полученный "
             "пакет\nЕсли же вы нажали случайно, вернитесь к выполнению заказа",
        reply_markup=keyboard)


@router.message(Sell.wait_confirm_complete, Text(text="😕Не могу выполнить😕", text_ignore_case=True))
async def can_not_complete(message: types.Message, state: FSMContext):
    await state.set_state(Sell.confirm_cannot_complete)
    kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="🔃Вернуться🔃")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(
        text="Подтвердите что вы не можете выполнить заказ по личным причина.\nЕсли же клиент допустил ошибку, "
             "вернитесь и выберите пункт ошибка",
        reply_markup=keyboard)


@router.message(Sell.wait_confirm_complete)
async def unidentified_command(message: types.Message):
    kb = [[types.KeyboardButton(text="✅Выполнил✅"), types.KeyboardButton(text="🙃Ошибка🙃"),
           types.KeyboardButton(text="😕Не могу выполнить😕")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(text="Прежде чем дальше пользоваться ботом, выполните заказ", reply_markup=keyboard)


@router.message(Sell.confirm_comlete, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_complete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await api_db.sql_bd_sellers.make_condition_complete(data['num'], data['id_buy'])
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Ожидайте подтверждения клиентом перевода. "
                              "Как только клиент закончит, на ваш счет сразу начисляться деньги",
                         reply_markup=keyboard)


@router.message(Sell.confirm_wrong, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_wrong(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await api_db.sql_bd_sellers.move_wait_to_wrong(data['num'], data['id_buy'], data['price_buy'])
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Заказ отменен. Вы модете продолжить пользоваться ботом.", reply_markup=keyboard)


@router.message(Sell.confirm_cannot_complete, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def cannot_complete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await api_db.sql_bd_sellers.move_wait_to_order(data['num'], data['id_buy'], data['link'], data['price'],
                                                       data['price_buy'])
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Заказ отменен. Вы модете продолжить пользоваться ботом.", reply_markup=keyboard)


@router.message(Sell.confirm_comlete, Text(text="🔃Вернуться🔃", text_ignore_case=True))
async def back_to_process(message: types.Message, state: FSMContext):
    await state.set_state(Sell.wait_confirm_complete)
    kb = [[types.KeyboardButton(text="✅Выполнил✅"), types.KeyboardButton(text="🙃Ошибка🙃"),
           types.KeyboardButton(text="😕Не могу выполнить😕")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(text='Вы вернулись к выполнению заказа', reply_markup=keyboard)


@router.message(Sell.confirm_wrong, Text(text="🔃Вернуться🔃", text_ignore_case=True))
async def back_to_process(message: types.Message, state: FSMContext):
    await state.set_state(Sell.wait_confirm_complete)
    kb = [[types.KeyboardButton(text="✅Выполнил✅"), types.KeyboardButton(text="🙃Ошибка🙃"),
           types.KeyboardButton(text="😕Не могу выполнить😕")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(text='Вы вернулись к выполнению заказа', reply_markup=keyboard)


@router.message(Sell.confirm_cannot_complete, Text(text="🔃Вернуться🔃", text_ignore_case=True))
async def back_to_process(message: types.Message, state: FSMContext):
    await state.set_state(Sell.wait_confirm_complete)
    kb = [[types.KeyboardButton(text="✅Выполнил✅"), types.KeyboardButton(text="🙃Ошибка🙃"),
           types.KeyboardButton(text="😕Не могу выполнить😕")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(text='Вы вернулись к выполнению заказа', reply_markup=keyboard)


@router.message(Sell.confirm_wrong)
async def unidentified_command(message: types.Message):
    await message.answer(text='Подтвердите что в заказе ошибка или покупатель уже имеет заказ или вернитесь к выполнению')


@router.message(Sell.confirm_comlete)
async def unidentified_command(message: types.Message):
    await message.answer(text='Подтвердите что выполнили задание или вернитесь')


@router.message(Sell.confirm_cannot_complete)
async def unidentified_command(message: types.Message):
    await message.answer(text='Подтвердите что не можете выполнить заказ или вернитесь к выполнению')
