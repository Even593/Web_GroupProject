import unittest
from app import create_app, db

class AppTestCase(unittest.TestCase):
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

    def test_app_exists(self):
        self.assertIsNotNone(self.app)

    def test_home_status_code(self):
        # our root / is redirect to url..
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)

if __name__ == '__main__':
    unittest.main()