from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from database import get_quiz_index, update_quiz_index
from quiz_data import quiz_data

router = Router(name=__name__)

correct_answer = 0
incorrect_answer = 0

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    global correct_answer
    correct_answer += 1
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    # Отображение сообщения выбраного пользователем
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Сохранение процесса"))

    await callback.message.answer(f"✅ Верно! Это {quiz_data[current_question_index]['options'][correct_option]}", reply_markup=builder.as_markup(resize_keyboard=True))
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("💯 Это был последний вопрос. Квиз завершен!")


@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    global incorrect_answer
    incorrect_answer += 1
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Сохранение процесса"))

    await callback.message.answer(f"❌ Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}", reply_markup=builder.as_markup(resize_keyboard=True))

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("💯 Это был последний вопрос. Квиз завершен!")


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


@router.message(F.text == "Сохранение процесса")
@router.message(Command("save"))
async def cmd_save(message: types.Message):

    await save(message)
    await message.answer(f"Сохранение прошло успешно!")
    await stat(message)


async def save(message):
    user_id = message.from_user.id
    current_question_index = await get_quiz_index(user_id)
    await update_quiz_index(user_id, current_question_index)


async def stat(message):
    user_id = message.from_user.id
    current_question_index = await get_quiz_index(user_id)
    len_of_questions = len(quiz_data)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Продолжить квиз"))
    await message.answer(f"Ваш текущий процесс: {current_question_index / len_of_questions * 100}% квиза пройдено!\n"
                         f"Правильных ответов: {correct_answer} 😃\n"
                         f"Неправильных ответов: {incorrect_answer} ☹️",
                         reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(F.text == "Продолжить квиз")
@router.message(Command("continue"))
async def cmd_continue(message: types.Message):
    user_id = message.from_user.id
    await get_question(message, user_id)


async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)
