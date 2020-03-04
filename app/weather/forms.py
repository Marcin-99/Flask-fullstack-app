from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class WeatherForm(FlaskForm):
    city_name = StringField('', validators=[DataRequired()])
    submit = SubmitField('Add city')