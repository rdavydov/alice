# TZ='Europe/Moscow'

import logging
from flask import Flask, request
import json
import sqlite3
import sys
import io

# Установка кодировки UTF-8 для консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


app = Flask(__name__)

# Настроим логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def create_user(user_id, password):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, password) VALUES (?, ?)", (user_id, password))
    conn.commit()
    conn.close()

def check_password(user_id, password):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return False
    return result[0] == password

import json

# ...

def pretty_print(data):
    return json.dumps(data, ensure_ascii=False, indent=4)

@app.route('/alice', methods=['POST'])
def alice():
    data = request.json
    user_id_request = data['session']['user_id']
    text = data['request']['original_utterance']

    # Выведем запрос в консоль с отступами и новыми строками
    logging.debug("---------- Request ----------")
    logging.debug(f"User ID (from request): {user_id_request}")
    logging.debug(pretty_print(data))

    # Проверим, существует ли таблица "users", и создадим её, если нет
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()

    if data['request'] and data['request']['original_utterance'] and len(data['request']['original_utterance']) > 0:
        text = data['request']['original_utterance']
    res = {
        'version': data['version'],
        'session': data['session'],
        'response': {
            'text': text,
            'end_session': False
        }
    }


    # Выведем ответ в консоль с отступами и новыми строками
    logging.debug("---------- Response ----------")
    logging.debug(pretty_print(res))

    conn.close()  # Закрываем соединение с базой данных
    return json.dumps(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
