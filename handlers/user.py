import random
import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from langchain_core.messages import SystemMessage

import keyboards
from config_data.config import Config, load_config
from database import database
from gigachat_processing import create_story, prompts, gigachat

user_router = Router()
config: Config = load_config()


class StoryState(StatesGroup):
    waiting_for_names = State()


async def send_story(callback_or_message, state: FSMContext, genre=None, names=None, template_text="Вот ваша сказка:"):
    send_method = callback_or_message.message.answer \
        if isinstance(callback_or_message, CallbackQuery) else callback_or_message.answer
    tg_id = callback_or_message.from_user.id

    try:
        await database.process_user_query(tg_id)
    except Exception:
        await send_method(text='У вас закончились бесплатные генерации сказок! Вам необходимо купить подписку!',
                          reply_markup=keyboards.buy_sub())
        return

    genre = genre or "Обычная"
    story = create_story(genre, names=names)
    await state.update_data(story_type=genre)

    await send_method(text=f"{template_text}{story}", reply_markup=keyboards.after_story())


@user_router.message(CommandStart())
@user_router.message(F.text == 'Главное меню')
async def start_menu(message: Message, state: FSMContext):
    await database.add_user(message.from_user.id)
    await message.answer(text=f'Добро пожаловать в бота-сказочника, {message.from_user.first_name}',
                         reply_markup=keyboards.start_menu())
    await state.clear()


@user_router.callback_query(F.data == 'story_genres')
async def view_genres(callback: CallbackQuery):
    await callback.message.answer(text='Выберите жанр:',
                                  reply_markup=keyboards.genres())



@user_router.callback_query(F.data.startswith('genre'))
async def story_with_genre(callback: CallbackQuery, state: FSMContext):
    genre = callback.data.split(':')[1]
    await state.update_data(selected_genre=genre)
    await callback.message.answer("Введите имя или имена главных героев сказки:")
    await state.set_state(StoryState.waiting_for_names)


@user_router.callback_query(F.data == 'story_random')
async def story_random(callback: CallbackQuery, state: FSMContext):
    genre = random.choice(list(prompts.keys()))
    await state.update_data(selected_genre=genre)
    await callback.message.answer("Введите имя или имена главных героев сказки:")
    await state.set_state(StoryState.waiting_for_names)


@user_router.callback_query(F.data == 'story_default')
async def story_default(callback: CallbackQuery, state: FSMContext):
    await state.update_data(selected_genre=None)
    await callback.message.answer("Введите имя или имена главных героев сказки:")
    await state.set_state(StoryState.waiting_for_names)


@user_router.message(StateFilter(StoryState.waiting_for_names))
async def handle_names_input(message: Message, state: FSMContext):
    names = message.text.strip()
    fsm_data = await state.get_data()
    genre = fsm_data.get('selected_genre')
    await send_story(message, state, genre=genre, names=names)
    await state.clear()


@user_router.message(F.text == 'Создать еще одну сказку')
async def one_more_story(message: Message, state: FSMContext):
    fsm_data = await state.get_data()
    genre = fsm_data.get('story_type')
    await message.answer("Введите имя или имена главных героев сказки:")
    await state.set_state(StoryState.waiting_for_names)


@user_router.message(F.text == '/random_story')
async def random_story_command(message: Message, state: FSMContext):
    genre = random.choice(list(prompts.keys()))
    await state.update_data(selected_genre=genre)
    await message.answer("Введите имя или имена главных героев сказки:")
    await state.set_state(StoryState.waiting_for_names)


@user_router.message(F.text == '/select_genre_story')
async def select_genre_story_command(message: Message, state: FSMContext):
    await message.answer(text='Выберите жанр:', reply_markup=keyboards.genres())


@user_router.callback_query(F.data == 'lc')
async def user_info(callback: CallbackQuery):
    user_info = await database.get_user_data(callback.from_user.id)
    is_premium = bool(user_info[2])
    text = f'Информация о пользователе:\nusername: @{callback.from_user.username}\nОсталось запросов: '
    text += 'неограничено' if is_premium else f'{user_info[1]} из 5'

    kb = None if is_premium else keyboards.buy_sub()
    await callback.message.answer(text=text, reply_markup=kb)


@user_router.callback_query(F.data == 'sub')
async def buy_sub(callback: CallbackQuery):
    payment_id = str(uuid.uuid4())
    await callback.message.answer_invoice(
        title='Подписка на безлимитные сказки',
        description='Подписка на безлимитные сказки',
        payload=payment_id,
        provider_token=config.payment_token,
        currency='RUB',
        prices=[LabeledPrice(label='Оплата услуг', amount=29990)])
    await callback.message.answer(text='Номер тест-карты: 4000 0000 0000 0408, остальные данные на рандом')


@user_router.pre_checkout_query()
async def process_pre_checkout_query(query: PreCheckoutQuery):
    await query.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


@user_router.message(F.successful_payment)
async def success_payment_handler(message: Message):
    await database.set_premium(message.from_user.id)
    await message.answer(text='Спасибо за покупку подписки!🤗\nТеперь вы можете неограничено пользоваться ботом!')
