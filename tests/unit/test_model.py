import datetime
import unittest
from app import create_app, db
from app.account import Account, Gender

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.db.create_all()

    def tearDown(self):
        db.db.session.remove()
        db.db.drop_all()
        self.ctx.pop()

    def test_account_creation(self):
        # new acc
        u = Account(name='alice', password='pass123', gender=Gender.FEMALE, birthdate= datetime.date.today())
        db.db.session.add(u)
        db.db.session.commit()

        fetched = Account.query.filter_by(name='alice').first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.gender, Gender.FEMALE)

    def test_unique_username(self):
        u1 = Account(name='sam', password='p', gender=Gender.UNKNOWN, birthdate=datetime.date.today())
        db.db.session.add(u1)
        db.db.session.commit()

        # submit same acc name
        u2 = Account(name='sam', password='p2', gender=Gender.UNKNOWN, birthdate=datetime.date.today())
        db.db.session.add(u2)
        with self.assertRaises(Exception):
            db.db.session.commit()

if __name__ == '__main__':
    unittest.main()