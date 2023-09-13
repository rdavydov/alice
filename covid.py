# -"- coding:utf-8 -"-

import requests
import json
import os

from flask import Flask, request
import logging
import sqlite3



def search(cords, rad=1):
    global cur
    count = 0  # количество где расстояние меньше километра
    count_new = 0
    dis = []  # список из дистанций
    
    cords[0] = int(cords[0].replace('.', '').ljust(10, '0'))
    cords[1] = int(cords[1].replace('.', '').ljust(10, '0'))
    result = cur.execute(
        "SELECT width, height, adress, new FROM adresses WHERE (width >= " + str(cords[0] - 9000000 * rad) + ") AND (width <= " + str(cords[0] + 9000000 * rad) +
        ") AND (height >= " + str(cords[1] - 1562500 * rad) + ") AND (height <= " + str(cords[1] + 1562500 * rad) + ")").fetchall()
    for i in result:  # считаем расстояния через разницу координат
        distance = ((
            (i[1] - cords[1]) / 900) ** 2 + (
            (i[0] - cords[0]) / 1562.5) ** 2) ** 0.5
        # print(distance)
        if distance <= 1000:
            count += 1
            if i[3] == 1:
                count_new += 1
        dis.append(distance)
    if count > 0:
        text = "В радиусе 1 километра от этого дома " + \
            str(count)  # сколько домов всего
        # склонение слова для красоты
        if str(count)[-1] == '1' and str(count)[-2] != '1':
            text += ' зараженный'
        else:
            text += ' зараженных'
        if count_new == 0:
            text += ', новых зараженных нет'
        else:
            text += ', из них новых зараженных '
            text += str(count_new)
        # если расстояние до дома меньше 10 метров, то считает что заболевший в данном доме
        if int(round(min(dis), 0)) > 10:
            text += ', при этом ближайший дом находится по адресу: '
            # адрес дома
            text += result[dis.index(min(dis))][2].replace('Москва, ', '')
            text += ' на расстоянии в '
            text += str(int(round(min(dis), 0)))  # расстояние до него
            # тоже для красоты
            if str(int(round(min(dis), 0)))[-1] == '1' and str(int(round(min(dis), 0)))[-2] != '1':
                text += ' метр от этого дома.'
            elif str(int(round(min(dis), 0)))[-1] == '2' and str(int(round(min(dis), 0)))[-2] != '1':
                text += ' метра от этого дома.'
            elif str(int(round(min(dis), 0)))[-1] == '3' and str(int(round(min(dis), 0)))[-2] != '1':
                text += ' метра от этого дома.'
            elif str(int(round(min(dis), 0)))[-1] == '4' and str(int(round(min(dis), 0)))[-2] != '1':
                text += ' метра от этого дома.'
            else:
                text += ' метров от этого дома.'
        else:
            # случай, когда заболевший в данном доме
            text += ' и ближайший зараженный находится в этом доме!'
    else:
        # случай, когда заболевших не найдено
        text = 'В радиусе километра зараженных не обнаружено, поздравляю!'
        # спрашивает хочет ли еще узнать
    text += ' Назови новый адрес или скажи "Завершить диалог"'
    return text

app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)


sessionStorage = {}

parts = {}  # 0 - узнаем адрес, 1 - говорим количество
#                  и ближайший адрес, 2 - спрашиваем хочет ли узнать еще

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
            'text'] = 'Привет! Узнай сколько заболевших коронавирусом есть около тебя! ' + \
            'Назови адрес, про который хочешь узнать, правда я могу сказать только про Москву и окрестности'
        return

    try: # на всякий случай)
        if list(map(lambda x: x.lower(), req['request']['nlu']['tokens'])) == ['закончить', 'диалог'] or \
           list(map(lambda x: x.lower(), req['request']['nlu']['tokens'])) == ['завершить', 'диалог']:
            res['response']['text'] = 'Пока! Возвращайся за новой информацией завтра и старайся поменьше выходить из дома!'
            res['response']['tts'] = 'Пока! Возвращайся за новой информацией завтра и старайся поменьше выход+ить из дома!'
            res['response']['end_session'] = True
            return
    except Exception:
        pass
    try:
        # что ты умеешь? - обязательный вопрос в навыке Алисы
        if list(map(lambda x: x.lower(), req['request']['nlu']['tokens'])) == ['что', 'ты', 'умеешь'] or \
           list(map(lambda x: x.lower(), req['request']['nlu']['tokens'])) == ['помощь']:
            res['response']['text'] = 'Я умею определять сколько зараженных коронавирусом людей находятся в ' + \
                'радиусе 1 километра от тебя, для этого мне достаточно сказать адрес любого дома. Скажи мне адрес'
            return
    except Exception:
        pass
    try:
        for i, dat in enumerate(req['request']['nlu']['entities']):
            if dat['type'] == "YANDEX.GEO":
                if 'city' not in list(req['request']['nlu']['entities'][i]['value'].keys()):
                    # ищем спрашиваемый дом через API Яндекс.Карт
                    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=Москва,+" + \
                        req['request']['nlu']['entities'][i]['value']['street'] + \
                        ",+" + \
                        req['request']['nlu']['entities'][i]['value']['house_number'] + \
                        "&format=json"
                else:
                    # случай, если будут спрашивать соседние города (Химки, Мытищи и тд)
                    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=Москва,+" + \
                        req['request']['nlu']['entities'][i]['value']['city'] + ',+' + \
                        req['request']['nlu']['entities'][i]['value']['street'] + \
                        ",+" + \
                        req['request']['nlu']['entities'][i]['value']['house_number'] + \
                        "&format=json"
                response = requests.get(geocoder_request)
                if response:  # если адрес нашелся
                    json_response = response.json()
                    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                    toponym_coordinates = toponym["Point"]["pos"]
                    res['response']['text'] = search(
                        toponym_coordinates.split())
                else:  # если не нашелся
                    res['response']['text'] = 'Мне очень жаль, но такого адреса нет, скажите еще раз'
                return
        # пользователь сказал не адрес
        res['response']['text'] = 'Кажется, это не адрес. Назовите адрес еще раз'
    except Exception as e:
        res['response']['text'] = "Не совсем тебя поняла. Назови адрес еще раз"

if __name__ == '__main__':
    con = sqlite3.connect('data_covid.db', check_same_thread=False)  # база данных
    cur = con.cursor()
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run(host='0.0.0.0', port=80)