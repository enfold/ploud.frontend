import transaction
import smtplib, random, sys, os
from email.mime.text import MIMEText

from pyramid.httpexceptions import HTTPFound
from pyramid import renderers
from pyramid.security import authenticated_userid

import ptah
from ptah import view

from ploud.utils import ploud_config
from ploud.frontend.config import log, ALLOWED_SITE_NAME_CHARS
from ploud.frontend import models, signup, utils
from ploud.frontend.root import PloudApplicationRoot


class WaitingList(ptah.View):
    #view.pview(
    #    'waitinglist.html', PloudApplicationRoot, layout='page-frontend',
    #    template = view.template('ploud.frontend:newui/waitinglist.pt'))

    title = 'Waiting list'

    def update(self):
        PLOUD = ptah.get_settings('ploud', self.request.registry)
        allowed = PLOUD.registration
        if allowed:
            return HTTPFound(location = '/signup.html')

        request = self.request
        principal = authenticated_userid(request)
        if principal:
            return HTTPFound(location = '/dashboard.html')

        email = request.POST.get('email', '').lower()
        self.completed = request.POST.get('completed')

        if self.completed and not utils.isValidMailAddress(email):
            view.addMessage(request, 'E-Mail is required.')
            self.completed = False
            return

        exists = ptah.get_session().query(
            models.WaitingList).filter_by(email=email).all()
        if email and not exists:
            exists = ptah.get_session().query(
                models.User).filter_by(email=email).all()

            if not exists:
                entry = models.WaitingList(email)
                ptah.get_session().add(entry)
                ptah.get_session().flush()
                self.send_confirmation(email)

            if email and exists:
                view.addMessage(
                    request,
                    'The email account %s is aleady on the list.' % email)
                self.completed = False

    def send_confirmation(self, email):
        template = renderers.get_renderer('newui/waitinglist_email.txt').implementation()
        data = dict(host=EMAIL_HOST, email=email)
        msg = MIMEText(str(template(**data)))
        msg['Subject'] = 'Ploud waiting list'
        msg['From'] = EMAIL_FROM
        msg['To'] = email

        try:
            server = smtplib.SMTP(MTA)
            server.sendmail(EMAIL_FROM, [email], msg.as_string())
            server.quit()
        except Exception, e:
            log.exception(str(e))
            print msg.as_string()


def enableUser():
    email = sys.argv[1]
    ploud_config.initializeConfig()
    dsn = PLOUD.dsn
    models.initialize_sql(dsn)
    config = Configurator()
    config.manager.push({'registry': config.registry, 'request': None})

    conn = ploud_config.PLOUD_POOL.getconn()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM waitinglist "
                   "WHERE completed = %s and email=%s",(False,email))

    row = cursor.fetchone()
    if row is None:
        print "Can't find email: %s"%email
        return

    transaction.begin()
    password = ''.join(
        [random.choice(ALLOWED_SITE_NAME_CHARS) for i in range(8)])
    user = models.User(email, password)
    user.type = 0
    token = user.token
    ptah.get_session().add(user)
    print email, token
    signup.send_activation(email, token)

    cursor.execute("UPDATE waitinglist SET completed = %s WHERE email=%s",
                   (True, email))
    cursor.close()
    conn.commit()
    transaction.commit()
