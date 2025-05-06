import typing

import flask_sqlalchemy
import sqlalchemy.orm as sa_orm

class __BaseModel(sa_orm.DeclarativeBase):
    _id: sa_orm.Mapped[int] = sa_orm.mapped_column("id", primary_key=True)

db = flask_sqlalchemy.SQLAlchemy(model_class=__BaseModel)

if typing.TYPE_CHECKING:
    class BaseModel(__BaseModel): ...
else:
    BaseModel = db.Model

