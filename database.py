import aiosqlite

DB_NAME = 'quiz_bot.db'


async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, correct_answer INTEGER, incorrect_answer INTEGER)''')
        # Сохраняем изменения
        await db.commit()


async def get_quiz_stat(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index, correct_answer, incorrect_answer FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results
            else:
                return 0


async def update_quiz_index(user_id, index, correct_answer, incorrect_answer):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, correct_answer, incorrect_answer) VALUES (?, ?, ?, ?)', (user_id, index, correct_answer, incorrect_answer))
        # Сохраняем изменения
        await db.commit()