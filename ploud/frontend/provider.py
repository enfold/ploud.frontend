import ptah
import sqlalchemy as sqla
from models import User


@ptah.auth_provider('ploud')

class PloudProvider(object):

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']

        user = User.get(login)

        if user is not None:
            if ptah.passwordTool.check(user.password,password):
                return user

    @classmethod
    def get_principal(self, uri):
        return User.getByURI(uri)

    def get_principal_bylogin(self, login):
        return User.get(login)

    _sql_search = ptah.QueryFreezer(
        lambda: ptah.get_session().query(User) \
        .filter(User.email.contains(sqla.sql.bindparam('term')))
        .order_by(sqla.sql.asc('email')))

    @classmethod
    def search(cls, term):
        for user in cls._sql_search.all(term = '%%%s%%'%term):
            yield user


ptah.resolver.register('user-ploud', PloudProvider.get_principal)
ptah.principal_searcher.register('ploud', PloudProvider.search)
