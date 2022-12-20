from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

import api_db.sql_bd_sellers
from filters.filters_buyers import is_username

router = Router()


class Username(StatesGroup):
    wait_input_values = State()
    confirm_input_values = State()


@router.message(Username.wait_input_values, Text(text="❌Отмена регистрации❌", text_ignore_case=True))
async def back_registration(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Регистрация номера телефона отменена", reply_markup=keyboard)


@router.message(Username.wait_input_values, is_username())
async def check_username(message: Message, state: FSMContext):
    await state.set_state(Username.confirm_input_values)
    await state.update_data(username=message.text.lower())
    kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="🔃Изменить имя🔃"),
           types.KeyboardButton(text="❌Отмена регистрации❌")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer("Подтвердите правильность имени\nВ случае, если вы ввели неверный ник, нажмите изменить имя!",
                         reply_markup=keyboard)


@router.message(Username.wait_input_values)
async def unidentified_command(message: Message):
    await message.answer('Вы ввели неверный ник. Введите заново в формате:\n@username')


@router.message(Username.confirm_input_values, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_username(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await api_db.sql_bd_sellers.seller_change_username(message.from_user.id, data['username'])
    await message.answer("Ваш ник добавлен или изменен", reply_markup=keyboard)


@router.message(Username.confirm_input_values, Text(text="🔃Изменить имя🔃", text_ignore_case=True))
async def change_username(message: Message, state: FSMContext):
    await state.set_state(Username.wait_input_values)
    kb = [[types.KeyboardButton(text="❌Отмена регистрации❌")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer('Введите заново в формате:\n@username', reply_markup=keyboard)


@router.message(Username.confirm_input_values, Text(text="❌Отмена регистрации❌", text_ignore_case=True))
async def back_registration(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Изменение ника отменено", reply_markup=keyboard)


@router.message(Username.confirm_input_values)
async def unidentified_command(message: Message):
    await message.answer("Неверная команда!\nПодтвердите или измените ваш ник, или же отмените изменение!")
