from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.context import FSMContext

import config
import api_db.sql_bd_buyers
import handlers_buyers.username_change
import handlers_buyers.support
import handlers_buyers.Redemption
import handlers_buyers.registration
import handlers_buyers.top_up

router = Router()


@router.message(Text(text="💳К покупке💳", text_ignore_case=True))
async def to_buy(message: Message, state: FSMContext):
    if await api_db.sql_bd_buyers.server_is_work():
        await state.set_state(handlers_buyers.Redemption.Order.wait_link_value)
        kb = [[types.KeyboardButton(text="🙁Отмена покупки🙁")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("Чтобы купить, вы должны указать ссылку на покупаемый предмет", reply_markup=keyboard)
    else:
        await message.answer("Покупка и продажа приостановлена\n На сервере ведутся работы\nНадеемся что вскоре "
                             "проблема будет устранена")


@router.message(Text(text="📄О проекте📄", text_ignore_case=True))
async def about_project(message: Message):
    buttons = [[types.InlineKeyboardButton(text="📝Правила📝", callback_data="rules"),
                types.InlineKeyboardButton(text="📃Оферта📃", callback_data="offer")], ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(open("texts/about_projects.txt", 'r', encoding='utf-8').read(), reply_markup=keyboard)


@router.callback_query(text="rules")
async def rules(callback: types.CallbackQuery):
    await callback.message.answer(open("texts/pravila_for_buyers.txt", 'r', encoding='utf-8').read())
    await callback.answer()


@router.callback_query(text="offer")
async def offer(callback: types.CallbackQuery):
    await callback.message.answer(open("texts/Offer.txt", 'r', encoding='utf-8').read())
    await callback.answer()


@router.message(Text(text="👨‍💼Поддержка👨‍💼"))
async def support(message: Message, state: FSMContext):
    await state.set_state(handlers_buyers.support.Support.input_values)
    kb = [[types.KeyboardButton(text="🙁Отмена обращения🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer(
        "Введите свое обращение. Оно должно содержать проблему или, например, предложение новых функций бота.",
        reply_markup=keyboard)


@router.message(Text(text="👨‍💻Аккаунт👨‍💻", text_ignore_case=True))
async def account(message: Message):
    buttons = [[types.InlineKeyboardButton(text="📱Тел📱", callback_data="tel"),
                types.InlineKeyboardButton(text="👨‍💻Имя пользооватлея👨‍💻", callback_data="username")],
               [types.InlineKeyboardButton(text="📈Статистика📈", callback_data="statistics")],
               [types.InlineKeyboardButton(text="📄Пополнение📄", callback_data="top_up")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    data = await api_db.sql_bd_buyers.get_inform_about_my_account_buyer(str(message.from_user.id))
    await message.answer(
        f"👨‍💻Пользователь: {data[0]}\n📱Ваш телефон: {data[2]}\n💰Баланс: {data[3]} рублей\n📈Ваш рейтинг: "
        f"{await api_db.sql_bd_buyers.get_rating_buyer(data[4], data[5], data[6])}",
        reply_markup=keyboard)


@router.callback_query(text="tel")
async def change_tel(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(handlers_buyers.registration.Registration.wait_input_values)
    kb = [[types.KeyboardButton(text="🙁Отмена регистрации🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await callback.message.answer("Чтобы добавить или изменить телефон, введите ваш номер в формате:\n89998885577",
                                  reply_markup=keyboard)
    await callback.answer()


@router.callback_query(text="username")
async def username(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(handlers_buyers.username_change.Username.wait_input_values)
    kb = [[types.KeyboardButton(text="🙁Отмена регистрации🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await callback.message.answer("Чтобы добавить или изменить имя пользователя, введите его с '@', пример:\n@username",
                                  reply_markup=keyboard)
    await callback.answer()


@router.callback_query(text="statistics")
async def statistics(callback: types.CallbackQuery):
    data = await api_db.sql_bd_buyers.get_inform_about_my_account_buyer(callback.from_user.id)
    await callback.message.answer(
        text=f"Статистика вашего 👨‍💻Аккаунт👨‍💻а:\nУспешных покупок: {data[4]}\nНеудачных: {data[5]}\nСкам: {data[6]}")
    await callback.answer()


@router.callback_query(text="top_up")
async def top_up(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(handlers_buyers.top_up.Top_up.wait_input_values)
    kb = [[types.KeyboardButton(text="🙁Отмена пополнения🙁")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await callback.message.answer(f"Чтобы пополнить ваш счет введите сумму пополнения(целое значение от "
                                  f"{config.min_price_ya_kassa} до {config.max_price_Ya_kassa} рублей)",
                                  reply_markup=keyboard)
    await callback.answer()


@router.message(commands=["start"])
async def start(message: Message):
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(open("texts/Offer.txt", 'r', encoding='utf-8').read(), reply_markup=keyboard)
    await message.answer(open("texts/pravila_for_buyers.txt", 'r', encoding='utf-8').read(), reply_markup=keyboard)
    await api_db.sql_bd_buyers.add_buyer(message.from_user.id, message.from_user.username)


@router.message()
async def undefined(message: Message):
    kb = [[types.KeyboardButton(text="💳К покупке💳"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Нераспознанная команда", reply_markup=keyboard)
