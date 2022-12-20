from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

import api_db.sql_bd_sellers

router = Router()


class Dring_up(StatesGroup):
    wait_requisites = State()
    wait_other_data = State()
    confirm_requisites = State()


@router.message(Dring_up.wait_requisites, Text(text="📱Мой номер📱", text_ignore_case=True))
async def chose_my_tel(message: Message, state: FSMContext):
    tel = await api_db.sql_bd_sellers.get_seller_tel(message.from_user.id)
    if tel != "-":
        await state.set_state(Dring_up.wait_other_data)
        await state.update_data(tel=tel)
        kb = [[types.KeyboardButton(text="❌Отмена вывода❌")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(
            "Теперь введите название банка, имя и отчество для проверки(имя и отчество не обязательно, это сделано "
            "для вашей безопасности)",
            reply_markup=keyboard)
    else:
        await message.answer(
            "Вашего телефона нет в базе, введите все данные вручную\n\n(тел/номер карты) (банк) (имя, отчество) - "
            "последнее не обязательно, это сделано для вашей безопасности")


@router.message(Dring_up.wait_requisites)
async def unidentified_command(message: Message, state: FSMContext):
    await state.set_state(Dring_up.confirm_requisites)
    await state.update_data(requisites=message.text.lower())
    kb = [[types.KeyboardButton(text="✔Подтвердить реквизиты✔"), types.KeyboardButton(text="❌Отмена вывода❌")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(f"Подтвердите правильность введенных реквезитов:\n\n{message.text.lower()}",
                         reply_markup=keyboard)


@router.message(Dring_up.wait_requisites, Text(text="❌Отмена вывода❌", text_ignore_case=True))
async def back_dring_up(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Вывод отменен", reply_markup=keyboard)


@router.message(Dring_up.wait_other_data)
async def unidentified_command(message: Message, state: FSMContext):
    await state.set_state(Dring_up.confirm_requisites)
    data = await state.get_data()
    await state.update_data(requisites=message.text.lower())
    kb = [[types.KeyboardButton(text="✔Подтвердить реквизиты✔"), types.KeyboardButton(text="❌Отмена вывода❌")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(f"Подтвердите правильность введенных реквезитов:\n\n{data['tel']} {message.text.lower()}",
                         reply_markup=keyboard)


@router.message(Dring_up.wait_other_data, Text(text="❌Отмена вывода❌", text_ignore_case=True))
async def back_dring_up(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Вывод отменен", reply_markup=keyboard)


@router.message(Dring_up.confirm_requisites, Text(text="✔Подтвердить реквизиты✔", text_ignore_case=True))
async def confirm_requisites(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    if 'tel' in data:
        await api_db.sql_bd_sellers.dring_up(message.from_user.id, data['amount'], data['tel'] + data['requisites'])
        await message.answer("Заявка на вывод создана\nОжидайте подтверждения модераторов", reply_markup=keyboard)
    else:
        await api_db.sql_bd_sellers.dring_up(message.from_user.id, data['amount'], data['requisites'])
        await message.answer("Заявка на вывод создана\nОжидайте подтверждения модераторов", reply_markup=keyboard)


@router.message(Dring_up.confirm_requisites, Text(text="❌Отмена вывода❌", text_ignore_case=True))
async def back_dring_up(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Вывод отменен", reply_markup=keyboard)


@router.message(Dring_up.confirm_requisites)
async def unidentified_command(message: Message):
    await message.answer("Неверная команда!\nПодтвердите или отмените вывод")
