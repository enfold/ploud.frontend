""" ploud.login """
import httplib
import transaction
from datetime import timedelta
from pyramid.view import view_config
from pyramid.i18n import TranslationStringFactory
from pyramid.traversal import DefaultRootFactory
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import token, form

_ = TranslationStringFactory('ploud.login')


from ploud.frontend.root import PloudApplicationRoot
from ploud.frontend.config import LOGIN_TOKEN_TYPE as TOKEN_TYPE


ptah.layout.register(
    'ploud-login', PloudApplicationRoot,
    renderer='ploud.frontend:newui/ssolayout.pt')


LoginSchema = form.Fieldset(
    form.TextField(
        'login',
        title = _(u'Login Name'),
        description = _('Login names are case sensitive, '\
                            'make sure the caps lock key is not enabled.'),
        default = u''),

    form.PasswordField(
        'password',
        title = _(u'Password'),
        description = _('Case sensitive, make sure caps lock is not enabled.'),
        default = u'')
)


@view_config(route_name='login', wrapper=ptah.wrap_layout('ploud-login'))
class LoginForm(form.Form):

    fields = LoginSchema

    @form.button('Login', actype=form.AC_PRIMARY)
    def loginHandler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        host = self.request.matchdict['site']
        data = '%s::%s'%(data['login'], data['password'])
        tid = token.service.generate(TOKEN_TYPE, data)
        transaction.commit()

        try:
            SSO = ptah.get_settings('ploud-login', self.request.registry)
            conn = httplib.HTTPConnection(SSO['backend'], timeout=2)
            conn.connect()
            conn.putrequest(
                'GET', '/__maintenance__/check-credentials,%s/Plone'%tid,
                skip_host=True, skip_accept_encoding=True)

            conn.putheader('Host', host)
            conn.endheaders()
            resp = conn.getresponse()
            data = resp.read().strip()
        except:
            self.message(
                "Can't connect to target host. Please try again later.",'warning')
            token.service.remove(tid)
            return

        if data == 'success':
            return HTTPFound(location='http://%s/authToken?token=%s'%(host, tid))

        token.service.remove(tid)
        self.message("Login or password are wrong.")

    @form.button('Cancel')
    def cancelHandler(self):
        site = self.request.matchdict['site']
        return HTTPFound(location='http://%s'%site)


ptah.register_settings(
    'ploud-login',

    form.TextField(
        'backend',
        required = True,
        title = 'Backend server host.',
        default = '',
        ),

    title = 'Ploud login service'
)
