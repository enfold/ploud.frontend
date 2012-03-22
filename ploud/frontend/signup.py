""" signup form """
import datetime, random
import simplejson as json
from email.mime.text import MIMEText
import transaction
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid import renderers
from pyramid.security import remember, authenticated_userid

import ptah
from ptah import view, config, form

from ploud.utils import ploud_config
from ploud.utils.policy import POLICIES
from ploud.frontend import utils, validators
from ploud.frontend.config import log, ALLOWED_SITE_NAME_CHARS
from ploud.frontend.models import User, Site
from root import PloudApplicationRoot


def lower(s):
    if isinstance(s, basestring):
        return s.lower()
    return s


SignupSchema = ptah.form.Fieldset(
    ptah.form.TextField(
        'signup-email',
        preparer = lower,
        validator = ptah.form.All(ptah.form.Email(), validators.checkEmail)),

    ptah.form.TextField(
        'signup-site-name',
        preparer = lower,
        validator = validators.checkSitename),
    )


@view_config(route_name='signup-validate')
def validate_signup_view(request):
    errors, data = validate_signup(request)

    response = request.response
    response.content_type = 'text/json'
    response.body = json.dumps(errors)
    return response


def validate_signup(request):
    fields = SignupSchema.bind(None, request.POST)
    data, errs = fields.extract()

    errors = {}
    for err in errs:
        if err.field:
            errors[err.field.name] = err.msg

    if not errors:
        toc = request.POST.get('signup-accept-toc', '').lower()
        if toc not in ('true', '1'):
            errors = {'signup-accept-toc':
                      'You must accept Terms and Conditions'}

    data['signup-site-language'] = request.POST.get('signup-site-language', 'en')
    return errors, data


@view_config('signup', context=PloudApplicationRoot)
def SignupView(request):
    PLOUD = ptah.get_settings('ploud', request.registry)
    allowed = PLOUD['registration']
    if not allowed:
        return HTTPFound(location = '/waitinglist.html')

    principal = authenticated_userid(request)
    if principal:
        return HTTPFound(location = '/dashboard.html')

    errors, data = validate_signup(request)
    if errors:
        return HTTPFound(location='/index.html')

    email = data['signup-email']
    site_name = data['signup-site-name']
    site_language = data['signup-site-language']
    password = ''.join(
        random.choice(ALLOWED_SITE_NAME_CHARS) for i in range(8))

    user = User(email, ptah.pwd_tool.encode(password), 98)
    token = user.token
    Session = ptah.get_session()
    Session.add(user)
    Session.flush()

    uri = user.__uri__

    FE = ptah.get_settings('frontend', request.registry)

    if FE['validation']:
        send_activation(email, token)
    else:
        user.type = 0
        user.token = None
        user.validated = datetime.datetime.now()

    try:
        utils.provision_site(user, 'plone41', site_name, language=site_language)
    except Exception, exc:
        transaction.abort()
        errors = {'signup-site-name': str(exc)}
        log.exception('Site provision problem')
        return HTTPFound(location='/index.html')

    headers = remember(request, uri)
    return HTTPFound(location='/dashboard.html', headers=headers)


@view_config(route_name='validate')
class Validate(ptah.View):

    def update(self):
        token = self.request.GET.get('token')

        user = ptah.get_session().query(User).filter_by(token=token).first()
        if user is not None:
            user.type = 0
            user.token = None
            user.validated = datetime.datetime.now()

            # change policy to 0 (free)
            conn = ploud_config.PLOUD_POOL.getconn()
            cursor = conn.cursor()
            POLICIES[user.type].apply(user.id, cursor)
            cursor.close()
            conn.commit()
            ploud_config.PLOUD_POOL.putconn(conn)

            headers = remember(self.request, user.__uri__)
            return HTTPFound(location = '/change-password.html', headers = headers)
        else:
            return HTTPFound(location="/index.html?message=Can't validate email address.")


def send_activation(email, token):
    mail_template = renderers.get_renderer(
        'newui/validate_email.txt').implementation()

    MAIL = ptah.get_settings(ptah.CFG_ID_PTAH)
    FRONTEND = ptah.get_settings('frontend')

    data = dict(host=FRONTEND['host'], email=email, token=token)
    msg = MIMEText(str(mail_template(**data)))
    msg['Subject'] = 'Activate Your Ploud Account'
    msg['From'] = FRONTEND['email_from']
    msg['To'] = email

    MAIL['Mailer'].send(FRONTEND['email_from'], email, msg)
