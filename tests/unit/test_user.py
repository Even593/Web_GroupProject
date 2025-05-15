import json
import unittest
import datetime

from app import create_app, db
from app.user import Account, Gender, __parse_date, route_to_login_if_required
from flask import g, session, url_for

class UserTestCase(unittest.TestCase):
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


    def test_register_and_login_logout(self):
        # 1) 注册
        payload = {"username": "bob", "password": "secret"}
        rv = self.client.post(
            url_for('api.user._bp_api_register'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(rv.data)
        self.assertTrue(data['succeed'])

        # 数据库中确实有该用户
        u = Account.query.filter_by(name="bob").first()
        self.assertIsNotNone(u)
        self.assertEqual(u.gender, Gender.MALE)

        # 2) 登陆
        rv = self.client.post(
            url_for('api.user._bp_api_login'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(rv.data)
        self.assertTrue(data['succeed'])

        # session 中存了 user_id，g.user 也被设置
        with self.client:
            self.client.post(
                url_for('api.user._bp_api_login'),
                data=json.dumps(payload),
                content_type='application/json'
            )
            self.assertIn('user_id', session)
            self.assertIsNotNone(g.user)
            self.assertEqual(g.user.name, "bob")

        # 3) 登出
        rv = self.client.post(url_for('api.user._bp_api_logout'))
        data = json.loads(rv.data)
        self.assertTrue(data['succeed'])
        with self.client:
            self.client.get('/')  # 触发 before_app_request
            self.assertIsNone(g.user)
            self.assertNotIn('user_id', session)



if __name__ == '__main__':
    unittest.main()