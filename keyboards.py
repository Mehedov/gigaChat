from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gigachat_processing import prompts


def start_menu():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Создать сказку', callback_data='story_default'))  # Дефолтный промт
    kb.row(InlineKeyboardButton(text='Выбрать жанр', callback_data='story_genres'),  # Заготовки промтов
           InlineKeyboardButton(text='Случайный жанр', callback_data='story_random'))  # Случайная заготовка
    kb.row(InlineKeyboardButton(text='Помощь', url='https://telegra.ph/Instrukciya-po-polzovaniyu-botom-skazochnikom-12-01'))  # Инструкция, там же и про оплату
    kb.row(InlineKeyboardButton(text='Личный кабинет', callback_data='lc'),  # Сколько осталось запросов
           InlineKeyboardButton(text='Купить подписку', callback_data='sub'))
    return kb.as_markup()


def genres():
    kb = InlineKeyboardBuilder()
    genres_list = prompts.keys()
    for genre in genres_list:
        kb.add(InlineKeyboardButton(text=genre, callback_data=f'genre:{genre}'))
    kb.adjust(2)
    return kb.as_markup()


def after_story():
    kb = [[KeyboardButton(text='Создать еще одну сказку')], [KeyboardButton(text='Главное меню')]]
    return ReplyKeyboardMarkup(keyboard=kb, one_time_keyboard=True)


def buy_sub():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Купить подписку', callback_data='sub'))
    kb.row(InlineKeyboardButton(text='Помощь', url='https://telegra.ph/Instrukciya-po-polzovaniyu-botom-skazochnikom-12-01'))  # Инструкция, там же и про оплату
    return kb.as_markup()