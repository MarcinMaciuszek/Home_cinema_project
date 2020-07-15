import os
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore, Security
from flask_mail import Mail
from app.config import Config
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer


template_dir = "{}".format(os.path.abspath('templates'))
static_dir = "{}".format(os.path.abspath('static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(Config)
database = SQLAlchemy(app)
mail = Mail(app)
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

roles_users = database.Table(
    'roles_users',
    database.Column('user_id', database.Integer(), database.ForeignKey('user.id')),
    database.Column('role_id', database.Integer(), database.ForeignKey('role.id'))
)

seances_and_users = database.Table(
    'seances_and_users',
    database.Column('user_id', database.Integer(), database.ForeignKey('user.id', onupdate="CASCADE")),
    database.Column('seance_id', database.Integer(), database.ForeignKey('seance.id', onupdate="CASCADE")),
)

from app.models import User, Role, Seance
from app import routes


user_datastore = SQLAlchemyUserDatastore(database, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def before_first_request():
    from app.admin_tabs import UserAdmin, RoleAdmin, SeanceAdmin, LoginMenuLink, LogoutMenuLink, HomeView
    from flask_admin.menu import MenuLink

    database.create_all()

    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='user', description='User')

    encrypted_password = generate_password_hash('admin')
    if not user_datastore.get_user('kinotest@gmail.com'): # should be replaced by correct email
        user_datastore.create_user(name='Admin', last_name='Admin',
                                   email='kinotest@gmail.com', password_hash=encrypted_password) # should be replaced by correct email
    try:
        database.session.commit()
    except Exception as error:
        return 'error: {}'.format(error)
    user_datastore.add_role_to_user('kinotest@gmail.com', 'admin') # should be replaced by correct email
    try:
        database.session.commit()
    except Exception as error:
        return 'error: {}'.format(error)

    admin = Admin(app, name='Admin', template_mode='bootstrap3', index_view=HomeView())
    admin.add_view(UserAdmin(User, database.session))
    admin.add_view(RoleAdmin(Role, database.session))
    admin.add_view(SeanceAdmin(Seance, database.session))
    admin.add_link(LoginMenuLink(name='Login', category='', url="/login"))
    admin.add_link(LogoutMenuLink(name='Logout', category='', url="/logout"))
    admin.add_link(MenuLink(name='Return', category='', url="/index"))