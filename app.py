from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/alice', methods=['POST'])
def alice():
    data = request.json
    if data['session']['new']:
        res = {
            'version': data['version'],
            'session': data['session'],
            'response': {
                'text': 'Привет! Создам тебе аккаунт, придумай для него пароль',
                'end_session': False
            }
        }
    else:
        res = {
            'version': data['version'],
            'session': data['session'],
            'response': {
                'text': 'Привет! Я тебя знаю, назови пароль',
                'end_session': False
            }
        }
    return json.dumps(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)