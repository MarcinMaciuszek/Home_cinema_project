import datetime

from flask import session, url_for, flash, render_template, redirect, session
from flask_login import current_user
from flask_mail import Message
from flask_login import login_user

from app import database, ts, mail, default_logger
from app.models import Seance, User


logger = default_logger.logger_creation(name='core_functions')


def free_spaces_update(seance_id):
    seance = Seance.query.filter_by(id=seance_id).first_or_404()
    taken_seats = 0
    logger.debug("New counting taken places, current value: {}.".format(taken_seats))
    for place_number in range(1, 8):
        if getattr(seance, 'place_{}'.format(place_number)):
            taken_seats += 1
            logger.debug("Place {} taken, sum of taken places: {}.".format(place_number, taken_seats))
    seance.free_places = seance.maximum_places - taken_seats
    logger.debug("Free places on seance: {}.".format(seance.free_places))
    try:
        database.session.commit()
    except Exception as error:
        return 'error: {}'.format(error)
    logger.debug("Free spaces on seance {} updated.".format(seance))


# tested
def set_seance_date(seance):
    seance.only_date = str(seance.date).split(' ')[0].split('-')
    seance.only_date.reverse()
    seance.only_date = ".".join(seance.only_date)
    logger.debug("Set new variable to seance: only_date to value: {}".format(seance.only_date))
    return seance.only_date

# tested
def set_seance_hour(seance):
    seance.only_hour = str(seance.date).split(' ')[1].split(':')[:2]
    seance.only_hour = ":".join(seance.only_hour)
    logger.debug("Set new variable to seance: only_hour to value: {}.".format(seance.only_hour))
    return seance.only_hour


def prepare_info_about_seances():
    session['url'] = url_for('index')
    list_of_seances_active = []
    list_of_seances_archive = []
    list_of_seances = Seance.query.order_by(Seance.date).all()
    logger.debug("List of seances: {}".format([str(seance) for seance in list_of_seances]))
    for seance in list_of_seances:
        set_seance_date(seance)
        set_seance_hour(seance)
        try:
            database.session.commit()
        except Exception as error:
            return 'error: {}'.format(error)
        logger.debug("New variables updated in database.")
        if datetime.date.today() > seance.date.date():
            seance.archive = True
            list_of_seances_archive.append(seance)
            logger.debug("Seance: {} added to archive.".format(seance))
        else:
            seance.archive = False
            list_of_seances_active.append(seance)
            logger.debug("Seance: {} added to active.".format(seance))
    try:
        database.session.commit()
    except Exception as error:
        return 'error: {}'.format(error)
    return list_of_seances_active, list_of_seances_archive


def check_that_new_user_is_correct_and_unique(form):
    registered_users = User.query.all()
    try:
        check_that_user_is_correct(form)
        logger.debug("Created user: {}, last_name: {}, email: {}.".format(form.name.data, form.last_name.data, form.email.data))
        for registered_user in registered_users:
            logger.debug("User name: {}, last_name: {}, email: {}.".format(registered_user.name, registered_user.last_name, registered_user.email))
            if form.email.data == registered_user.email:
                raise Exception(
                    "Użytkownik wykorzystujący email: {} już istnieje! Wybierz inny mail.".format(form.email.data))
            elif form.name.data == registered_user.name and form.last_name.data == registered_user.last_name:
                raise Exception(
                    "Użytkownik {} {} już istnieje! Wybierz inne dane.".format(form.name.data, form.last_name.data))
        else:
            logger.debug("User valid and correct.")
    except Exception as error:
        flash(str(error))
        return 0
    return 1


def check_that_user_is_correct(form):
    if ' ' in form.name.data.strip():
        raise Exception("Niedozowolna spacja w imieniu użytkownika: {}.".format(form.name.data))
    elif ' ' in form.last_name.data.strip():
        raise Exception("Niedozowolna spacja w nazwisku użytkownika: {}.".format(form.last_name.data))
    elif ' ' in form.email.data.strip():
        raise Exception("Niedozowolna spacja w emailu użytkownika: {}.".format(form.email.data))
    else:
        logger.debug("User correct.")
        return 1


def register_unique_user(form):
    user = User(name=form.name.data, last_name=form.last_name.data, email=form.email.data, active=0)
    logger.debug("User {} created.".format(user))
    user.set_password(form.password.data)
    logger.debug("Password set for user: {}.".format(user))
    user.push_user_to_database_and_set_role()
    # logger.debug("Added role: {} to user: {}".format(user.has_role().data, user))
    try:
        database.session.commit()
    except Exception as error:
        return 'error: {}'.format(error)
    mail_confirmation(email=form.email.data, url='confirm_email', salt='email-confirm-key',
                      option='confirm_register', name=form.name.data)
    return 1


def mail_confirmation(email, url, salt, option, name=None):
    token = ts.dumps(email, salt=salt)
    confirm_url = url_for(url, token=token, _external=True)
    msg = prepare_mail(option, confirm_url, email, name)
    mail.send(msg)
    return logger.debug("Mail send.")


def check_that_credentials_are_valid(form):
    user = User.query.filter_by(email=form.email.data).first_or_404()
    if user is None or not user.check_password(form.password.data):
        flash('Nieprawidłowy login lub hasło.')
        return redirect(url_for('login'))
    elif not user.active:
        flash("Konto nieaktywne. Aktywuj konto klikając w link w mailu potwierdzającym rejestrację.")
        return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    flash('Zalogowałeś się jako {} {}.'.format(user.name, user.last_name))
    if 'url' in session:
        return redirect(session['url'])
    else:
        return redirect(url_for('index'))



def place_reservation(delete, profil, id):
    seance = Seance.query.filter_by(id=id).first_or_404()
    index_in_tag_table, place_number, delete_reservation_function = find_place_taken_by_current_user(seance)
    print(delete_reservation_function)
    if delete_reservation_function:
        if delete:
            delete_reservation_function(seance, place_number, index_in_tag_table)
        free_spaces_update(id)
        if profil:
            from app.routes import profile
            return profile(email=current_user.email)
        else:
            return seance, delete_reservation_function
    else:
        free_spaces_update(id)
        delete_reservation_function = None
        return seance, delete_reservation_function


def find_place_taken_by_current_user(seance):
    index_in_tag_table = 0
    for user_seance in current_user.seances_and_users:
        if user_seance.id == seance.id:
            for place_number in range(1, 8):
                if str(current_user) == getattr(seance, 'place_{}'.format(place_number)):
                    delete_reservation_function = delete_reservation
                    logger.debug("User {} find on place {}.".format(current_user, place_number))
                    return index_in_tag_table, place_number, delete_reservation_function
        index_in_tag_table += 1
    return 0, 0, 0


def delete_reservation(seance, place_number, index_in_tag_table):
    setattr(seance, 'place_{}'.format(place_number), None)
    current_user.seances_and_users.pop(index_in_tag_table)
    try:
        database.session.commit()
    except Exception as error:
        return 'error: {}'.format(error)
    logger.debug("Delete reservation for user: {} on seance: {} and place: {}".format(current_user, seance, place_number))


def prepare_mail(option, url=None, email=None, name=None):
    if option == 'auto_reply':
        body = "Siemano {},\n\n" \
               "Witaj w Kine! Badź na bieżąco, śledź najnowsze wydarzenia.\n\n" \
               "Pozdrawiamy".format(current_user.name)
        msg = Message(subject='elo', recipients=[current_user.email], body=body)
        return msg
    elif option == 'confirm_register':
        body = "Witamy Cię {} w Kinie!\n" \
               "Aby dokończyć rejestrację kliknij w poniższy link:\n" \
               "{}\n\n" \
               "Dyrektor Artystyczny auto_reply".format(name, url)
        msg = Message(subject='Potwierdzenie rejestracji w Kinie', recipients=[email], body=body)
        return msg
    elif option == 'password_reset':
        body = "Elo,\n" \
               "Aby zresetować hasło kliknij w poniższy link:\n" \
               "{}\n\n" \
               "Konserwator".format(url)
        msg = Message(subject='Reset hasła', recipients=[email], body=body)
        return msg
    else:
        return logger.debug("No valid option.")