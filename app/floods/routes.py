from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.floods.forms import SurgingSeasForm
from app.models import SurgingSeasCard
from flask_login import current_user
import requests
from app.utilities import check_for_duplicates, check_for_the_same_parameters, is_int
from flask import Blueprint

floods_bp = Blueprint('floods_bp', __name__)


@floods_bp.route('/floods', methods=['POST', 'GET'])
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
        return redirect(url_for('floods_bp.floods'))

    if current_user.is_authenticated:
        data = SurgingSeasCard.query.filter(SurgingSeasCard.user_id == current_user.id)
        return render_template('floods.html', form=form, data=data)
    else:
        return render_template('not_signed_in.html')


@floods_bp.route('/delete_link/<int:link>')
def delete_link(link):
    link_to_delete = SurgingSeasCard.query.filter_by(id=link).first()
    local_object = db.session.merge(link_to_delete)

    db.session.delete(local_object)
    db.session.commit()
    db.session.close()
    flash(f'Link for "{link_to_delete.city}" deleted successfully.', 'success')

    return redirect(url_for('floods_bp.floods'))