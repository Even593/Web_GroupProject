# Import base class for Flask-WTF form handling
from flask_wtf import FlaskForm

# Import form field types and validators
from wtforms import FloatField, DateField, SubmitField
from wtforms.validators import DataRequired

# Form class used for submitting weight records
class WeightForm(FlaskForm):

    record_date = DateField("Date", validators=[DataRequired()])
    weight_kg = FloatField("Weight (kg)", validators=[DataRequired()])
    submit = SubmitField("Add Record")