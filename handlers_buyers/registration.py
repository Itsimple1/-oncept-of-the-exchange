from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

import api_db.sql_bd_buyers
from filters.filters_buyers import is_telephone_number

router = Router()


class Registration(StatesGroup):
    wait_input_values = State()
    confirm_input_values = State()


@router.message(Registration.wait_input_values, Text(text="🙁Отмена регистрации🙁", text_ignore_case=True))
async def back_menu_wait(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Регистрация номера телефона отменена", reply_markup=keyboard)


@router.message(Registration.wait_input_values, is_telephone_number())
async def is_tel_number(message: Message, state: FSMContext):
    await state.set_state(Registration.confirm_input_values)
    await state.update_data(input_tel=message.text.lower().replace(" ", ""))
    kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="🔃Ошибка в номере🔃"),
           types.KeyboardButton(text="🙁Отмена регистрации🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer(
        "Подтвердите правильность номера. \nВ случае неверно введенного номера при покупке тех-Поддержка не сможет "
        "вам помочь!",
        reply_markup=keyboard)


@router.message(Registration.wait_input_values)
async def undefined_wait_input(message: Message):
    await message.answer('Вы ввели неверный номер телефона. Введите номер в формате:\n+79990007711 или 89998885577')


@router.message(Registration.confirm_input_values, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await api_db.sql_bd_buyers.buyer_add_tel(str(message.from_user.id), data['input_tel'])
    await message.answer("Ваш номер телефона добавлен или изменен", reply_markup=keyboard)


@router.message(Registration.confirm_input_values, Text(text="🔃Ошибка в номере🔃", text_ignore_case=True))
async def mistake_in_number(message: Message, state: FSMContext):
    await state.set_state(Registration.wait_input_values)
    kb = [[types.KeyboardButton(text="Отмена регистрации")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer('Введите ваш номер телефона заново в формате:\n+79990007711 или 89998885577',
                         reply_markup=keyboard)


@router.message(Registration.confirm_input_values, Text(text="🙁Отмена регистрации🙁", text_ignore_case=True))
async def back_registration(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Регистрация номера телефона отменена", reply_markup=keyboard)


@router.message(Registration.confirm_input_values)
async def unidentified_command(message: Message):
    await message.answer("Неверная команда!\nПодтвердите или измените номер телефона, или же отмените регистрацию!")
