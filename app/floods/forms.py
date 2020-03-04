from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SurgingSeasForm(FlaskForm):
    city_name = StringField('<h6 style="color:#4976d0">Name of the city</h6>', validators=[DataRequired()])
    how_many_metters = StringField('<h6 class="text-danger">Increase of seas level [m]</h6>', validators=[DataRequired()])
    submit = SubmitField('Load link')