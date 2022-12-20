from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text

import api_db.sql_bd_sellers
import config
from aiogram.dispatcher.fsm.context import FSMContext
import handlers_sellers.username_change

router = Router()


@router.message(Text(text="👉К продаже👈", text_ignore_case=True))
async def to_sell(message: Message, state: FSMContext):
    if await api_db.sql_bd_sellers.server_is_work():
        await state.set_state(handlers_sellers.Redemption.Sell.get_orders)
        kb = [[types.KeyboardButton(text="📝Получить список📝"), types.KeyboardButton(text="❌Отмена продажи❌")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                             input_field_placeholder="Выберите услугу")
        await message.answer(
            "Получите список доступных заказов. Учтите, что надо выполнять все по алгоритму.\nПри попытке об"
            "мануть систему вы будете забанены навсегда!", reply_markup=keyboard)
    else:
        await message.answer(
            "Покупка и продажа приостановлена\nНа сервере ведутся работы\nНадеемся что вскоре проблема будет устранена")


@router.message(Text(text="👨‍💼Поддержка👨‍💼", text_ignore_case=True))
async def support(message: Message, state: FSMContext):
    await state.set_state(handlers_sellers.support.Support.input_values)
    kb = [[types.KeyboardButton(text="❌Отмена обращения❌")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await message.answer("Введите свое обращение в поддержку.", reply_markup=keyboard)


@router.message(Text(text="❌Отмена продажи❌", text_ignore_case=True))
async def back_from_sell(message: Message):
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Продажа отменена", reply_markup=keyboard)


@router.message(Text(text="📄О проекте📄", text_ignore_case=True))
async def about_project(message: Message):
    buttons = [[types.InlineKeyboardButton(text="📝Правила📝", callback_data="rules")], ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(open("texts/about_projects.txt", 'r', encoding='utf-8').read(), reply_markup=keyboard)


@router.callback_query(text="rules")
async def rules(callback: types.CallbackQuery):
    await callback.message.answer(open("texts/pravila_for_buyers.txt", 'r', encoding='utf-8').read())
    await callback.answer()


@router.message(Text(text="👨‍💻Аккаунт👨‍💻", text_ignore_case=True))
async def account(message: Message):
    buttons = [[types.InlineKeyboardButton(text="📱Тел📱", callback_data="tel"),
                types.InlineKeyboardButton(text="👨‍💻Имя пользователя👨‍💻", callback_data="username")],
               [types.InlineKeyboardButton(text="📈Статистика📈", callback_data="statistics")],
               [types.InlineKeyboardButton(text="💵Вывод💵", callback_data="dring_up")],
               [types.InlineKeyboardButton(text="💵История выводов💵", callback_data="history_dring_up")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    data = await api_db.sql_bd_sellers.get_inform_about_my_account_seller(message.from_user.id)
    await message.answer(
        f"👨‍💻Пользователь: {data[0]}\n📱Ваш телефон: {data[2]}\n💰Баланс: {data[3]} рублей\n📈Ваш рейтинг: "
        f"{await api_db.sql_bd_sellers.get_reiting_seller(data[4], data[5], data[6], data[7], data[8])}",
        reply_markup=keyboard)


@router.callback_query(text="tel")
async def input_tel(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(handlers_sellers.registration.Registration.wait_input_values)
    kb = [[types.KeyboardButton(text="❌Отмена регистрации❌")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await callback.message.answer(text="Чтобы добавить или изменить телефон, введите ваш номер в формате:\n89998885577",
                                  reply_markup=keyboard)
    await callback.answer()


@router.callback_query(text="statistics")
async def statistic(callback: types.CallbackQuery):
    data = await api_db.sql_bd_sellers.get_inform_about_my_account_seller(callback.from_user.id)
    await callback.message.answer(
        text=f"Статистика вашего 👨‍💻Аккаунт👨‍💻а:\nУспешных продаж: {data[4]}\nНеудачных продаж: {data[5]}\nВсего пропусков: "
             f"{data[6]}\nОтмечено ошибок: {data[7]}\nСкам: {data[8]}")
    await callback.answer()


@router.callback_query(text="dring_up")
async def dring_up(callback: types.CallbackQuery, state: FSMContext):
    score = await api_db.sql_bd_sellers.get_seller_count_score(callback.from_user.id)
    if score >= config.min_amount_dring_up:
        await state.set_state(handlers_sellers.dring_up.Dring_up.wait_requisites)
        await state.update_data(amount=score)
        kb = [[types.KeyboardButton(text="📱Мой номер📱"), types.KeyboardButton(text="❌Отмена вывода❌")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await callback.message.answer(
            text=f"Вы хотите вывести деньги с вашего баланса в размере {score} рублей\nВведите свои реквезиты в "
                 f"формате:\n\n(номер карты/тел) (банк) (имя отчество)\nВы также можете заполнить номер автоматически",
            reply_markup=keyboard)
    else:
        await callback.message.answer(
            text=f"Для вывода баланса ваш баланс должен привышать минимальный порог ({config.min_amount_dring_up} "
                 f"рублей)")
    await callback.answer()


@router.callback_query(text="history_dring_up")
async def get_history_dring_up(callback: types.CallbackQuery):
    await callback.message.answer(text=await api_db.sql_bd_sellers.get_dring_ups(callback.from_user.id))
    await callback.answer()


@router.callback_query(text="username")
async def change_username(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(handlers_sellers.username_change.Username.wait_input_values)
    kb = [[types.KeyboardButton(text="❌Отмена регистрации❌")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите пункт")
    await callback.message.answer("Чтобы добавить или изменить имя пользователя, введите его с '@', пример:\n@username",
                                  reply_markup=keyboard)
    await callback.answer()


@router.message(commands=["start"])
async def cmd_start(message: Message):
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(open("texts/pravila_for_buyers.txt", 'r', encoding='utf-8').read(), reply_markup=keyboard)
    await api_db.sql_bd_sellers.add_seller(message.from_user.id, message.from_user.username)


@router.message()
async def unidentified_command(message: Message):
    kb = [[types.KeyboardButton(text="👉К продаже👈"), types.KeyboardButton(text="📄О проекте📄"),
           types.KeyboardButton(text="👨‍💼Поддержка👨‍💼"), types.KeyboardButton(text="👨‍💻Аккаунт👨‍💻")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Нераспознанная команда", reply_markup=keyboard)
