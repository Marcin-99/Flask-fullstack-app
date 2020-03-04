from flask import render_template, url_for, flash, redirect, Flask, request
from app import app, bcrypt, db
from app.weather.forms import WeatherForm
from app.models import WeatherCard
from flask_login import current_user
import requests
from app.utilities import check_for_duplicates
from flask import Blueprint

weather_bp = Blueprint('weather_bp', __name__)


@weather_bp.route('/weather', methods=['POST', 'GET'])
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
        return redirect(url_for('weather_bp.weather'))

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


@weather_bp.route('/delete_card/<int:card>')
def delete_card(card):
    card_to_delete = WeatherCard.query.filter_by(id=card).first()
    local_object = db.session.merge(card_to_delete)

    db.session.delete(local_object)
    db.session.commit()
    db.session.close()
    flash(f'Card for "{card_to_delete.city}" deleted successfully.', 'success')

    return redirect(url_for('weather_bp.weather'))