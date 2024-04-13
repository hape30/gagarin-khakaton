
import sqlite3
from sqlite3 import Error

# Создаем подключение к базе данных
conn = sqlite3.connect('stydents.db')
cursor = conn.cursor()

# Создаем таблицу для хранения информации о пользователях
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT
                )''')



def register_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Проверяем, нет ли уже пользователя с таким именем
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    if cursor.fetchone():
        return('Пользователь с таким именем уже существует')
    else:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return('Пользователь зарегистрирован успешно')



