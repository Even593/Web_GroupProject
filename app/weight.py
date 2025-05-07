import os
import typing
from lib2to3.pgen2.tokenize import endprogs

import flask
from fpdf import FPDF
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import current_user, login_required
from . import db
from . import user
from . import util
from .forms import WeightForm
from .db import WeightRecord
from .user import route_to_login_if_required

bp_view, bp_api = util.make_module_blueprints("weight")

@bp_view.get("/", endpoint="/")
def _index():
    form = WeightForm()
    weight_records = WeightRecord.query.filter_by(user_id=typing.cast(user.Account, flask.g.user)._id).all()
    return render_template("weight.html", form=form, records=weight_records, export_url=url_for("weight.export_pdf"))


@bp_view.post("/submit", endpoint="submit")
def _form():
    form = WeightForm()

    if form.validate_on_submit():
        new_record = WeightRecord(
            user_id=typing.cast(user.Account, flask.g.user)._id,
            record_date=form.record_date.data,
            weight_kg=form.weight_kg.data
        )
        db.db.session.add(new_record)
        db.db.session.commit()
    return redirect(url_for("weight./"))

def ___index():
    form = WeightForm()

    if form.validate_on_submit():
        new_record = WeightRecord(
            user_id=typing.cast(user.Account, flask.g.user)._id,
            record_date=form.record_date.data,
            weight_kg=form.weight_kg.data
        )
        db.db.session.add(new_record)
        db.db.session.commit()
        return redirect(url_for("weight.index"))

    #weight_records = WeightRecord.query.all()
    weight_records = WeightRecord.query.filter_by(user_id=typing.cast(user.Account, flask.g.user)._id).all()

    return render_template("weight.html", form=form, records=weight_records, export_url=url_for("weight.export_pdf"))

@bp_view.get("/export_pdf", endpoint="export_pdf")
def _export_pdf():
    weight_records = WeightRecord.query.all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Weight Records", ln=True, align="C")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 10, "Date", border=1)
    pdf.cell(50, 10, "Weight (kg)", border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 12)
    for record in weight_records:
        pdf.cell(50, 10, str(record.record_date), border=1)
        pdf.cell(50, 10, str(record.weight_kg), border=1)
        pdf.ln()

    output_dir = os.path.join(os.getcwd(), "share", "pdf files")
    os.makedirs(output_dir, exist_ok=True)  # create folder

    pdf_path = os.path.join(output_dir, "weight_records.pdf")

    pdf.output(pdf_path)
    #generate file
    print(f"PDF saved at: {pdf_path}")

    return send_file(pdf_path, as_attachment=True)