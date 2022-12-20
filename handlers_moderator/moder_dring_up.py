from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

import api_db.sql_bd_moderator

router = Router()


class Moder_dring_up(StatesGroup):
    start = State()
    wait_for_processing = State()
    confirm_proccess = State()
    confirm_ban = State()


# Проверка лота на правильность --------------------------------------------------
@router.message(Moder_dring_up.start, Text(text="Обработать заявку", text_ignore_case=True))
async def process_application(message: Message, state: FSMContext):
    data = await api_db.sql_bd_moderator.get_moderator_dring_up(message.from_user.id)
    if data is not None:
        await state.set_state(Moder_dring_up.wait_for_processing)
        history_orders = await api_db.sql_bd_moderator.get_history_orders(data[1])
        kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Получить доп информацию"),
               types.KeyboardButton(text="Бан"), types.KeyboardButton(text="Отмена")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await state.update_data(number=data[0], id_sel=data[1], amount=data[2], requisites=data[3],
                                history_orders=history_orders)
        await message.answer(
            f"Заявка на вывод №{data[0]}\nID продавца: {data[1]}\nСумма вывода: {data[2]}\n\nРеквизиты: {data[3]}")
        score = 0
        text = "История заказов:\n"
        for i in history_orders:
            text += f"{i[0]}   {i[1]}   {i[2]}\n"
            score += i[2]
        text += f"\nИтоговая сумма: {score}"
        await message.answer(text)
        await message.answer("Проверьте заявку, а затем переведите деньги продавцу и нажмите выполнил",
                             reply_markup=keyboard)
    else:
        await state.clear()
        kb = [[types.KeyboardButton(text="Модерация"), types.KeyboardButton(text="Заявки на вывод"),
               types.KeyboardButton(text="Статистика"), types.KeyboardButton(text="Правила")], ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer(text="На данный момент нет заявок на вывод", reply_markup=keyboard)


@router.message(Moder_dring_up.start, Text(text="Меню", text_ignore_case=True))
async def menu(message: Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="Модерация"), types.KeyboardButton(text="Заявки на вывод"),
           types.KeyboardButton(text="Статистика"), types.KeyboardButton(text="Правила")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Возвращаем вас в меню", reply_markup=keyboard)


@router.message(Moder_dring_up.start)
async def unidentified_process(message: Message):
    await message.answer(text="Выберите один из пунктов")


@router.message(Moder_dring_up.wait_for_processing, Text(text="Обработал", text_ignore_case=True))
async def complete_application(message: types.Message, state: FSMContext):
    await state.set_state(Moder_dring_up.confirm_proccess)
    kb = [[types.KeyboardButton(text="Подтвердить"), types.KeyboardButton(text="Вернуться к рассмотрению")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Подтвердите, что перевели деньги продавцу", reply_markup=keyboard)


@router.message(Moder_dring_up.wait_for_processing, Text(text="Получить доп информацию", text_ignore_case=True))
async def get_dop_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(await api_db.sql_bd_moderator.dop_info_sell(data['id_sel']))


@router.message(Moder_dring_up.wait_for_processing, Text(text="Бан", text_ignore_case=True))
async def ban_user(message: types.Message, state: FSMContext):
    await state.set_state(Moder_dring_up.confirm_ban)
    kb = [[types.KeyboardButton(text="Подтвердить"), types.KeyboardButton(text="Отмена")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Подтвердите, что хотите заблокировать данного пользоавтеля", reply_markup=keyboard)


@router.message(Moder_dring_up.wait_for_processing, Text(text="Отмена", text_ignore_case=True))
async def back_process(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Moder_dring_up.start)
    kb = [[types.KeyboardButton(text="Обработать заявку"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer(text="Получите заявку для проверки или остановите проверку", reply_markup=keyboard)


@router.message(Moder_dring_up.wait_for_processing)
async def unidentified_in_wait_process(message: Message):
    kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Получить доп информацию"),
           types.KeyboardButton(text="Бан"), types.KeyboardButton(text="Отмена")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Выберите один из пунктов", reply_markup=keyboard)


@router.message(Moder_dring_up.confirm_proccess, Text(text="Подтвердить", text_ignore_case=True))
async def confirm_process(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await api_db.sql_bd_moderator.move_to_complete_dring_up(data['number'], data['id_sel'], data['amount'],
                                                            data['requisites'], data['history_orders'])
    await state.clear()
    await state.set_state(Moder_dring_up.start)
    kb = [[types.KeyboardButton(text="Обработать заявку"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Спасибо за обработку) Переходите к следующему лоту", reply_markup=keyboard)


@router.message(Moder_dring_up.confirm_proccess, Text(text="Вернуться к рассмотрению", text_ignore_case=True))
async def back_to_process(message: types.Message, state: FSMContext):
    await state.set_state(Moder_dring_up.wait_for_processing)
    kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Получить доп информацию"),
           types.KeyboardButton(text="Бан"), types.KeyboardButton(text="Отмена")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Закончите обработку заказа", reply_markup=keyboard)


@router.message(Moder_dring_up.confirm_proccess)
async def unidentified_confirm_process(message: Message):
    await message.answer(text="Выберите один из пунктов")


@router.message(Moder_dring_up.confirm_ban, Text(text="Подтвердить", text_ignore_case=True))
async def confirm_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await api_db.sql_bd_moderator.complete_ban_user(data['id_sel'])
    await state.set_state(Moder_dring_up.start)
    kb = [[types.KeyboardButton(text="Обработать заявку"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите услугу")
    await message.answer("Спасибо за обработку) Переходите к следующему лоту", reply_markup=keyboard)


@router.message(Moder_dring_up.confirm_ban, Text(text="Отмена", text_ignore_case=True))
async def back_process(message: Message, state: FSMContext):
    await state.set_state(Moder_dring_up.wait_for_processing)
    kb = [[types.KeyboardButton(text="Обработал"), types.KeyboardButton(text="Получить доп информацию"),
           types.KeyboardButton(text="Бан"), types.KeyboardButton(text="Отмена")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Закончите обработку заказа", reply_markup=keyboard)


@router.message(Moder_dring_up.confirm_ban)
async def unidentified_confirm_ban(message: Message):
    await message.answer(text="Выберите один из пунктов")
