from flask import render_template, url_for, flash, redirect, Flask, request
from app import app
from app.forms import RegistrationForm, LoginForm, WeatherForm, SurgingSeasForm
from app.models import User, WeatherCard
from app.__init__ import bcrypt, db
from flask_login import login_user, logout_user, current_user
import requests

def check_for_duplicates(new_city):
    WeatherCards = WeatherCard.query.all()
    for card in WeatherCards:
        if (card.city == new_city.city) and (current_user.id == card.user_id):
            return True
            break

@app.route('/weather', methods=['POST', 'GET'])
def weather():
    form = WeatherForm()

    if form.validate_on_submit():
        new_city = WeatherCard(city=form.city_name.data, user_id=current_user.id)
        if check_for_duplicates(new_city) == True:
            flash('You already have card with this city name.', 'danger')
        else:
            db.session.add(new_city)
            db.session.commit()
            db.session.close()
        return redirect(url_for('weather'))

    WeatherCards = WeatherCard.query.all()
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=88e12df4038659e5d9e36114cd2599d6'
    weather_data = []

    for card in WeatherCards:
        r = requests.get(url.format(card.city)).json()
        try:
            weather = {
                'city': card.city,
                'temperature': round((r['main']['temp']-32)*0.5556, 2),
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
                'pressure': r['main']['pressure'],
                'wind': r['wind']['speed'],
                'user': card.user_id,
                'id': card.id,
                'cord': [r['coord']['lon'], r['coord']['lat']],
            }
            weather_data.append(weather)
        except KeyError:
            local_object = db.session.merge(card)
            db.session.delete(local_object)
            db.session.commit()
            db.session.close()
            flash(f'There is not such a city "{card.city}". Try again with another one.', 'danger')

    return render_template('weather.html', form=form, weather_data=weather_data)

@app.route('/delete_card/<int:card>')
def delete_card(card):
    card_to_delete = WeatherCard.query.filter_by(id=card).first()
    local_object = db.session.merge(card_to_delete)

    db.session.delete(local_object)
    db.session.commit()
    db.session.close()
    flash(f'Card for "{card_to_delete.city}" deleted successfully.', 'success')

    return redirect(url_for('weather'))

@app.route('/')
@app.route('/floods', methods=['POST', 'GET'])                              ##################<----------------------------TUTAJ JESTEM
def floods():
    form = SurgingSeasForm()

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=88e12df4038659e5d9e36114cd2599d6'


    if form.validate_on_submit():
        try:
            r = requests.get(url.format(form.city_name)).json()
            coordinates = [r['coord']['lon'], r['coord']['lat']]
            city = {
                'city': form.city_name,
                'how_many_degrees': form.how_many_degrees.data,
                'coordinate_x': coordinates[0],
                'coordinate_y': coordinates[1],
            }
            return redirect(url_for('floods'))
        except KeyError:
            flash(f'There is not such a city. Try again with another one.', 'danger')
    else:
        city = None

    return render_template('floods.html', form=form, city=city)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('weather'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'You have been logged in successfully.', 'success')
            return redirect(url_for('weather'))
        else:
            flash(f'Login unsuccessfull. Please, check your username and password.', 'danger')
    return render_template('login.html', titile='Login', form=form)

@app.route('/logout')
def logout():
    user = User.query.filter_by(username=current_user.username).first()
    logout_user()
    flash(f'Logout for {user.username} succesfull.', 'success')
    return redirect(url_for('about'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('weather'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        db.session.close()
        flash(f'Account has been created for {user.username}. You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', titile='Register', form=form)