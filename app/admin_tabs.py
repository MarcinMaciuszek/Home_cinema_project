import re
from app.core_functions import free_spaces_update
from app import default_logger
from app import database
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_security import current_user
from wtforms import validators


class HomeView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')


class UserAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')
    # do not display password in User tab and User form
    column_exclude_list = ('password_hash',)
    form_excluded_columns = ('password_hash',)

    # display relation variables
    column_display_all_relations = True
    # order of display in User tab
    column_list = ['name', 'last_name', 'email', 'roles']


class RoleAdmin(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')


class SeanceAdmin(ModelView):
    def __init__(self, Seance, database):
        super(SeanceAdmin, self).__init__(Seance, database)
        self.users_on_places = []
        self.errors = []
        self.logger = default_logger.logger_creation(name='admin')

    def is_accessible(self):
        return current_user.has_role('admin')

    def after_model_change(self, form, Seance, is_created):
        free_spaces_update(Seance.id)

    def on_model_change(self, form, Seance, is_created):
        try:
            database.session.commit()
        except Exception as error:
            return 'error: {}'.format(error)

        # validation before submit form
        try:
            self.check_users_names_on_places(Seance)
            self.check_that_tags_are_compatible_with_users_names_on_places(form)
            self.check_that_users_names_on_places_are_compatible_with_tags(form)
            self.form_check(form)
            self.image_setter(form, Seance)

        except Exception as e:
            self.errors.append(str(e))
            errors_printout = ", ".join(self.errors)
            self.errors = []
            try:
                database.session.delete(Seance)
                database.session.commit()
            except Exception as error:
                return 'error: {}'.format(error)
            raise validators.ValidationError(message=errors_printout)

        try:
            database.session.commit()
        except Exception as error:
            return 'error: {}'.format(error)

    def check_users_names_on_places(self, Seance):
        self.users_on_places = []
        seance = Seance.query.filter_by(id=Seance.id).first_or_404()
        for counter in range(1, 8):
            if getattr(seance, 'place_{}'.format(counter)):
                user_name = getattr(seance, 'place_{}'.format(counter))  # .split()[0]
                self.users_on_places.append((user_name, 'place_{}'.format(counter)))
        self.logger.debug("self.users_on_places: {}".format(self.users_on_places))

    def check_that_tags_are_compatible_with_users_names_on_places(self, form):
        for user in form.users_on_seance.data:
            self.logger.debug("user: {} {} {}".format(user.name, user.last_name, user.email))
            if not len(self.users_on_places):
                self.logger.debug("pusta lista self.user_on_places")
                self.errors.append("W polu Users On Seance znajduje się {} który nie zajął żadnego miesjaca!".format(str(user)))
            else:
                for place in self.users_on_places:
                    if str(user) in place:
                        self.logger.debug("user zanleziony w {}".format(place))
                        break
                    else:
                        self.logger.debug("{} not in {}".format(str(user), place))
                else:
                    self.errors.append("W polu Users On Seance znajduje się {} który nie zajął żadnego miesjaca!".format(str(user)))

    def check_that_users_names_on_places_are_compatible_with_tags(self, form):
        for place in self.users_on_places:
            self.logger.debug("user on place: {}".format(place))
            if not len(form.users_on_seance.data):
                self.logger.debug("pusta lista form.users_on_seance")
                self.errors.append("Użytownik {} na miejscu {} nie jest w tagach.".format(place[0], place[1]))
            else:
                for user in form.users_on_seance.data:
                    if(str(user)) in place:
                        self.logger.debug("user zanleziony w {}".format(place))
                        break
                    else:
                        self.logger.debug("{} not in {}".format(str(user), place))
                else:
                    self.errors.append(
                        "W polu Users On Seance znajduje się {} który nie jest w tagacha!".format(place[0]))

    def form_check(self, form):
        filmweb_pattern = re.compile(r'.*www.filmweb.pl.*')
        if not form.date.data:
            self.errors.append("brak daty")
        if not form.film.data:
            self.errors.append("nie ma filmu")
        if not form.film_info.data:
            self.errors.append("brak linku")
        elif not filmweb_pattern.search(form.film_info.data):
            self.errors.append("błędny link")
        if self.errors:
            raise Exception

    def image_setter(self, form, Seance):
            film_img_link = "{}/photos".format(form.film_info.data)

            request_to_filmweb = Request(film_img_link, headers={'User-Agent': 'Magic Browser'})
            respose_from_filmweb = urlopen(request_to_filmweb)
            soup = BeautifulSoup(respose_from_filmweb, 'html.parser')

            try:
                film_img = soup.find('a', class_='slideshowStart gallery__photo-item__wrapper')
                self.logger.debug("Link to film img: {}.".format(film_img['data-photo']))
                Seance.film_img = film_img['data-photo']
            except Exception as e:
                self.errors.append(e)
                print("No photo")

            if not Seance.film_img:

                poster_img_link = "{}/posters".format(form.film_info.data)

                request_to_filmweb = Request(poster_img_link, headers={'User-Agent': 'Magic Browser'})
                respose_from_filmweb = urlopen(request_to_filmweb)
                soup = BeautifulSoup(respose_from_filmweb, 'html.parser')

                try:
                    poster_img = soup.find('img', class_='simplePoster__image')
                    self.logger.debug("Link to poster img: {}.".format(poster_img['data-src']))
                    Seance.film_img = poster_img['data-src']
                except Exception as e:
                    self.errors.append(e)
                    print("No photo")

    form_excluded_columns = ('free_places', 'film_img')
    form_columns = ('date', 'film', 'film_info', 'maximum_places', 'place_1', 'place_2', 'place_3',
                    'place_4', 'place_5', 'place_6', 'place_7', 'users_on_seance')
    column_list = ['id', 'date', 'film', 'film_info', 'free_places', 'maximum_places']


class LoginMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated

