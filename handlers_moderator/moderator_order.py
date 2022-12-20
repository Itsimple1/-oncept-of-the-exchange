from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

import api_db.sql_bd_moderator

router = Router()


class Moderator_order(StatesGroup):
    start = State()
    wait_make_a_verdict = State()
    confirm_choose_sell = State()
    confirm_choose_buy = State()


# Проверка заказа на правильность --------------------------------------------------
@router.message(Moderator_order.start, Text(text="Получить заказ", text_ignore_case=True))
async def get_order(message: Message, state: FSMContext):
    data = await api_db.sql_bd_moderator.get_moderator_order()
    if data is not None:
        await state.set_state(Moderator_order.wait_make_a_verdict)
        kb = [[types.KeyboardButton(text="Покупатель"), types.KeyboardButton(text="Продавец"),
               types.KeyboardButton(text="Получить доп информацию")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await state.update_data(number=data[0], id_buy=data[1], link=data[2], price=data[3], price_buy=data[4],
                                id_sel=data[5], price_sel=data[6])
        await message.answer(
            f"Проблема №{data[0]}\nID покупателя: {data[1]}\nID продавца: {data[5]}\n\nЗаказ: {data[2]}\n\nСтоимость "
            f"заказа: {data[3]}")
        await message.answer("Оцените данную ситуацию и вынесите решение, кто должен получить деньги\nЕсли заказ "
                             "существует, и его можно купить, то выберите покупателя\nЕсли заказ уже куплен или "
                             "недступен, то выберите продавца", reply_markup=keyboard)
    else:
        await state.clear()
        kb = [[types.KeyboardButton(text="Модерация"), types.KeyboardButton(text="Заявки на вывод"),
               types.KeyboardButton(text="Статистика"), types.KeyboardButton(text="Правила")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(text="На данный момент нет доступных для модерации заказов", reply_markup=keyboard)


@router.message(Moderator_order.start, Text(text="Меню", text_ignore_case=True))
async def menu(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="Модерация"), types.KeyboardButton(text="Заявки на вывод"),
           types.KeyboardButton(text="Статистика"), types.KeyboardButton(text="Правила")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Возвращаем вас в меню", reply_markup=keyboard)


@router.message(Moderator_order.start)
async def unrecognized_command(message: Message):
    await message.answer(text="Выберите один из пунктов")


@router.message(Moderator_order.wait_make_a_verdict, Text(text="Покупатель", text_ignore_case=True))
async def buyer_is_right(message: types.Message, state: FSMContext):
    await state.set_state(Moderator_order.confirm_choose_buy)
    kb = [[types.KeyboardButton(text="Подтвердить"), types.KeyboardButton(text="Вернуться к рассмотрению")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Подтвердите, что прав ПОКУПАТЕЛЬ и именно он должен получить возврат денег",
                         reply_markup=keyboard)


@router.message(Moderator_order.wait_make_a_verdict, Text(text="Продавец", text_ignore_case=True))
async def seller_is_right(message: types.Message, state: FSMContext):
    await state.set_state(Moderator_order.confirm_choose_sell)
    kb = [[types.KeyboardButton(text="Подтвердить"), types.KeyboardButton(text="Вернуться к рассмотрению")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Подтвердите, что прав ПРОДАВЕЦ и именно он должен получить деньги", reply_markup=keyboard)


@router.message(Moderator_order.wait_make_a_verdict, Text(text="Получить доп информацию", text_ignore_case=True))
async def dop_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(await api_db.sql_bd_moderator.dop_info_buy(data['id_buy']))
    await message.answer(await api_db.sql_bd_moderator.dop_info_sell(data['id_sel']))


@router.message(Moderator_order.wait_make_a_verdict, Text(text="Стоп", text_ignore_case=True))
async def stop(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Moderator_order.start)
    kb = [[types.KeyboardButton(text="Получить заказ"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(text="Получите заказ для проверки или остановите проверку", reply_markup=keyboard)


@router.message(Moderator_order.wait_make_a_verdict)
async def unrecognized_command(message: Message):
    await message.answer(text="Выберите один из пунктов")


@router.message(Moderator_order.confirm_choose_buy, Text(text="Подтвердить", text_ignore_case=True))
async def confirm_choose_buy(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await api_db.sql_bd_moderator.move_to_solved_problem_orders(data['number'], data['id_buy'], data['link'],
                                                                data['price'], data['price_buy'], data['id_sel'],
                                                                data['price_sel'], 'buy')
    await state.clear()
    await state.set_state(Moderator_order.start)
    kb = [[types.KeyboardButton(text="Получить заказ"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Спасибо за обработку) Переходите к следующему заказу", reply_markup=keyboard)


@router.message(Moderator_order.confirm_choose_buy, Text(text="Вернуться к рассмотрению", text_ignore_case=True))
async def back_to_process(message: types.Message, state: FSMContext):
    await state.set_state(Moderator_order.wait_make_a_verdict)
    kb = [[types.KeyboardButton(text="Покупатель"), types.KeyboardButton(text="Продавец"),
           types.KeyboardButton(text="Получить доп информацию")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Вынесите свой вердикт или отложите его")


@router.message(Moderator_order.confirm_choose_sell, Text(text="Подтвердить", text_ignore_case=True))
async def confirm_choose_sel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await api_db.sql_bd_moderator.move_to_solved_problem_orders(data['number'], data['id_buy'], data['link'],
                                                                data['price'], data['price_buy'], data['id_sel'],
                                                                data['price_sel'], 'sell')
    await state.clear()
    await state.set_state(Moderator_order.start)
    kb = [[types.KeyboardButton(text="Получить заказ"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Спасибо за обработку) Переходите к следующему заказу", reply_markup=keyboard)


@router.message(Moderator_order.confirm_choose_sell, Text(text="Вернуться к рассмотрению", text_ignore_case=True))
async def besk_to_process(message: types.Message, state: FSMContext):
    await state.set_state(Moderator_order.wait_make_a_verdict)
    kb = [[types.KeyboardButton(text="Покупатель"), types.KeyboardButton(text="Продавец"),
           types.KeyboardButton(text="Получить доп информацию")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Вынесите свой вердикт или отложите его")


@router.message(Moderator_order.confirm_choose_sell)
async def unrecognized_command(message: Message):
    await message.answer(text="Выберите один из пунктов")
