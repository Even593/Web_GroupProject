# Enables postponed evaluation of annotations (for type hints)
from __future__ import annotations

from . import util

import json
import typing
import datetime

import flask
import flask_sqlalchemy

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

# Base model class with auto-incrementing primary key 'id'
class __BaseModel(sa_orm.DeclarativeBase):
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)

# SQLAlchemy instance using our custom base model
db = flask_sqlalchemy.SQLAlchemy(model_class=__BaseModel)

# Alias for model base class to support type checking and runtime use
if typing.TYPE_CHECKING:
    class BaseModel(__BaseModel): ...
else:
    BaseModel = db.Model

# Mixin to associate records with a user account (foreign key to account.id)
class UidMixin:
    uid: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"))

# Table to store user weight records
class WeightRecord(db.Model):
    user_id = db.Column(db.Integer, nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)

# Table to track workout records shared between users    
class SharedWorkout(db.Model):
    __tablename__ = "shared_workout"
    from_user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey("workout_record.id"), nullable=False)
    shared_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Table to store mutual friendship relationships between users
class Friendship(db.Model):
    __tablename__ = "friendship"
    user_id = db.Column(db.Integer, db.ForeignKey("account.id"), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey("account.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # This table represents a mutual friendship (both users must add each other)

# Table to store private messages between friends
class PrivateMessage(db.Model):
    __tablename__ = "private_message"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    # This table stores private messages between friends

# Table to store comments on workout records
class WorkoutComment(db.Model):
    __tablename__ = "workout_comment"
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey("workout_record.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # This table stores comments on workout records

# Table to store likes on workout records
class WorkoutLike(db.Model):
    __tablename__ = "workout_like"
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey("workout_record.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # This table stores likes on workout records

__ModelClass = typing.Type[BaseModel]

# Incoming request data conversion (JSON -> Python)
__TYPE_CONVERSION_IN = {
    sa.Integer: int,
    sa.Date: lambda d: datetime.datetime.strptime(d, "%Y-%m-%d").date(),
    sa.DateTime: lambda d: datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M"),
}

# Outgoing data formatting (Python -> JSON)
__TYPE_CONVERSION_OUT = {
    sa.Date: lambda d: d.strftime("%Y-%m-%d"),
    sa.DateTime: lambda d: d.strftime("%Y-%m-%dT%H:%M"),
}

# Create JSON response with optional IDs or results
def __make_response(succeed: bool, ids, objs):
    result = dict()
    result["succeed"] = succeed
    if ids:
        result["ids"] = ids
    if objs:
        result["result"] = objs
    return json.dumps(result)

# Apply a transform function to a column across all dict rows
def __transform_column_values(values, key, fn):
    for item in values:
        value = item.get(key, None)
        if value is not None:
            item[key] = fn(value)

# Universal insert handler for JSON API endpoints
def handle_api_insert(model: __ModelClass, req: flask.Request) -> str:
    from . import account

    # parameters should be a json string
    params = req.get_json(silent=True)
    if params is None:
        return __make_response(False, None, None)

    # accepts single item insertion
    values = params
    if not isinstance(values, list):
        values = (values,)

    # fill the current user's ID
    user = util.get_current_user()
    if user and issubclass(model, UidMixin):
        for item in values:
            item[model.uid.key] = user.id

    # handle implicit type conversions
    for col in model.__table__.columns:
        fn = __TYPE_CONVERSION_IN.get(col.type.__class__)
        if fn:
            __transform_column_values(values, col.key, fn)

    stmt = sa.insert(model).values(values).returning(model.id)
    ids = db.session.scalars(stmt).all()
    db.session.commit()
    return __make_response(True, ids, None)

# Universal query handler for JSON API endpoints
def handle_api_query(model: __ModelClass, _: flask.Request) -> str:
    from . import account

    column_defs = model.__table__.columns
    column_keys = tuple(c.key for c in column_defs)
    column_fns = tuple(__TYPE_CONVERSION_OUT.get(c.type.__class__) for c in column_defs)

    # TODO(junyuzhang): handle criteria specifiers
    stmt = sa.select(*column_defs)
    user = util.get_current_user()
    if user and issubclass(model, UidMixin):
        stmt.where(model.uid == user.id)

    objs = []
    for item in db.session.execute(stmt).yield_per(100):
        obj = dict()
        for idx, key in enumerate(column_keys):
            fn = column_fns[idx]
            val = item[idx]
            obj[key] = fn(val) if fn else val
        objs.append(obj)

    return __make_response(True, None, objs)

# Universal delete handler for JSON API endpoints
def handle_api_delete(model: __ModelClass, req: flask.Request) -> str:
    params = req.get_json(silent=True)
    if params is None:
        return __make_response(False, None, None)

    ids = params.get("ids", None)
    if not ids:
        return __make_response(False, None, None)

    db.session.execute(sa.delete(model).where(model.id.in_(ids)))
    db.session.commit()
    return __make_response(True, None, None)

# Mock data insertion for development and testing purposes
# Call this function to populate the database with sample users, weight records, and workout records.
def insert_mock_data():
    from .account import Account
    from .workout import WorkoutRecord
    from .db import WeightRecord
    import datetime

    # Create sample users
    user1 = Account(name="alice", email="alice@example.com", password="hashedpassword1", gender=1, birthdate=datetime.date(1995, 5, 1))
    user2 = Account(name="bob", email="bob@example.com", password="hashedpassword2", gender=1, birthdate=datetime.date(1990, 8, 15))
    user3 = Account(name="carol", email="carol@example.com", password="hashedpassword3", gender=2, birthdate=datetime.date(1998, 12, 20))
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    # Add weight records for users
    weight_records = [
        WeightRecord(user_id=user1.id, record_date=datetime.date(2025, 5, 10), weight_kg=60.5),
        WeightRecord(user_id=user1.id, record_date=datetime.date(2025, 5, 15), weight_kg=60.0),
        WeightRecord(user_id=user2.id, record_date=datetime.date(2025, 5, 12), weight_kg=75.2),
        WeightRecord(user_id=user3.id, record_date=datetime.date(2025, 5, 14), weight_kg=55.8),
    ]
    db.session.add_all(weight_records)
    db.session.commit()

    # Add workout records for users
    workout_records = [
        WorkoutRecord(uid=user1.id, date=datetime.date(2025, 5, 10), notes="Morning run", duration=30, calories=250),
        WorkoutRecord(uid=user1.id, date=datetime.date(2025, 5, 12), notes="Yoga session", duration=45, calories=180),
        WorkoutRecord(uid=user2.id, date=datetime.date(2025, 5, 11), notes="Cycling", duration=60, calories=400),
        WorkoutRecord(uid=user3.id, date=datetime.date(2025, 5, 13), notes="Swimming", duration=50, calories=350),
    ]
    db.session.add_all(workout_records)
    db.session.commit()

    # Add a shared workout example
    from .db import SharedWorkout
    shared = SharedWorkout(from_user_id=user1.id, to_user_id=user2.id, record_id=workout_records[0].id)
    db.session.add(shared)
    db.session.commit()

    # Add friendship examples
    friendship1 = Friendship(user_id=user1.id, friend_id=user2.id)
    friendship2 = Friendship(user_id=user2.id, friend_id=user3.id)
    db.session.add_all([friendship1, friendship2])
    db.session.commit()

    print("Mock data inserted successfully.")
