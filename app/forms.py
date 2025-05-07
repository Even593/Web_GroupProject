from flask_wtf import FlaskForm
from wtforms import FloatField, DateField, SubmitField
from wtforms.validators import DataRequired

class WeightForm(FlaskForm):

    record_date = DateField("Date", validators=[DataRequired()])
    weight_kg = FloatField("Weight (kg)", validators=[DataRequired()])
    submit = SubmitField("Add Record")