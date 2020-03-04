from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
manage_login = LoginManager(app)

from app.floods.routes import floods_bp
from app.main.routes import about_bp
from app.users.routes import users_bp
from app.weather.routes import weather_bp

app.register_blueprint(floods_bp)
app.register_blueprint(about_bp)
app.register_blueprint(users_bp)
app.register_blueprint(weather_bp)