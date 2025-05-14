from __future__ import annotations

from . import util

import json
import typing
import datetime

import flask
import flask_sqlalchemy

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

class __BaseModel(sa_orm.DeclarativeBase):
    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)

db = flask_sqlalchemy.SQLAlchemy(model_class=__BaseModel)

if typing.TYPE_CHECKING:
    class BaseModel(__BaseModel): ...
else:
    BaseModel = db.Model

class UidMixin:
    uid: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.ForeignKey("account.id", ondelete="CASCADE"))

class WeightRecord(db.Model):
    user_id = db.Column(db.Integer, nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    
class SharedWorkout(db.Model):
    __tablename__ = "shared_workout"
    from_user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey("workout_record.id"), nullable=False)
    shared_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

__ModelClass = typing.Type[BaseModel]

__TYPE_CONVERSION_IN = {
    sa.Integer: int,
    sa.Date: lambda d: datetime.datetime.strptime(d, "%Y-%m-%d").date(),
    sa.DateTime: lambda d: datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M"),
}

__TYPE_CONVERSION_OUT = {
    sa.Date: lambda d: d.strftime("%Y-%m-%d"),
    sa.DateTime: lambda d: d.strftime("%Y-%m-%dT%H:%M"),
}

def __make_response(succeed: bool, ids, objs):
    result = dict()
    result["succeed"] = succeed
    if ids:
        result["ids"] = ids
    if objs:
        result["result"] = objs
    return json.dumps(result)

def __transform_column_values(values, key, fn):
    for item in values:
        value = item.get(key, None)
        if value is not None:
            item[key] = fn(value)

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
