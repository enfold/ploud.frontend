""" dashboard """
import simplejson as json
from datetime import timedelta
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget, authenticated_userid

import ptah
from ptah import token, form

from ploud.utils import maintenance
from ploud.utils import ploud_config
from ploud.utils.policy import POLICIES
from ploud.utils.vhost import addVirtualHosts, removeVirtualHosts

from ploud.frontend import decorators
from ploud.frontend.config import CHOICES

import utils, validators
from config import LOGIN_TOKEN_TYPE
from models import Site, User, Host
from root import PloudApplicationRoot
import utils


def addVirtualHost(site, hostname):
    host = Host(site.id, hostname.lower())
    ptah.get_session().add(host)
    addVirtualHosts((str(hostname),), 'plone41')


@view_config(
    route_name='dactions-vtransfer',
    decorator=decorators.require_object_login)
def validateTransfer_view(request):
    errors, data = validateTransfer(request)

    response = request.response
    response.content_type = 'text/json'
    response.body = json.dumps(errors)
    return response


def validateTransfer(request):
    site_id = request.params.get('site_id','')
    newowner = request.POST.get('newowner','').lower()
    principal = authenticated_userid(request)

    user = User.getByURI(principal)
    pol = POLICIES[user.type]
    if user.transfers >= pol.transfers:
        return {'newowner': "You are not allowed to transfer site."}, None

    if newowner == principal:
        return {'newowner': "Can't transfer sit to itself."}, None

    user = ptah.get_session().query(User).filter_by(email = newowner).first()
    if user is None:
        return {'newowner': 'User is not found.'}, None

    l = 0
    for s in user.sites:
        if not s.removed:
            l += 1

    remaining = POLICIES[user.type].sites - l
    if remaining <= 0:
        return {'newowner': 'User aready has created maximum number of allowed sites.'}, None

    data = {'site': site_id,
            'user_id': user.id,
            'type': user.type}
    return {}, data


@view_config(
    route_name='dactions-transfer',
    decorator=decorators.require_object_login)
def transfer(request):
    errors, data = validateTransfer(request)
    if errors:
        return HTTPFound(
            location="/dashboard.html?message=Can't transfer site.")

    site = ptah.get_session().query(Site).filter_by(id = data['site']).first()
    if site is None:
        return HTTPFound(
            location="/dashboard.html?message=Can't transfer site.")

    principal = authenticated_userid(request)
    user = User.getByURI(principal)
    if site.user_id != user.id:
        return HTTPFound(
            location="/dashboard.html?message=Can't transfer site.")

    user.transfers += 1

    site.user_id = data['user_id']

    # change policy
    hosts = [h.host for h in site.hosts]
    POLICIES[data['type']].changeHostsPolicy(hosts, site.site_name)

    # change owner of new site

    if maintenance.maintence is not None:
        maintenance.maintence.execute(hosts[0], 'ploud-fix-owner')

    return HTTPFound(
        location="/dashboard.html?message=Site has been transfered.")


@view_config(route_name='dactions-remove',
             decorator=decorators.require_object_login)
def remove(request):
    site = request.POST.get('site_id')
    site = ptah.get_session().query(Site).filter_by(id = site).first()
    if site is None:
        return HTTPFound(location="/dashboard.html?message=Can't find site.")

    principal = authenticated_userid(request)
    user = User.getByURI(principal)
    if site.user_id != user.id:
        return HTTPFound(location="/dashboard.html?message=Can't find site.")

    pol = POLICIES[user.type]
    if user.removes >= pol.removes:
        return HTTPFound(
            location="/dashboard.html?message=You are not allowed to remove site.")

    conn = ploud_config.PLOUD_POOL.getconn()
    cursor = conn.cursor()
    pol.removeSite(site.id, cursor)
    site.removed = True

    cursor.execute(
        "SELECT host FROM vhost WHERE id = %s", (site.id,))
    sites = [row[0] for row in cursor.fetchall()]
    if sites:
        cursor.execute(
            "DELETE FROM vhost WHERE id = %s", (site.id,))
        removeVirtualHosts(sites)

    site.site_name = 'site_for_removing_%s'%site.id

    user.removes += 1
    cursor.close()
    conn.commit()
    ploud_config.PLOUD_POOL.putconn(conn)

    return HTTPFound(location="/dashboard.html?message=Site has been removed.")


@view_config(route_name='dactions-login',
             decorator=decorators.require_object_login)
def login(request):
    site_id = request.params.get('site_id', '')
    try:
        site_id = int(site_id)
    except:
        return HTTPFound(location = '/dashboard.html')

    site = ptah.get_session().query(Site).filter_by(id = site_id).first()
    if site is None:
        return HTTPFound(
            location = "/dashboard.html?message=Can't find site information.")

    principal = authenticated_userid(request)
    user = User.getByURI(principal)
    if user is None:
        return HTTPFound(
            location = "/dashboard.html?message=Can't find site information.")

    if site.user_id != user.id:
        return HTTPFound(
            location = "/dashboard.html?message=Can't find site information.")

    data = '%s::%s'%(user.email, user.password)
    tid = token.service.generate(LOGIN_TOKEN_TYPE, data)
    return HTTPFound(location='http://%s/authToken?token=%s'%(site.hosts[0].host, tid))


@view_config(
    route_name='dashboard',
    wrapper=ptah.wrap_layout('page-frontend'),
    decorator=decorators.require_object_login,
    renderer='ploud.frontend:newui/dashboard.pt')
class Dashboard(ptah.View):

    def siteChoices(self):
        site_types = list(CHOICES)
        choices = dict(CHOICES)
        for site in self.user.sites:
            if site.removed:
                continue
            name = site.site_name + ' (' + choices[site.typeof] + ')'
            site_types.append((site.site_name, name))

        return site_types

    def languageChoices(self):
        return utils.languages()

    def _site_actions(self):
        """ Generate the actions available for each site.
            This will also take into considerations what user/policy enabled

<a href="../change-name-1/index.html" class="colorbox disabled-anchor modal-cta-find:change-name-1" title="Change the URL of this site">Change name</a></li>

        """
        available = ['remove', 'change_domain', 'change_ownership']
        actions = {}

        ptype = self.user.type

        for site in self.user.sites:
            info = {'site_name' : site.site_name,
                    'remove' : {'available':False},
                    'change_domain' : {'available':False},
                    'change_ownership' : {'available':False}}

            if ptype in (0, 1, 2, 99):
                info['remove'].update(available = True)
            if ptype in (1, 2, 99):
                info['change_domain'].update(available = True)
            if ptype in (1, 2, 99):
                info['change_ownership'].update(availale = True)

            actions[site.site_name] = info

            """ XXX must compute if available clones, deletes, etc
            """
        return actions

    def update(self):
        request = self.request

        self.status = {}
        self.message = ''

        principal = authenticated_userid(request)
        self.user = user = User.getByURI(principal)
        self.user_type = user.type

        # user has been removed
        if user is None:
            headers = forget(request)
            return HTTPFound(location='/', headers=headers)

        self.policy = policy = POLICIES[user.type]

        self.allowRemove = user.removes < policy.removes
        self.allowTransfer = user.transfers < policy.transfers
        self.allowChangehost = False
        if user.type in (1, 2, 99):
            self.allowChangehost = True

        self.urls = urls = []
        self.stats = stats = {'db': 0, 'bw': 0,
                              'vhosts': policy.vhosts, 'bots': policy.bots}

        PLOUD = ptah.get_settings('ploud', self.request.registry)
        host = PLOUD['domain']

        _site_actions = self._site_actions()

        for site in user.sites:
            if site.removed:
                continue

            vhost = ptah.get_session().query(Host).filter_by(id=site.id).first()

            urls.append({'url': 'http://%s/' % vhost.host,
                         'id': site.id,
                         'site_name': site.site_name,
                         'host': vhost.host,
                         'db': '%0.2fMb'%(site.size/1048576.0),
                         'disabled': site.disabled,
                         'site_id': site.id,
                         'hostname' : vhost and vhost.host or None,
                         'bw': '%0.2fMb'%((site.bwin+site.bwout)/1048576.0),
                         'actions' : _site_actions[site.site_name]})

            stats['db'] = stats['db'] + site.size
            stats['bw'] = stats['bw'] + site.bwin + site.bwout

        urls = sorted(urls, key=lambda site: site['site_name'])
        max_provisioned = policy.sites
        self.remaining = max_provisioned - len(urls)
        self.allowCreate = False if self.remaining <=0 else True #bool(self.remaining)

        stats['db_pc'] = '%0.1f'%(stats['db'] / (policy.dbsize/100.0))
        stats['db'] = '%0.2f Mb'%(stats['db']/1048576.0)
        stats['db_to'] = '%d Mb'%(policy.dbsize/1048576)

        stats['bw_pc'] = '%0.1f'%(stats['bw'] / (policy.bandwidth/100.0))
        stats['bw'] = '%0.2f Mb'%(stats['bw']/1048576.0)
        stats['bw_to'] = '%d Mb'%(policy.bandwidth/1048576)

        createSite = request.POST.get('form-create-site', None)
        if createSite is not None:
            res = self.createSite()
            if isinstance(res, HTTPFound):
                return res

        return {'stats': stats, 'urls': urls}

    def createSite(self):
        request = self.request

        if not self.allowCreate:
            self.message = "Can't create more sites."
            return

        site_name = request.POST.get('createsite-site-name', '').lower()
        site_type = request.POST.get('createsite-site-type', '').lower()
        site_language = request.POST.get('createsite-site-language', 'en').lower()

        try:
            validators.checkSitename(None, site_name)
        except form.Invalid, e:
            self.status['createsite-site-name'] = e.msg
            return

        choices = dict(CHOICES)
        template_id = None
        if not site_type in choices:
            found = False
            for site in self.user.sites:
                if site.site_name == site_type:
                    template_id = site.id
                    site_type = site.typeof
                    found = True
                    break
            if not found:
                self.message = "Can't create template from nonexistent site %s." % site_type
                return

        print site_type, site_name, template_id
        site = utils.provision_site(self.user, site_type, site_name, template_id, site_language)
        return HTTPFound(
            location="/dashboard.html?message=New site has been created.")
