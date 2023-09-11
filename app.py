import logging
from flask import Flask, request
import json
import sqlite3

app = Flask(__name__)

# Настроим логирование
logging.basicConfig(level=logging.DEBUG)

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
    user_id_application = data['application']['application_id']
    user_id_request = data['session']['user_id']
    text = data['request']['original_utterance']

    # Выведем запрос в консоль с отступами и новыми строками
    logging.debug("---------- Request ----------")
    logging.debug(f"User ID (from application): {user_id_application}")
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

    if data['session']['new']:
        # Пользователь новый, создаем аккаунт
        create_user(user_id_request, text)  # Вызываем функцию для создания пользователя
        res = {
            'version': data['version'],
            'session': data['session'],
            'response': {
                'text': 'Пароль принят, добро пожаловать!',
                'end_session': False
            }
        }
    else:
        if check_password(user_id_request, text):
            res = {
                'version': data['version'],
                'session': data['session'],
                'response': {
                    'text': 'Пароль принят, добро пожаловать!',
                    'end_session': False
                }
            }
        else:
            res = {
                'version': data['version'],
                'session': data['session'],
                'response': {
                    'text': 'Неверный пароль. Попробуйте еще раз или введите пароль заново.',
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
