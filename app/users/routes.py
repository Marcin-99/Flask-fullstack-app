from flask import render_template, url_for, flash, redirect, Flask, request
from app import db, bcrypt
from app.users.forms import RegistrationForm, LoginForm
from app.models import User, WeatherCard, SurgingSeasCard
from flask_login import login_user, logout_user, current_user
import requests
from flask import Blueprint

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('weather_bp.weather'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'You have been logged in successfully.', 'success')
            return redirect(url_for('weather_bp.weather'))
        else:
            flash(f'Login unsuccessfull. Please, check your username and password.', 'danger')
    return render_template('login.html', titile='Login', form=form)


@users_bp.route('/logout')
def logout():
    user = User.query.filter_by(username=current_user.username).first()
    logout_user()
    flash(f'Logout for {user.username} succesfull.', 'success')
    return redirect(url_for('about_bp.about'))


@users_bp.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('weather_bp.weather'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        db.session.close()
        flash(f'Account has been created for {form.username.data}. You are now able to log in.', 'success')
        return redirect(url_for('users_bp.login'))
    return render_template('register.html', titile='Register', form=form)


@users_bp.route('/delete_account/<int:user>')
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
    logout_user()   #for some reason next registered user is automaticly authenticated without logout

    flash(f'Account for "{acc_to_delete.username}" deleted successfully.', 'success')

    return redirect(url_for('about_bp.about'))