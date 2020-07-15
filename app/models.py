import datetime
from app import database, roles_users, seances_and_users
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security import RoleMixin, UserMixin


MAXIMUM_PLACES = 7


class Role(database.Model, RoleMixin):
    id = database.Column(database.Integer(), primary_key=True)
    name = database.Column(database.String(80), unique=True)
    description = database.Column(database.String(255))

    def __str__(self):
        return self.name


class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(255))
    last_name = database.Column(database.String(255))
    email = database.Column(database.String(255), unique=True)
    password_hash = database.Column(database.String(255))
    active = database.Column(database.Boolean(), default=False)
    roles = database.relationship(
        'Role',
        secondary=roles_users,
    )
    seances_and_users = database.relationship(
        'Seance',
        secondary=seances_and_users,
        cascade="all,delete",
        backref=database.backref('users_on_seance', passive_deletes=True)
    )

    def __str__(self):
        return "{} {}".format(self.name, self.last_name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def push_user_to_database_and_set_role(self):
        from app import user_datastore
        user_datastore.create_user(name=self.name, last_name=self.last_name,
                                   email=self.email, password_hash=self.password_hash, active=False)
        user_datastore.add_role_to_user(self.email, 'user')


class Places(database.Model):
    places = database.Column(database.Integer, primary_key=True)
    place_1 = database.Column(database.String(200), default=None)
    place_2 = database.Column(database.String(200), default=None)


class Seance(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    date = database.Column(database.DateTime(200), default=datetime.datetime.now)
    film = database.Column(database.String(200))
    film_info = database.Column(database.String(400))
    film_img = database.Column(database.String(400))
    archive = database.Column(database.Boolean(), default=False)
    maximum_places = database.Column(database.Integer, default=MAXIMUM_PLACES)
    free_places = database.Column(database.Integer, default=MAXIMUM_PLACES)
    place_1 = database.Column(database.String(200), default=None)
    place_2 = database.Column(database.String(200), default=None)
    place_3 = database.Column(database.String(200), default=None)
    place_4 = database.Column(database.String(200), default=None)
    place_5 = database.Column(database.String(200), default=None)
    place_6 = database.Column(database.String(200), default=None)
    place_7 = database.Column(database.String(200), default=None)

    def __str__(self):
        return "ID: {}, Date and time: {}, Film: {}".format(self.id, self.date, self.film)

    def __getitem__(self):
        self.film


