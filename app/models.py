from app import db, manage_login
from flask_login import UserMixin

@manage_login.user_loader
def find_user(id):
    return User.query.get(id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    weather_card = db.relationship('WeatherCard', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.password}')"


class WeatherCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"City('{self.city}', '{self.id}')"


class SurgingSeasCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(100), nullable=False)
    lvl_increase = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"City('{self.city}', '{self.id}')"