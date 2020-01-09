from flask import render_template, url_for, flash, redirect, Flask, request
from app import app
from app.forms import RegistrationForm, LoginForm, WeatherForm, SurgingSeasForm
from app.models import User, WeatherCard, SurgingSeasCard
from app.__init__ import bcrypt, db
from flask_login import login_user, logout_user, current_user
import requests
from app.my_functions import check_for_duplicates, check_for_the_same_parameters, is_int


@app.route('/weather', methods=['POST', 'GET'])
def weather():
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=88e12df4038659e5d9e36114cd2599d6'
    form = WeatherForm()

    if form.validate_on_submit():
        new_city = WeatherCard(city=form.city_name.data, user_id=current_user.id)
        if check_for_duplicates(new_city, WeatherCard) == True:
            flash(f'You already have a card for {form.city_name.data}.', 'danger')
        else:
            try:
                r = requests.get(url.format(new_city.city)).json()
                weather = r['weather'][0]['description']
                db.session.add(new_city)
                db.session.commit()
                db.session.close()
                flash(f'Card for "{form.city_name.data}" added successfully.', 'success')
            except KeyError:
                flash(f'There is not such a city "{form.city_name.data}". Try again with another one.', 'danger')
        return redirect(url_for('weather'))

    WeatherCards = WeatherCard.query.all()
    weather_data = []

    for card in WeatherCards:
        r = requests.get(url.format(card.city)).json()

        '''I am checking database once again, because sometimes records go in when they shouldn't.'''
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
            }
            weather_data.append(weather)
        except KeyError:
            local_object = db.session.merge(card)
            db.session.delete(local_object)
            db.session.commit()
            db.session.close()

    if current_user.is_authenticated:
        return render_template('weather.html', form=form, weather_data=weather_data)
    else:
        return render_template('not_signed_in.html')


@app.route('/delete_card/<int:card>')
def delete_card(card):
    card_to_delete = WeatherCard.query.filter_by(id=card).first()
    local_object = db.session.merge(card_to_delete)

    db.session.delete(local_object)
    db.session.commit()
    db.session.close()
    flash(f'Card for "{card_to_delete.city}" deleted successfully.', 'success')

    return redirect(url_for('weather'))


@app.route('/floods', methods=['POST', 'GET'])
def floods():
    form = SurgingSeasForm()

    if form.validate_on_submit():
        try:
            url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=88e12df4038659e5d9e36114cd2599d6'
            r = requests.get(url.format(form.city_name.data)).json()
            coordinates = [r['coord']['lon'], r['coord']['lat']]
            link_for_city = f'https://www.floodmap.net/?ll={coordinates[1]},{coordinates[0]}&z=11&e={form.how_many_metters.data}'
            new_city = SurgingSeasCard(city=form.city_name.data, link=link_for_city, lvl_increase=form.how_many_metters.data, user_id=current_user.id)
            if check_for_the_same_parameters(new_city, SurgingSeasCard) == True:
                flash('You already have a link with those parameters.', 'danger')
            elif is_int(form.how_many_metters.data) == False:
                flash('"Increase of seas level" must be an integer.', 'danger')
            else:
                db.session.add(new_city)
                db.session.commit()
                db.session.close()
                flash(f'Link for {form.city_name.data} added successfully.', 'success')
        except KeyError:
            flash(f'There is not such a city "{form.city_name.data}". Try again with another one.', 'danger')
        return redirect(url_for('floods'))

    if current_user.is_authenticated:
        data = SurgingSeasCard.query.filter(SurgingSeasCard.user_id == current_user.id)
        return render_template('floods.html', form=form, data=data)
    else:
        return render_template('not_signed_in.html')


@app.route('/delete_link/<int:link>')
def delete_link(link):
    link_to_delete = SurgingSeasCard.query.filter_by(id=link).first()
    local_object = db.session.merge(link_to_delete)

    db.session.delete(local_object)
    db.session.commit()
    db.session.close()
    flash(f'Link for "{link_to_delete.city}" deleted successfully.', 'success')

    return redirect(url_for('floods'))


@app.route('/')
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
        flash(f'Account has been created for {form.username.data}. You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', titile='Register', form=form)


@app.route('/delete_account/<int:user>')
def delete_account(user):
    links_to_delete = SurgingSeasCard.query.filter_by(user_id=user)
    for link in links_to_delete:
        local_object = db.session.merge(link)
        db.session.delete(local_object)
        db.session.commit()
        db.session.close()

    cards_to_delete = WeatherCard.query.filter_by(user_id=user)
    for card in cards_to_delete:
        local_object = db.session.merge(card)
        db.session.delete(local_object)
        db.session.commit()
        db.session.close()

    acc_to_delete = User.query.filter_by(id=user).first()
    local_object = db.session.merge(acc_to_delete)
    db.session.delete(local_object)
    db.session.commit()
    db.session.close()
    logout_user()   #for some reason next registered user is automaticly authenticated without this

    flash(f'Account for "{acc_to_delete.username}" deleted successfully.', 'success')

    return redirect(url_for('about'))