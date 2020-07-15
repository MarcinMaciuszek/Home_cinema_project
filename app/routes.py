import os
from app import app, database, mail, default_logger, ts
from app.core_functions import free_spaces_update, set_seance_date, set_seance_hour, prepare_info_about_seances, \
    check_that_new_user_is_correct_and_unique, register_unique_user, check_that_credentials_are_valid, place_reservation, \
    prepare_mail, mail_confirmation
from app.forms import LoginForm, RegistrationForm, PasswordChangeForm, PasswordResetForm, SeanceForm, ForgotForm
from app.models import User, Seance

from flask import render_template, redirect, url_for, flash, session
from flask_login import logout_user
from flask_security import current_user, login_required


logger = default_logger.logger_creation(name='routes')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    list_of_seances_active, list_of_seances_archive = prepare_info_about_seances()
    logger.debug("Active seances: {}".format([str(seance) for seance in list_of_seances_active]))
    return render_template('index.html', list_of_seances=list_of_seances_active, func=os.path.exists)


@app.route('/archive', methods=['GET', 'POST'])
def archive():
    list_of_seances_active, list_of_seances_archive = prepare_info_about_seances()
    logger.debug("Archive seances: {}".format([str(seance) for seance in list_of_seances_archive]))
    return render_template('archive.html', list_of_seances=list_of_seances_archive, func=os.path.exists)


@app.route('/about', methods=['GET', 'POST'])
def about():
    if not current_user.is_authenticated:
        flash('Aby dowiedzieć się więcej o nas, musisz się zalogować.')
        return redirect(url_for('index'))
    return render_template('about.html')


@app.route('/profile/<email>', methods=['GET', 'POST'])
@login_required
def profile(email):
    user = User.query.filter_by(email=email).first_or_404()
    seances = user.seances_and_users
    active_user_seances = []
    for seance in seances:
        if not seance.archive:
            active_user_seances.append(seance)
    return render_template('profile.html', user=user, seances=active_user_seances)


@app.route('/profile_archive_seances/<email>', methods=['GET', 'POST'])
@login_required
def profile_archive_seances(email):
    user = User.query.filter_by(email=email).first_or_404()
    seances = user.seances_and_users
    archive_user_seances = []
    for seance in seances:
        if seance.archive:
            archive_user_seances.append(seance)
    return render_template('profile_archive_seances.html', user=user, seances=archive_user_seances)


@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        return check_that_credentials_are_valid(form)
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('Zostałeś wylogowany.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        unique_user = check_that_new_user_is_correct_and_unique(form)
        if unique_user:
            if register_unique_user(form):
                flash('Utworzyłeś konto! Sprawdź maila w celu aktywacji konta.')
                return redirect(url_for('login'))
            else:
                flash("Coś poszło nie tak.")
    return render_template('register.html', form=form)


@app.route('/confirm/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    email = ts.loads(token, salt='email-confirm-key', max_age=86400)
    user = User.query.filter_by(email=email).first_or_404()
    logger.debug("User finded: {}".format(user))
    user.active = True
    try:
        database.session.commit()
    except Exception as error:
        return 'error: {}'.format(error)
    flash("Konto aktywowane")
    return redirect(url_for('login'))


@app.route('/password_change', methods=['GET', 'POST'])
@login_required
def password_change():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first_or_404()
        user.set_password(form.new_password.data)
        try:
            database.session.commit()
        except Exception as error:
            return 'error: {}'.format(error)
        flash('Hasło zmienione.')
        return redirect(url_for('index'))
    return render_template('password_change.html', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()
        if user:
            mail_confirmation(email=form.email.data, url='password_reset', salt='password-reset-key', option='password_reset')
            flash('Na maila został wysłany link do resetu hasła. Kliknij go a następnie zmień hasło.')
    return render_template('forgot_password.html', form=form)


@app.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit():
        email = ts.loads(token, salt='password-reset-key', max_age=86400)
        user = User.query.filter_by(email=email).first_or_404()
        user.set_password(form.new_password.data)
        try:
            database.session.commit()
        except Exception as error:
            return 'error: {}'.format(error)
        flash('Hasło zostało zmienione.')
        return redirect(url_for('index'))
    return render_template('password_reset.html', form=form)


@app.route('/reservation/<date>/<film>/<id>/<delete>/<profil>', methods=["POST", "GET"])
def reservation(date, film, id, delete, profil):
    if delete.lower() in ['false']:
        delete = False
    if profil.lower() in ['false']:
        profil = False
    if not current_user.is_authenticated:
        session['url'] = url_for('reservation', date=date, film=film, id=id, delete=False, profil=False)
        flash('Aby zarezerwować musisz się zalogować.')
        return redirect(url_for('login'))
    else:
        seance, delete_reservation_function = place_reservation(delete, profil, id)
        return render_template('reservation.html', seance=seance, delete_function=delete_reservation_function, user_name=str(current_user))


@app.route('/reservation_confirmation/<date>/<film>/<id>/<place>', methods=['GET', 'POST'])
def reservation_confirmation(date, film, id, place):
    seance = Seance.query.filter_by(id=id).first_or_404()
    current_user.seances_and_users.append(seance)
    place_no = 'place_{}'.format(place)
    setattr(seance, place_no, str(current_user))
    free_spaces_update(id)
    set_seance_date(seance)
    set_seance_hour(seance)
    try:
        database.session.commit()
    except Exception as error:
        return 'error: {}'.format(error)
    return render_template('reservation_confirmation.html', current_user=current_user, place=place, seance=seance)


@app.route('/seance', methods=['GET', 'POST'])
def seance():
    if not current_user.is_authenticated:
        flash('Aby zaproponować seans musisz się zalogować.')
        return redirect(url_for('index'))
    form = SeanceForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('seance.html', form=form)


@app.route('/mail_from_auto_reply', methods=['GET', 'POST'])
def mail_from_auto_reply():
    if current_user.is_authenticated:
        msg = prepare_mail('auto_reply')
        mail.send(msg)
        flash("Sprawdź swój mail: {}. Otrzymałeś maila od auto_replya.".format(current_user.email))
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))