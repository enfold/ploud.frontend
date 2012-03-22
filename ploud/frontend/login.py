""" login """
import simplejson as json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from sqlalchemy.sql import expression as expr

from pyramid import renderers
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid, remember, forget

import ptah
from ptah.token import service as tokenService

from ploud.frontend.models import User
from ploud.frontend.config import log, PASSWORD_RESET_TOKEN_TYPE


@view_config(route_name='frontend-login-val')
def validate_login_view(request):
    errors = validate_login(request)

    response = request.response
    response.content_type = 'text/json'
    response.body = json.dumps(errors)
    return response


def validate_login(request):
    errors = {}

    email = request.POST.get('login-email', '').lower()
    password = request.POST.get('login-password', '')

    user = ptah.get_session().query(User).filter_by(email=email).first()
    if user is None:
        errors['login-email'] = 'Account not found.'
        return errors

    if not ptah.pwd_tool.check(user.password, password):
        errors['login-password'] = 'Incorrect password, please try again.'

    return errors


@view_config(route_name='frontend-login')
def loginView(request):
    principal = authenticated_userid(request)
    if principal:
        return HTTPFound(location='/dashboard.html')

    errors = validate_login(request)
    if errors:
        return HTTPFound(location='/index.html')

    email = request.POST.get('login-email', '').lower()
    user = ptah.get_session().query(User).filter_by(email=email).first()

    headers = remember(request, user.__uri__)
    return HTTPFound(location='/dashboard.html', headers=headers)


@view_config(route_name='frontend-logout')
def LogoutView(request):
    principal = authenticated_userid(request)
    if principal is not None:
        headers = forget(request)
        return HTTPFound(location='/index.html', headers=headers)
    else:
        return HTTPFound(location='/index.html')


@view_config(route_name='frontend-rpw-v')
def validate_resetpw_view(request):
    errors = validate_resetpw(request)

    response = request.response
    response.content_type = 'text/json'
    response.body = json.dumps(errors)
    return response


def validate_resetpw(request):
    email = request.POST.get('login-email', '').lower()

    if not email:
        return {'login-email': u"Can't find login information."}

    user = ptah.get_session().query(User).filter_by(email=email).first()
    if user is None:
        return {'login-email': u"Can't find login information."}

    return {}


@view_config(
    route_name='frontend-resetpw',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/resetpassword.pt')
class ResetPassword(ptah.View):

    status = None

    def update(self):
        if "form.resetpw" not in self.request.POST:
            return

        errors = validate_resetpw(self.request)

        if not errors:
            email = self.request.POST.get('login-email').lower()
            user = ptah.get_session().query(User).filter_by(email=email).first()
            if user is None:
                msg = "Can't rest password for this login."
                return HTTPFound(location='/reset-password.html?message=%s'%msg)

            token = tokenService.generate(
                PASSWORD_RESET_TOKEN_TYPE, user.id)
            send_new_password_email(email, token)
            success = "You've reset your password. Please check your email."
            return HTTPFound(location='/index.html?message=%s'%success)


@view_config(
    route_name='frontend-changepw',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/changepassword.pt')
class ChangePassword(ptah.View):

    message = ''
    token = None
    userid = None

    td = timedelta(hours=1)

    def update(self):
        request = self.request

        principal = authenticated_userid(request)
        user = User.getByURI(principal)
        if user is None:
            self.token = token = request.params.get('token')
            if token:
                self.userid = tokenService.get(token)
                if self.userid is None:
                    return HTTPFound(location='/reset-password.html')

                user = User.getById(self.userid)

        if user is None:
            return HTTPFound(location='/reset-password.html')

        if 'form-change' in request.POST:
            password = request.POST.get('change-password')
            confirm = request.POST.get('confirm-password')
            if not password:
                return

            if password != confirm:
                self.message = \
                    'Password and Confirm password has to be identical.'

            if self.userid is not None:
                tokenService.remove(self.token)

            user.password = ptah.pwd_tool.encode(password)
            if not user.validated:
                user.validated = datetime.now()

            headers = {}
            if not principal:
                headers = remember(request, user.__uri__)

            return HTTPFound(
                location='/dashboard.html?message=Password has been changed',
                headers = headers)

        token = request.params.get('token')
        if not token and user is None:
            return HTTPFound(location='/dashboard.html')


def send_new_password_email(email, token):
    MAIL = ptah.get_settings(ptah.CFG_ID_PTAH)
    FRONTEND = ptah.get_settings('frontend')

    data = dict(host=FRONTEND['host'], email=email, token=token)

    text = renderers.render('ploud.frontend:newui/reset_password.txt', data)

    msg = MIMEText(text.encode('utf-8'))
    msg['Subject'] = "You've Reset Your Ploud Password"
    msg['From'] = FRONTEND['email_from']
    msg['To'] = email

    MAIL['Mailer'].send(FRONTEND['email_from'], email, msg)
