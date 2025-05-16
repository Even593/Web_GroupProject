import json
import unittest
import datetime

from app import create_app, db
from app.account import Account, Gender
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
        #  register
        payload = {"username": "bob", "password": "secret", "email": "example@gmail.com"}
        rv = self.client.post(
            url_for('api.user._bp_api_register'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(rv.data)
        self.assertTrue(data['succeed'])

        # query table
        u = Account.query.filter_by(name="bob").first()
        self.assertIsNotNone(u)
        self.assertEqual(u.gender, Gender.UNKNOWN)

        # log in
        rv = self.client.post(
            url_for('api.user._bp_api_login'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = json.loads(rv.data)
        self.assertTrue(data['succeed'])

        with self.client:
            self.client.post(
                url_for('api.user._bp_api_login'),
                data=json.dumps(payload),
                content_type='application/json'
            )
            self.assertIn('user_id', session)
            self.assertIsNotNone(g.user)
            self.assertEqual(g.user.name, "bob")

        #  log out
        rv = self.client.post(url_for('api.user._bp_api_logout'))
        data = json.loads(rv.data)
        self.assertTrue(data['succeed'])
        with self.client:
            self.client.get('/')
            self.assertIsNone(g.user)
            self.assertNotIn('user_id', session)



if __name__ == '__main__':
    unittest.main()
