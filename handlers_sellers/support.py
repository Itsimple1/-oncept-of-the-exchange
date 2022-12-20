from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
import api_db.sql_bd_sellers

router = Router()


class Support(StatesGroup):
    input_values = State()
    confirm_input_values = State()


@router.message(Text(text="👨‍💼Поддержка👨‍💼", text_ignore_case=True))
async def suppport(message: Message, state: FSMContext):
    await state.set_state(Support.input_values)
    kb = [[types.KeyboardButton(text="❌Отмена обращения❌")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Введите свое обращение в поддержку.", reply_markup=keyboard)


@router.message(Support.input_values, Text(text="❌Отмена обращения❌", text_ignore_case=True))
async def back_support(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Введите свое обращение в поддержку.", reply_markup=keyboard)


@router.message(Support.input_values)
async def unidentified_command(message: Message, state: FSMContext):
    await state.set_state(Support.confirm_input_values)
    await state.update_data(text=message.text.lower())
    kb = [[types.KeyboardButton(text="✔Подтвердить✔"), types.KeyboardButton(text="❌Отмена обращения❌")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer("Подтвердите обращение в поддержку", reply_markup=keyboard)


@router.message(Support.confirm_input_values, Text(text="❌Отмена обращения❌", text_ignore_case=True))
async def back_support(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Обращение отменено", reply_markup=keyboard)


@router.message(Support.confirm_input_values, Text(text="✔Подтвердить✔", text_ignore_case=True))
async def confirm_support(message: Message, state: FSMContext):
    text = await state.get_data()
    await state.clear()
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await api_db.sql_bd_sellers.add_support_cause_seller(message.from_user.id, text['text'])
    await message.answer("Запрос отправлен. Можете продолжать продавать)", reply_markup=keyboard)


@router.message(Support.confirm_input_values)
async def unidentified_command(message: Message):
    await message.answer("Выберите один из пунктов")
