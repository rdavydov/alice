# TZ='Europe/Moscow'

import logging
from flask import Flask, request
import json
import sqlite3
import sys
import io

# import time  # Добавляем импорт библиотеки time

# Установка кодировки UTF-8 для консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)

# Настроим логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Проверим, существует ли таблица "users", и создадим её, если нет
conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        password TEXT,
        name TEXT
    )
''')
conn.commit()

# Функции
# ---------------------------------
def create_user(user_id, password, name):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, password, name) VALUES (?, ?, ?)", (user_id, password, name))
    conn.commit()
    conn.close()

def check_password(password):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE password=?", (password,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return False
    return result[0]

def pretty_print(data):
    return json.dumps(data, ensure_ascii=False, indent=4)
# ---------------------------------

# Тестовые пользователи
# Вызовы create_user расскоментировать при первом запуске приложения
# для того, чтобы пользователи добавились в БД
# при последующих запусках - закомментировать обратно
########################################
# create_user('1', 'орлан', 'Роман')
# create_user('2', 'ястреб', 'Иван')
# create_user('3', 'барс', 'Пётр')
########################################
'''
@app.route('/alice', methods=['POST'])
def main():
    # logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    # logging.info(f'Response:  {response!r}')
    return json.dumps(response)

def handle_dialog(req, res): # диалог с пользователем
    user_id = req['session']['user_id']
    if req['session']['new']: # новая сессия
        res['response'][
            'text'] = 'Привет! Я тестовый навык для Алисы! ' + \
            'Я могу идентифицировать пользователей!'
        return

    try: # на всякий случай)
        if list(map(lambda x: x.lower(), req['request']['nlu']['tokens'])) == ['закончить', 'диалог'] or \
           list(map(lambda x: x.lower(), req['request']['nlu']['tokens'])) == ['завершить', 'диалог']:
            res['response']['text'] = 'Пока! Возвращайся снова!'
            res['response']['tts'] = 'Пока! Возвращайся снова!'
            res['response']['end_session'] = True
            return
    except Exception:
        pass
    try:
        # что ты умеешь? - обязательный вопрос в навыке Алисы
        if list(map(lambda x: x.lower(), req['request']['nlu']['tokens'])) == ['что', 'ты', 'умеешь'] or \
           list(map(lambda x: x.lower(), req['request']['nlu']['tokens'])) == ['помощь']:
            res['response']['text'] = 'Я умею идентифицировать пользователей ' + \
                'по тем кодовым словам (паролям), которые они мне назовут'
            return
    except Exception:
        pass
    try:
        name = check_password(req['request']['command'])
        if name:
            res['response']['text'] = f'Пароль верный, привет, {name}!'
        else:
            res['response']['text'] = 'Пароль неверный'
        return
    except Exception as e:
        # res['response']['text'] = "Не совсем тебя поняла."
        res['response']['text'] = f"Не совсем тебя поняла. Исключение: {e}"
'''
@app.route('/alice', methods=['POST'])
def alice():
    data = request.json
    user_id_request = data['session']['user_id']

    # Задержка в 5 секунд
    # time.sleep(5)

    res = None  # Инициализируем переменную res

    if data['request'] and data['request']['command'] and len(data['request']['command']) > 0:
        input_text = data['request']['command']
        logging.info(f"input_text: {input_text}")

        # что ты умеешь? - обязательный вопрос в навыке Алисы
        if list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['что', 'ты', 'умеешь'] or \
           list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['помощь']:
            res = {
                'version': data['version'],
                'session': data['session'],
                'response': {
                    'text': 'Я умею идентифицировать пользователей ' + \
                'по тем кодовым словам (паролям), которые они мне назовут',
                    'end_session': False
                }
            }
            return json.dumps(res)

        if check_password(input_text):
            name = check_password(input_text)
            res = {
                'version': data['version'],
                'session': data['session'],
                'response': {
                    'text': f'Пароль верный, привет, {name}!',
                    'end_session': False
                }
            }
            return json.dumps(res)
        else:
            res = {
                'version': data['version'],
                'session': data['session'],
                'response': {
                    'text': 'Пароль неверный',
                    'end_session': False
                }
            }
            return json.dumps(res)

    # Выведем запрос в консоль с отступами и новыми строками
    logging.debug("---------- Request ----------")
    logging.debug(f"User ID (from request): {user_id_request}")
    logging.debug(pretty_print(data))

    # Выведем ответ в консоль с отступами и новыми строками
    logging.debug("---------- Response ----------")
    logging.debug(pretty_print(res))

    if res is None:
        res = {
            'version': data['version'],
            'session': data['session'],
            'response': {
                'text': 'Для идентификации мне нужен ваш пароль',
                'end_session': False
            }
        }

    return json.dumps(res)


if __name__ == '__main__':
    # con = sqlite3.connect('data_covid.db', check_same_thread=False)  # база данных
    # cur = con.cursor()
    app.run(host='0.0.0.0', port=80)