# TZ='Europe/Moscow'

import logging
from flask import Flask, request
import json
import random
import sys
import io

# Установка кодировки UTF-8 для консоли
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

# Middleware to handle reverse proxy
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
app.wsgi_app = ReverseProxied(app.wsgi_app)

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
    try:
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
    except Exception as e:
        logging.error(f"Error generating poem: {str(e)}")
        return ["Произошла ошибка при генерации стиха"]

def pretty_print(data):
    return json.dumps(data, ensure_ascii=False, indent=4)

def get_tokens(data):
    """Safely extract tokens from request"""
    try:
        # Try to get tokens from NLU
        return data['request']['nlu']['tokens']
    except KeyError:
        try:
            # Fallback to splitting command text
            command = data['request']['command']
            return command.split() if command else []
        except KeyError:
            return []
# ---------------------------------

# Define phrase lists for better maintainability
STOP_PHRASES = [
    ['закончить', 'диалог'],
    ['пока'],
    ['всё'],
    ['хватит'],
    ['стоп'],
    ['надоело'],
    ['остановись'],
    ['завершить', 'диалог']
]

HELP_PHRASES = [
    ['что', 'ты', 'умеешь'],
    ['помощь']
]

@app.route('/alice', methods=['POST'])
def alice():
    try:
        data = request.json
        if not data:
            logging.error("Received empty request")
            return json.dumps({
                'version': '1.0',
                'response': {'text': 'Ошибка: пустой запрос', 'end_session': False}
            }), 400

        # Safely get session and user ID
        session = data.get('session', {})
        user_id_request = session.get('user_id', 'unknown')
        
        res = None
        request_data = data.get('request', {})
        command = request_data.get('command', '')
        
        # Log request immediately for debugging
        logging.debug("---------- Request ----------")
        logging.debug(f"User ID: {user_id_request}")
        logging.debug(pretty_print(data))

        # Process tokens safely
        tokens = get_tokens(data)
        token_list_lower = [token.lower() for token in tokens]

        # Check for stop phrases
        if token_list_lower in STOP_PHRASES:
            res = {
                'version': data.get('version', '1.0'),
                'session': session,
                'response': {
                    'text': 'Пока! Возвращайся за новыми стихами!',
                    'end_session': True
                }
            }
        
        # Check for help phrases
        elif token_list_lower in HELP_PHRASES:
            res = {
                'version': data.get('version', '1.0'),
                'session': session,
                'response': {
                    'text': 'Я - стихоплёт! Создаю стихи по одному известному демотиватору. Такие стихи плету, закачаешься! Скажи мне любое слово, а в ответ получишь стих! Если надоем, то скажи "стоп" или "хватит". Приятного стихопрослушивания!',
                    'end_session': False
                }
            }
        
        # Generate poem if we have a command
        elif command:
            logging.info(f"Command received: {command}")
            poem = '\n'.join(generate_poem())
            logging.info(f"Generated poem:\n{poem}")
            
            res = {
                'version': data.get('version', '1.0'),
                'session': session,
                'response': {
                    'text': poem,
                    'tts': poem,
                    'end_session': False
                }
            }
        
        # Fallback to help message
        if res is None:
            res = {
                'version': data.get('version', '1.0'),
                'session': session,
                'response': {
                    'text': 'Я - стихоплёт! Создаю стихи по одному известному демотиватору. Такие стихи плету, закачаешься! Скажи мне любое слово, а в ответ получишь стих! Если надоем, то скажи "стоп" или "хватит". Приятного стихопрослушивания!',
                    'end_session': False
                }
            }

        # Log response
        logging.debug("---------- Response ----------")
        logging.debug(pretty_print(res))

        return json.dumps(res)
    
    except Exception as e:
        logging.exception("Unhandled exception in alice()")
        return json.dumps({
            'version': '1.0',
            'response': {
                'text': 'Произошла внутренняя ошибка при обработке запроса',
                'end_session': False
            }
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443)
