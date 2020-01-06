from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User, WeatherCard

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class WeatherForm(FlaskForm):
    city_name = StringField('', validators=[DataRequired()])
    submit = SubmitField('Add city')

class SurgingSeasForm(FlaskForm):
    city_name = StringField('<h6 style="color:#4976d0">Name of the city</h6>', validators=[DataRequired()])
    how_many_metters = StringField('<h6 class="text-danger">Increase of seas level [m]</h6>', validators=[DataRequired()])
    submit = SubmitField('Load link')