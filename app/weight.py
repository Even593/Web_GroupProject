from . import db
from . import util

import datetime

import fpdf
import flask
import flask_wtf
import wtforms.validators

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

bp_view = flask.Blueprint("weight", __name__, url_prefix="/weight")

class WeightForm(flask_wtf.FlaskForm):
    date = wtforms.DateField("Date", validators=[wtforms.validators.DataRequired()])
    weight = wtforms.FloatField("Weight (kg)", validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField("Add Record")

class WeightRecord(db.UidMixin, db.BaseModel):
    date: sa_orm.Mapped[datetime.date] = sa_orm.mapped_column(sa.Date)
    weight: sa_orm.Mapped[float] = sa_orm.mapped_column(sa.Float)

@bp_view.get("/", endpoint="")
@util.route_check_login
def _view_index():
    form = WeightForm()
    stmt = sa.select(WeightRecord).where(WeightRecord.uid == util.get_current_user().id)
    records = db.db.session.scalars(stmt)
    return flask.render_template("weight.html", form=form, records=records)

@bp_view.post("/submit", endpoint="submit")
@util.route_check_login
def _form():
    form = WeightForm()

    if form.validate_on_submit():
        new_record = WeightRecord(
            uid=util.get_current_user().id,
            date=form.date.data,
            weight=form.weight.data
        )
        db.db.session.add(new_record)
        db.db.session.commit()
    return flask.redirect(flask.url_for("weight."))

@bp_view.get("/export", endpoint="export")
@util.route_check_login
def _view_export_pdf():

    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Weight Records", ln=True, align="C")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 10, "Date", border=1)
    pdf.cell(50, 10, "Weight (kg)", border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 12)

    stmt = sa.select(WeightRecord.date, WeightRecord.weight)\
        .where(WeightRecord.uid == util.get_current_user().id)
    for date, weight in db.db.session.execute(stmt).yield_per(100):
        pdf.cell(50, 10, str(date), border=1)
        pdf.cell(50, 10, str(weight), border=1)
        pdf.ln()

    # this is how fpdf write to the export file in python 3
    content = pdf.output(dest="S").encode("latin1")
    headers = {"Content-Disposition": "attachment; filename=records.pdf"}
    return flask.Response(content, mimetype="application/pdf", headers=headers)
