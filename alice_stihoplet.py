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

app = Flask(__name__)

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
                        'text': 'Пока! Возвращайся снова!',
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
                    'text': 'Я - стихоплёт! Такие стихи плету, закачаешься! Скажи мне что-нибудь, а в ответ получишь стих!',
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
                'text': 'Я - стихоплёт. Скажи мне что-нибудь, а в ответ получишь стих!',
                'end_session': False
            }
        }

    return json.dumps(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)