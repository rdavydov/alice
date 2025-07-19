# Универсальный стихоплёт - навык для Алисы (ассистента Яндекса)

Цензурная версия.

https://dialogs.yandex.ru/store/skills/ed360f3e-universal-nyj-stihoplyo?action=donation

![](https://github.com/rdavydov/alice/blob/main/stihoplet.png?raw=true)

# ![](https://github.com/rdavydov/alice/blob/main/logo.png?raw=true)

```
pip install gunicorn
TZ='Europe/Moscow' gunicorn -w 4 -b 0.0.0.0:8443 alice_stihoplet:app --log-config uvicorn_logging.conf
```
