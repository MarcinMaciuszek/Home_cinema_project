import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, URL, Regexp


class RegistrationForm(FlaskForm):
    name = StringField('Imię', validators=[DataRequired()])
    last_name = StringField('Nazwisko', validators=[DataRequired()])
    email = StringField('Adres email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    password_confirmation = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zarejestruj')


class LoginForm(FlaskForm):
    email = StringField('Adres email', validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember_me = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')


class PasswordChangeForm(FlaskForm):
    previous_password = PasswordField('Stare hasło', validators=[DataRequired()])
    new_password = PasswordField('Nowe hasło', validators=[DataRequired()])
    new_password_confirmation = PasswordField('Powtórz nowe hasło', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Zmień hasło')


class ForgotForm(FlaskForm):
    email = StringField('Adres email', validators=[DataRequired(), Email()])
    submit = SubmitField('Zresetuj hasło')


class PasswordResetForm(FlaskForm):
    new_password = PasswordField('Nowe hasło', validators=[DataRequired()])
    new_password_confirmation = PasswordField('Powtórz nowe hasło', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Zatwierdź nowe hasło')


class SeanceForm(FlaskForm):
    filmweb_pattern = re.compile(r'.*www.filmweb.pl.*')
    link = StringField('Link do filmu na filmwebie', validators=[DataRequired(), URL(), Regexp(filmweb_pattern)])
    description = TextAreaField('Uzasadnienie', render_kw={'cols': '80', 'rows': '4'})
    submit = SubmitField('Wyślij propozycję')
