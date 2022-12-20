from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

import api_db.sql_bd_moderator
import bot_buyers

router = Router()


class moder_support_buy(StatesGroup):
    start = State()
    wait_for_processing = State()
    wait_message = State()
    confirm_send_message = State()
    confirm_proccess = State()


# Проверка лота на правильность --------------------------------------------------
@router.message(moder_support_buy.start, Text(text="Обработать запрос", text_ignore_case=True))
async def complete_support_request(message: Message, state: FSMContext):
    data = await api_db.sql_bd_moderator.get_support_request_buy()
    if data is not None:
        await state.set_state(moder_support_buy.wait_for_processing)
        kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Доп информация"),
               types.KeyboardButton(text="Отправить сообщение"), types.KeyboardButton(text="Отменить")],
              ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await state.update_data(number=data[0], id_buy=data[1], request=data[2])
        await message.answer(f"Запрос №{data[0]}\nID покупателя: {data[1]}\n\nЗапрос:\n{data[2]}")
        await message.answer("Обработайте запрос и подтвердите обработку", reply_markup=keyboard)
    else:
        await state.clear()
        kb = [[types.KeyboardButton(text="Модерация"), types.KeyboardButton(text="Заявки на вывод"),
               types.KeyboardButton(text="Статистика"), types.KeyboardButton(text="Правила")],
              ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(text="На данный момент нет запросов в поддержку", reply_markup=keyboard)


@router.message(moder_support_buy.start, Text(text="Меню", text_ignore_case=True))
async def back_menu(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="Модерация"), types.KeyboardButton(text="Заявки на вывод"),
           types.KeyboardButton(text="Статистика"), types.KeyboardButton(text="Правила")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Возвращаем вас в меню", reply_markup=keyboard)


@router.message(moder_support_buy.start)
async def unidentified_command(message: Message):
    await message.answer(text="Выберите один из пунктов")


@router.message(moder_support_buy.wait_for_processing, Text(text="Обработал", text_ignore_case=True))
async def confirm_complete(message: types.Message, state: FSMContext):
    await state.set_state(moder_support_buy.confirm_proccess)
    kb = [[types.KeyboardButton(text="Подтвердить"), types.KeyboardButton(text="Вернуться к рассмотрению")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Подтвердите, что обработали запрос", reply_markup=keyboard)


@router.message(moder_support_buy.wait_for_processing, Text(text="Доп информация", text_ignore_case=True))
async def dop_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(await api_db.sql_bd_moderator.dop_info_buy(data['id_buy']))


@router.message(moder_support_buy.wait_for_processing, Text(text="Отправить сообщение", text_ignore_case=True))
async def sen_message(message: types.Message, state: FSMContext):
    await state.set_state(moder_support_buy.wait_message)
    kb = [[types.KeyboardButton(text="Отменить отправку")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Введите сообщение, которое нужно отправить человекку, написавшему данынй запрос",
                         reply_markup=keyboard)


@router.message(moder_support_buy.wait_for_processing, Text(text="Отменить", text_ignore_case=True))
async def back_process(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(moder_support_buy.start)
    kb = [[types.KeyboardButton(text="Получить лот"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Получите лот для проверки или остановите проверку", reply_markup=keyboard)


@router.message(moder_support_buy.wait_for_processing)
async def unidentified_command(message: Message):
    await message.answer(text="Выберите один из пунктов")


@router.message(moder_support_buy.wait_message, Text(text="Отменить отправку", text_ignore_case=True))
async def back_sending(message: types.Message, state: FSMContext):
    await state.set_state(moder_support_buy.wait_for_processing)
    kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Доп информация"),
           types.KeyboardButton(text="Отправить сообщение"), types.KeyboardButton(text="Отменить")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Отправка сообщения отменена. Закончите обработку запроса", reply_markup=keyboard)


@router.message(moder_support_buy.wait_message)
async def unidentified_command(message: types.Message, state: FSMContext):
    await state.set_state(moder_support_buy.confirm_send_message)
    await state.update_data(send_text=message.text.lower())
    kb = [[types.KeyboardButton(text="Подтвердить"), types.KeyboardButton(text="Отменить отправку")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(f"Подтвердите, что пользователю нужно отправить данное сообщение\n\n{message.text.lower()}",
                         reply_markup=keyboard)


@router.message(moder_support_buy.confirm_send_message, Text(text="Подтвердить", text_ignore_case=True))
async def confirm_send_message(message: types.Message, state: FSMContext):
    await state.set_state(moder_support_buy.wait_for_processing)
    data = await state.get_data()
    await bot_buyers.send_message_to_buyer(data['id_buy'], data['send_text'])
    kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Доп информация"),
           types.KeyboardButton(text="Отправить сообщение"), types.KeyboardButton(text="Отменить")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Сообщение отправлено. Закончите обработку запроса", reply_markup=keyboard)


@router.message(moder_support_buy.confirm_send_message, Text(text="Отменить отправку", text_ignore_case=True))
async def back_sending(message: types.Message, state: FSMContext):
    await state.set_state(moder_support_buy.wait_for_processing)
    kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Доп информация"),
           types.KeyboardButton(text="Отправить сообщение"), types.KeyboardButton(text="Отменить")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Отправка сообщения отменена. Закончите обработку запроса", reply_markup=keyboard)


@router.message(moder_support_buy.confirm_send_message)
async def unidentified_command(message: types.Message):
    await message.answer("Выберите один из пунктов")


@router.message(moder_support_buy.confirm_proccess, Text(text="Подтвердить", text_ignore_case=True))
async def confirm_process(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await api_db.sql_bd_moderator.del_support_requerst_buy(data['number'], data['id_buy'])
    await state.clear()
    await state.set_state(moder_support_buy.start)
    kb = [[types.KeyboardButton(text="Обработать запрос"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Спасибо за обработку) Переходите к следующему запросу", reply_markup=keyboard)


@router.message(moder_support_buy.confirm_proccess, Text(text="Вернуться обработке", text_ignore_case=True))
async def back_to_process(message: types.Message, state: FSMContext):
    await state.set_state(moder_support_buy.wait_for_processing)
    kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Доп информация"),
           types.KeyboardButton(text="Отправить сообщение"), types.KeyboardButton(text="Отменить")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Отправка сообщения отменена. Закончите обработку запроса", reply_markup=keyboard)


@router.message(moder_support_buy.confirm_proccess)
async def confirm_process(message: Message, state: FSMContext):
    await message.answer(text="Выберите один из пунктов")
