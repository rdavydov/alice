# TZ='Europe/Moscow'

import logging
from flask import Flask, request
import json
import random
import sys
import io

# import time  # Добавляем импорт библиотеки time

# Установка кодировки UTF-8 для консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

# Add this BEFORE creating the Flask app
class ReverseProxied:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        return self.app(environ, start_response)

app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)  # Add this line after creating app

# Настроим логирование
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Функции
# ---------------------------------
def is_int(data):
    try:
        int(data)
        return True
    except ValueError:
        return False

def generate_poem():
    with open('config/dict.json', 'r', encoding='utf-8') as dict_file:
        vocabular = json.load(dict_file)

    random_values = []

    for i in range(len(vocabular)):
        random_values.append(random.choice(vocabular[i]))

    with open('config/structure.json', 'r', encoding='utf-8') as structure_file:
        structure = json.load(structure_file)

    poem = []

    for i in range(len(structure)):
        element = ""
        for j in range(len(structure[i])):
            if is_int(structure[i][j]):
                element += random_values[structure[i][j]] + " "
            else:
                element += structure[i][j] + " "
        poem.append(element.rstrip())  # Удаление лишних пробелов в конце строки

    return poem

def pretty_print(data):
    return json.dumps(data, ensure_ascii=False, indent=4)
# ---------------------------------


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

        try: # на всякий случай)
            if list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['закончить', 'диалог'] or \
            list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['пока'] or \
            list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['всё'] or \
            list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['хватит'] or \
            list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['стоп'] or \
            list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['надоело'] or \
            list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['остановись'] or \
            list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['завершить', 'диалог']:
                res = {
                    'version': data['version'],
                    'session': data['session'],
                    'response': {
                        'text': 'Пока! Возвращайся за новыми стихами!',
                        'end_session': True
                    }
                }
                return json.dumps(res)
        except Exception:
            pass

        # что ты умеешь? - обязательный вопрос в навыке Алисы
        if list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['что', 'ты', 'умеешь'] or \
           list(map(lambda x: x.lower(), data['request']['nlu']['tokens'])) == ['помощь']:
            res = {
                'version': data['version'],
                'session': data['session'],
                'response': {
                    'text': 'Я - стихоплёт! Создаю стихи по одному известному демотиватору. Такие стихи плету, закачаешься! Скажи мне любое слово, а в ответ получишь стих! Если надоем, то скажи "стоп" или "хватит". Приятного стихопрослушивания!',
                    'end_session': False
                }
            }
            return json.dumps(res)

        poem = '\n'.join(generate_poem())
        logging.info(f"poem:\n{poem}")

        res = {
            'version': data['version'],
            'session': data['session'],
            'response': {
                'text': f'{poem}',
                'tts': f'{poem}',
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
                'text': 'Я - стихоплёт! Создаю стихи по одному известному демотиватору. Такие стихи плету, закачаешься! Скажи мне любое слово, а в ответ получишь стих! Если надоем, то скажи "стоп" или "хватит". Приятного стихопрослушивания!',
                'end_session': False
            }
        }

    return json.dumps(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
