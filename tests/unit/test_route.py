import unittest
from flask import url_for
from app import create_app, db

class RouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.db.session.remove()
        db.db.drop_all()
        self.ctx.pop()

    def test_protected_route_requires_login(self):
        #test 'login required' for /weight
        resp = self.client.get('/weight')
        # 未登录应被重定向到登录页
        self.assertEqual(resp.status_code, 308)


if __name__ == '__main__':
    unittest.main()