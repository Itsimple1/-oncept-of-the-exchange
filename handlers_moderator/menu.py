from aiogram import Router, types
from aiogram.types import Message
from aiogram.dispatcher.filters.text import Text
from aiogram.dispatcher.fsm.context import FSMContext

import handlers_moderator.moder_support_buy
import handlers_moderator.moder_support_sel
import handlers_moderator.moder_dring_up
import handlers_moderator.moderator_order
import api_db.sql_bd_moderator

router = Router()


@router.message(Text(text="Модерация", text_ignore_case=True))
async def moderation_start(message: Message):
    kb = [[types.KeyboardButton(text="Модерация заказов"), types.KeyboardButton(text="Sup_buy"),
           types.KeyboardButton(text="Sup_sel"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Получите заказ для проверки или остановите проверку", reply_markup=keyboard)


@router.message(Text(text="Модерация заказов", text_ignore_case=True))
async def moderation(message: Message, state: FSMContext):
    await state.set_state(handlers_moderator.moderator_order.Moderator_order.start)
    kb = [[types.KeyboardButton(text="Получить заказ"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Получите заказ для проверки или остановите проверку", reply_markup=keyboard)


@router.message(Text(text="Sup_buy", text_ignore_case=True))
async def support_buy(message: Message, state: FSMContext):
    await state.set_state(handlers_moderator.moder_support_buy.moder_support_buy.start)
    kb = [[types.KeyboardButton(text="Обработать запрос"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Получите заказ для проверки или остановите проверку", reply_markup=keyboard)


@router.message(Text(text="Sup_sel", text_ignore_case=True))
async def support_sel(message: Message, state: FSMContext):
    await state.set_state(handlers_moderator.moder_support_sel.moder_support_sel.start)
    kb = [[types.KeyboardButton(text="Обработать запрос"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Получите заказ для проверки или остановите проверку", reply_markup=keyboard)


@router.message(Text(text="Заявки на вывод", text_ignore_case=True))
async def applications_dring_up(message: Message, state: FSMContext):
    await state.set_state(handlers_moderator.moder_dring_up.Moder_dring_up.start)
    kb = [[types.KeyboardButton(text="Обработать заявку"), types.KeyboardButton(text="Меню")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(text="Обработайте заявку на вывод или вернитесь в меню", reply_markup=keyboard)


@router.message(Text(text="Статистика"))
async def statistic(message: Message):
    await message.answer(await api_db.sql_bd_moderator.get_statistic_info())


@router.message(Text(text="Правила", text_ignore_case=True))
async def rules(message: Message):
    await message.answer(open("texts/pravila_for_moderator.txt", 'r', encoding='utf-8').read())


@router.message(commands=["start"])
async def cmd_start(message: Message):
    kb = [[types.KeyboardButton(text="Модерация"), types.KeyboardButton(text="Заявки на вывод"),
           types.KeyboardButton(text="Статистика"), types.KeyboardButton(text="Правила")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(open("texts/pravila_for_moderator.txt", 'r', encoding='utf-8').read(), reply_markup=keyboard)


@router.message()
async def unidentified(message: Message):
    kb = [[types.KeyboardButton(text="Модерация"), types.KeyboardButton(text="Заявки на вывод"),
           types.KeyboardButton(text="Статистика"), types.KeyboardButton(text="Правила")], ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Нераспознанная команда", reply_markup=keyboard)
