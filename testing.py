import unittest
import api

import time
from urllib.parse import urlparse
import redis


class TestFlask(unittest.TestCase):

    def setUp(self):
        api.app.testing = True
        self.app = api.app.test_client()

    def test_get_request(self):
        response = self.app.get('/visited_domains?from=1581253751&to=1581253756')
        self.assertEqual(response.status_code, 200)

        domains = response.json.get('domains')
        self.assertIsInstance(domains, list)

        status = response.json.get('status')
        self.assertEqual(status, 'ok')

    def test_post_request(self):

        json = {
            "links": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
            ]
        }

        response = self.app.post('/visited_links', content_type='application/json', json=json)
        self.assertEqual(response.status_code, 200)

        status = response.json.get('status')
        self.assertEqual(status, 'ok')

        """
        The following code is used to clear the database ather the test input
        It removes ALL the keys from the database, so you have to use it carefully or just comment
        """
        r = api.Redis()
        db = r.db
        db.flushall()
        self.assertEqual(len(db.keys()), 0)
        self.assertIsInstance(db.keys(), list)


class TestReddis(unittest.TestCase):

    def setUp(self):
        self.links = {'ya.ru', 'google.com', 'stackoverflow.com'}
        self.r = api.Redis()
        self.db = self.r.db
        self.assertIsInstance(self.db, redis.client.Redis)

    def test_links_prettify(self):
        raw_links = {
            'https://ya.ru',
            'ya.ru?q=123"',
            'google.com/123',
            'stackoverflow.com?q=123'
        }
        netloc = lambda x: urlparse(x).netloc
        scheme = lambda x: urlparse(x).scheme
        links = set(netloc(u) if scheme(u) else netloc('https://' + u) for u in raw_links)
        self.assertEqual(links, self.links)

    def test_redis_insert(self):
        timestamp = round(time.time())
        num_of_items_inserted = self.r.insert(timestamp, self.links)
        self.assertIsInstance(num_of_items_inserted, int)

    def test_redis_select(self):
        start = round(time.time()) - 100
        end = round(time.time()) + 100
        link_list = self.r.select_delta(start, end)
        self.assertIsInstance(link_list, list)


if __name__ == '__main__':
    unittest.main()
