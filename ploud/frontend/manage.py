""" management """
import bsddb, simplejson
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from sqlalchemy.sql.expression import asc

import ptah
from ptah.token import service
from ptah import view, config, form, manage

from ploud.utils import ploud_config
from ploud.utils.policy import POLICIES
from ploud.utils.disable import disableVhosts, enableVhosts

import utils
from config import MNGLOGIN_TOKEN_TYPE
from models import User, Site
from ploud.frontend.root import PloudApplicationRoot


@manage.module('ploud')
class Management(manage.PtahModule):
    """Ploud Frontend management module."""

    title = 'Ploud management'

    def __getitem__(self, key):
        try:
            key = int(key)
        except:
            raise KeyError(key)

        user = ptah.get_session().query(User).filter_by(id=key).first()
        user.__parent__ = self
        user.__name__ = str(key)
        return user


@view_config(
    context=Management,
    wrapper=ptah.wrap_layout(),
    renderer='ploud.frontend:newui/manage.pt')
class UsersList(ptah.View):

    users = ()
    sites = ()

    def update(self):
        request = self.request

        action = None
        param = request.params.get('search', '')

        if 'searchusers' in request.POST:
            action = 'searchusers'
            request.session['manage_param'] = param
            request.session['manage_action'] = action

        if 'showusers' in request.POST:
            action = 'showusers'
            request.session['manage_param'] = param
            request.session['manage_action'] = action

        if 'searchsites' in request.POST:
            action = 'searchsites'
            request.session['manage_param'] = param
            request.session['manage_action'] = action

        if 'showsites' in request.POST:
            action = 'showsites'
            request.session['manage_param'] = param
            request.session['manage_action'] = action

        if action is None:
            param = request.session.get('manage_param', None)
            action = request.session.get('manage_action', None)

        if action == 'searchusers':
            self.users = ptah.get_session().query(User)\
                .filter(User.email.contains('%%%s%%'%param))\
                .order_by(asc('id')).all()

        elif action == 'showusers':
            self.users = ptah.get_session().query(User).order_by(asc('id')).all()

        if action == 'searchsites':
            self.sites = ptah.get_session().query(Site)\
                .filter(Site.site_name.contains('%%%s%%'%param))\
                .order_by(asc('id')).all()
            self.sites = [site for site in self.sites if not site.removed]

        elif action == 'showsites':
            self.sites = ptah.get_session().query(Site).order_by(asc('id')).all()
            self.sites = [site for site in self.sites if not site.removed]


policies = form.SimpleVocabulary(
    form.SimpleTerm(0, '0', 'Type 0 (Free)'),
    form.SimpleTerm(1, '1', 'Type 1 (Basic 20$)'),
    form.SimpleTerm(2, '2', 'Type 2 (Full 60$)'),
    form.SimpleTerm(98, '98', 'Type 98 (Un-validated)'),
    form.SimpleTerm(99, '99', 'Type 99 (Superuser)'))


PolicySchema = form.Fieldset(
    form.RadioField(
        'policy',
        title = u'Membership type',
        description = u'Choose user membership type.',
        validator = form.OneOf(policies),
        vocabulary = policies)
)


@view_config(
    context=User,
    wrapper=ptah.wrap_layout(),
    renderer='ploud.frontend:newui/userinfo.pt')
class UserView(form.Form):

    prefix = 'user_info'
    fields = PolicySchema

    def update(self):
        super(UserView, self).update()

        user = self.context
        request = self.request
        policy = POLICIES[user.type]

        size = 0
        bandwidth = 0
        for site in user.sites:
            if site.removed:
                continue
            size += site.size
            bandwidth += site.bwin
            bandwidth += site.bwout

        self.sites = len(user.sites)
        self.dbsize = '%0.2fMb (%0.1f%%)'%(
            size/1048576.0, size / (policy.dbsize/100.0))
        self.bandwidth = '%0.2fMb (%0.1f%%)'%(
            bandwidth/1048576.0, bandwidth / (policy.bandwidth/100.0))

        site_infos = []
        if not bandwidth:
            bandwidth = 0.000001
        if not size:
            size = 0.000001

        for site in user.sites:
            if site.removed:
                continue

            site_form = SiteForm(user, site, request)
            site_form.update()

            site_infos.append(
                {'id': '%s/%s'%(site.id, site.typeof),
                 'site_id': site.id,
                 'name': site.site_name,
                 'last_accessed': site.last_accessed,
                 'disabled': str(site.disabled),
                 'dbsize': '%0.2fMb (%0.1f%%)'%(
                        site.size/1048576.0, site.size / (size/100.0)),
                 'bandwidth': '%0.2fMb (%0.1f%%)'%(
                        (site.bwin+site.bwout)/1048576.0,
                        (site.bwin+site.bwout) / (bandwidth/100.0)),
                 'form': site_form,
                 'host': site.hosts[0].host})
        self.site_infos = site_infos
        self.sites = len(site_infos)

        self.change_password = ChangePasswordForm(user, request)
        self.change_password.update()

    def form_content(self):
        return {'policy': self.context.type}

    @form.button(u'Update', actype=form.AC_PRIMARY)
    def changeUserType(self):
        data, errors = self.extract()

        if not errors:
            self.message("User's membership type has been change.")

            user = self.context
            if user.type != data['policy']:
                user.type = data['policy']

                conn = ploud_config.PLOUD_POOL.getconn()
                cursor = conn.cursor()
                POLICIES[user.type].apply(user.id, cursor)
                cursor.close()
                conn.commit()
                ploud_config.PLOUD_POOL.putconn(conn)

    @form.button(u'Remove User', actype=form.AC_DANGER)
    def removeHandler(self):
        user = self.context
        ptah.get_session().delete(user)
        self.message("User has been removed.")
        return HTTPFound(location='../index.html')


class ChangePasswordForm(form.Form):

    prefix = 'user_password'
    fields = form.Fieldset(
        form.TextField(
            'password',
            title = u'Change password'))

    @form.button('Change', actype=form.AC_PRIMARY)
    def changePassword(self):
        data, errors = self.extract()

        if not errors:
            self.message("Password has been changed")

            self.context.password = data['password']


class SiteForm(form.Form):

    fields = form.Fieldset(
        form.BoolField(
            'disabled',
            title = u'Disabled'))

    def __init__(self, user, site, request):
        self.context = site
        self.request = request

        self.prefix = 'site%s'%site.id
        self.__paernt__ = user

    def form_content(self):
        return {'disabled': self.context.disabled}

    @form.button(u'Update')
    def updateHandler(self):
        data, errors = self.extract()

        if not errors:
            site = self.context

            if site.disabled != data['disabled']:
                site.disabled = data['disabled']
                if site.disabled:
                    utils.disableHost(site)
                else:
                    utils.enableHost(site)

            self.message('Site info has been updated.')

    @form.button(u'Remove', actype=form.AC_DANGER)
    def updateHandler(self):
        return HTTPFound(location='removesite.html?id=%s'%self.context.id)


@view_config(
    'removesite.html', context=User,
    wrapper=ptah.wrap_layout(),
    renderer='ploud.frontend:newui/removesite.pt')
class RemoveSiteView(form.Form):

    def update(self):
        site = None
        try:
            id = int(self.request.params.get('id'))
            for s in self.context.sites:
                if s.id == id:
                    site = s
                    break
            if site is not None:
                self.site = site
        except HTTPFound:
            raise
        except:
            pass

        if site is None:
            self.message('Site id is required.')
            return HTTPFound(location='index.html')

        super(RemoveSiteView, self).update()

    @form.button(u'Remove', actype=form.AC_DANGER)
    def removeHandler(self):
        user = self.context
        conn = ploud_config.PLOUD_POOL.getconn()
        cursor = conn.cursor()

        pol = POLICIES[user.type]
        pol.removeSite(self.site.id, cursor)

        self.site.removed = True
        cursor.close()
        conn.commit()
        ploud_config.PLOUD_POOL.putconn(conn)
        self.message("Site has been removed.")
        return HTTPFound(location='index.html')

    @form.button(u'Cancel')
    def cancelHandler(self):
        return HTTPFound(location='index.html')


@view_config('login', context=Management)
def managerLogin(request):
    sid = request.params.get('id')

    if sid:
        site = ptah.get_session().query(Site).filter_by(id=sid).first()
        if site is not None:
            # login
            token = service.generate(MNGLOGIN_TOKEN_TYPE, site.id)
            host = site.hosts[0]
            return HTTPFound(
                location='http://%s/authToken?token=%s'%(host.host, token))

    return HTTPFound(location='/ptah-manage/ploud/')


@view_config('listprocs', context=PloudApplicationRoot)
def listProcesses(request):
    cfg = ptah.get_settings('apache')
    processes = cfg['processes']
    lbfile = cfg['lbfile']

    h = bsddb.hashopen(lbfile, 'r')

    data = {}

    for key in h.keys():
        id = h[key]
        if id in data or '.' not in key:
            continue
        else:
            data[id] = key
            if len(data) == processes:
                break
    h.close()

    request.response.headerslist = {'Content-Type': 'application/json'}
    request.response.body = simplejson.dumps(data)
    return request.response
