import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

import hero
from hero import heroes
import sqlite3
import keyboatds
from aiogram import F, Router, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()
dp = Dispatcher()


class User(StatesGroup):
    username = State()
    win = State()
    lose = State()
    steam_id = State()
    rank = State()
    # def __init__(self, steam_id, rank):
    #     self.steam_id = steam_id
    #     self.rank = rank


user = User()


@router.message(Command('start'))
async def command_start(message: Message):
    await message.reply(
        f'Привет! {message.from_user.first_name} это первый тестовый бот! Подробная информация /help ')


@router.message(Command('help'))
async def command_help(message: Message):
    await message.reply('Для того чтобы вывести информацию об аккаунте, напишите /reg ')


@router.message(Command('reg'))
async def command_reg(message: Message, state: FSMContext):
    await state.set_state(User.username)
    await message.answer('Введите свой nick_name: ')
    # req = requests.get(f'https://api.opendota.com/api/players/{message.text.}/wl')


@router.message(User.username)
async def user_name_add(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(User.steam_id)
    data = await state.get_data()
    user.username = data['username']
    await message.answer('Введите id-аккаунта: ')


@router.message(User.steam_id)
async def steam_id_add(message: Message, state: FSMContext):
    await state.update_data(steam_id=message.text)
    data = await state.get_data()
    user.steam_id = data['steam_id']
    is_user_inserted = insert_user(user)
    if is_user_inserted:
        await message.answer(f'Ваш steam id:{user.steam_id}')
        await message.answer(requests.get(f'https://api.opendota.com/api/players/{user.steam_id}').text,
                             reply_markup=keyboatds.menu)

    else:
        await message.answer('Такой пользователь уже существует.', reply_markup=keyboatds.menu)
    await state.clear()


@router.message(Command('win'))
async def command_w_l(message: Message):
    response = requests.get(f'https://api.opendota.com/api/players/{user.steam_id}/wl').json()
    user.win = response['win']
    user.lose = response['lose']
    await message.answer(
        f'🎲Игр: {user.win + user.lose}\n⚡Побед: {user.win}\n🗿Поражений: {user.lose}\n🚀Винерейт: {round(user.win / (user.win + user.lose) * 100, 2)}%',
        reply_markup=keyboatds.menu)


@router.message(Command('rank'))
async def get_rank(message: Message):
    response = requests.get(f'https://api.opendota.com/api/players/{user.steam_id}').json()
    user.rank = response['rank_tier']
    await message.answer('Ваш ранг: ')
    if (int(user.rank) // 10) != 8:
        await message.answer(get_rank_stars(int(user.rank)))
    await message.answer_photo(get_rank_title(int(user.rank)))
    await message.answer('Выберите пункт: ',
                         reply_markup=keyboatds.menu)


@router.message(Command('users'))
async def get_users(message: Message):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users;')
        await message.answer(str(cursor.fetchall()))


@router.message(Command('totals'))
async def get_totals(message: Message):
    re = requests.get(f'https://api.opendota.com/api/players/{user.steam_id}/totals').json()
    await message.answer(
        f'🩸Всего убийств: {str(re[0]['sum'])}\n⚰Смертей: {re[1]['sum']}\n🚑Ассистов: {re[2]['sum']}\n🤜Denies: {re[8]['sum']}\n🥊hero_damage: {re[12]['sum']}\n'
        f'🏡tower_damage: {re[13]['sum']}', reply_markup=keyboatds.menu)


@router.message(Command('stat_all_math'))
async def get_hero_game_top(message: Message):
    re = requests.get(f'https://api.opendota.com/api/players/{user.steam_id}/heroes').json()
    hero_name = str()
    hero_page = ''
    for i in hero.heroes:
        if i['id'] == re[0]['hero_id']:
            hero_name = i['name']
            hero_page = i['page']

    win_rate_hero = round((re[0]['win'] / re[0]['games']) * 100, 2)
    await message.answer_photo(photo=str(hero_page), caption=str(f'Больше всего игр: {hero_name}\n'
                             f'🎲Игр: {re[0]['games']}\n'
                             f'⚡Побед: {re[0]['win']}\n'
                             f'🗿Поражений: {re[0]['games'] - re[0]['win']}\n'
                             f'🚀Винрейт: {win_rate_hero}'),
                             reply_markup=keyboatds.menu)



def get_rank_stars(rank: int):
    return "⭐" * (rank % 10)


def get_rank_title(rank: int):
    names = {
        1: 'https://www.vikingdota.com/cdn/shop/collections/SeasonalRank1-0_250x.png?v=1616514498',
        2: 'https://www.vikingdota.com/cdn/shop/collections/SeasonalRank2-5_250x.png?v=1616514574',
        3: 'https://www.vikingdota.com/cdn/shop/collections/160px-SeasonalRank3-5_250x.png?v=1616514558',
        4: 'https://www.vikingdota.com/cdn/shop/collections/SeasonalRank4-5_250x.png?v=1616514409',
        5: 'https://www.vikingdota.com/cdn/shop/collections/160px-SeasonalRank5-5_250x.png?v=1616514343',
        6: 'https://www.vikingdota.com/cdn/shop/collections/SeasonalRank6-5_250x.png?v=1616514480',
        7: 'https://www.vikingdota.com/cdn/shop/collections/160px-SeasonalRank7-5_250x.png?v=1616514394',
        8: 'https://www.vikingdota.com/cdn/shop/collections/mmr_boosting_water_mark_480x480_b253f2db-ec10-45d4-88d3-3ffb40498387_250x.png?v=1616514441'
    }

    return names[rank // 10]


def insert_user(user):
    with sqlite3.connect('database.db') as conn:
        is_user_inserted = False
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO users (steam_id, username) VALUES ({int(user.steam_id)},'{str(user.username)}');")
            conn.commit()
            is_user_inserted = True
        except sqlite3.Error:
            is_user_inserted = False
            pass
        return is_user_inserted


@router.callback_query(F.data == 'rank')
async def get_ranks(callback: CallbackQuery):
    await get_rank(callback.message)
    await callback.answer()


@router.callback_query(F.data == 'win_rate')
async def get_winrate(callback: CallbackQuery):
    await command_w_l(callback.message)
    await callback.answer()


@router.callback_query(F.data == 'users')
async def get_history(callback: CallbackQuery):
    await get_users(callback.message)
    await callback.answer()


@router.callback_query(F.data == 'totals')
async def get_history(callback: CallbackQuery):
    await get_totals(callback.message)
    await callback.answer()


@router.callback_query(F.data == 'hero_game_top')
async def get_top_math(callback: CallbackQuery):
    await get_hero_game_top(callback.message)
    await callback.answer()
# @router.callback_query(F.data == 'registrate')
# async def callback_reg(message: Message, state: FSMContext, callback: CallbackQuery):
#     await command_reg(message, state)
#     await callback.answer()
