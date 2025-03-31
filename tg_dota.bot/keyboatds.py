from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

registration = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Регистрация', callback_data='registrate')], [
        InlineKeyboardButton(text='Пользователи', callback_data='users')
    ]])

menu = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Статистика', callback_data='win_rate')], [
        InlineKeyboardButton(text='rank', callback_data='rank')
    ], [
                         InlineKeyboardButton(text='Вся статистика', callback_data='totals')
                     ], [InlineKeyboardButton(text='Больше всего игр', callback_data='hero_game_top')],[
                         InlineKeyboardButton(text='История пользователей:', callback_data='users')
                     ]])
