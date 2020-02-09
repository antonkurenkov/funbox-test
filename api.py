"""
Реализуйте web-приложение для простого учета посещенных (неважно, как, кем и когда)
ссылок. Приложение должно удовлетворять следующим требованиям.
• Приложение написано на языке Python версии ~> 3.7.
• Приложение предоставляет JSON API по HTTP.
• Приложение предоставляет два HTTP ресурса.
--------------------------
Ресурс загрузки посещений:

Запрос 1
POST /visited_links
{
    "links": [
        "https://ya.ru",
        "https://ya.ru?q=123",
        "funbox.ru",
        "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
    ]
}

{
"status": "ok"
}
---------------------------
Ресурс получения статистики:
Запрос 2
GET /visited_domains?from=1545221231&to=1545217638

{
    "domains": [
        "ya.ru",
        "funbox.ru",
        "stackoverflow.com"
    ],
    "status": "ok"
}

Первый ресурс служит для передачи в сервис массива ссылок в POST-запросе.
Временем их посещения считается время получения запроса сервисом.
• Второй ресурс служит для получения GET-запросом списка уникальных доменов,
посещенных за переданный интервал времени.
• Поле status ответа служит для передачи любых возникающих при обработке запроса
ошибок.
• Для хранения данных сервис должен использовать БД Redis.
• Код должен быть покрыт тестами.
• Инструкции по запуску должны находиться в файле README.

"""

import time
from urllib.parse import urlparse
import redis
from flask import Flask, jsonify
from flask import request

app = Flask(__name__)
# start_time = round(time.time())
start_time = 1545221231  # is used for testing
max_uts = 2147483647


class Redis(object):

    def __init__(self):
        self.db = redis.StrictRedis(host='localhost', port=6379, db=0)

    def insert(self, timestamp, links):
        return self.db.sadd(timestamp, *links)

    def select_delta(self, _from_, _to_):
        full_set = set()
        for moment in range(_from_, _to_ + 1):
            if self.db.smembers(str(moment)):
                part = self.db.smembers(str(moment))
                full_set.update(part)
        return [b.decode('utf-8') for b in full_set]


@app.route('/visited_domains', methods=['GET'])
def visited_domains():
    try:
        start = int(request.args.get('from'))
        assert start in range(start_time, max_uts), 'Incorrect "from" timestamp'

        end = int(request.args.get('to'))
        assert end in range(start_time, max_uts), 'Incorrect "to" timestamp'

        link_list = Redis().select_delta(start, end)
        return jsonify({'domains': link_list, 'status': 'ok'})
    except Exception as e:
        return jsonify({'status': {'error': e.__class__.__name__, 'etc': e.args}})


@app.route('/visited_links', methods=['POST'])
def visited_links():
    timestamp = round(time.time())
    netloc = lambda x: urlparse(x).netloc
    scheme = lambda x: urlparse(x).scheme

    try:
        raw_links = request.json.get('links')
        links = set(netloc(u) if scheme(u) else netloc('https://' + u) for u in raw_links)
        Redis().insert(timestamp, links)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': {'error': e.__class__.__name__, 'etc': e.args}})



if __name__ == '__main__':
    app.run(debug=True)
