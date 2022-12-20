from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

import api_db.sql_bd_buyers

router = Router()


class Support(StatesGroup):
    input_values = State()
    confirm_input_values = State()


@router.message(Support.input_values, Text(text="🙁Отмена обращения🙁", text_ignore_case=True))
async def back_appeals(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Обращение отменено", reply_markup=keyboard)


@router.message(Support.input_values)
async def wait_appeals(message: Message, state: FSMContext):
    await state.set_state(Support.confirm_input_values)
    await state.update_data(text=message.text.lower())
    kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="🙁Отмена обращения🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer("Подтвердите или отмените обращение в поддержку", reply_markup=keyboard)


@router.message(Support.confirm_input_values, Text(text="🙁Отмена обращения🙁", text_ignore_case=True))
async def back_appeals(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Обращение отменено", reply_markup=keyboard)


@router.message(Support.confirm_input_values, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_appeals(message: Message, state: FSMContext):
    text = await state.get_data()
    await state.clear()
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await api_db.sql_bd_buyers.add_support_cause_buyers(message.from_user.id, text['text'])
    await message.answer("Запрос отправлен. Можете продолжать покупки)", reply_markup=keyboard)


@router.message(Support.confirm_input_values)
async def unidentified_appeals(message: Message):
    await message.answer("Подтвердите или отмените обращение в поддержку")
