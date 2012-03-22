""" dashboard """
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

import ptah
from ptah import view

from ploud.utils import ploud_config
from ploud.utils.policy import POLICIES
from ploud.utils.vhost import addVirtualHosts, removeVirtualHosts

from ploud.frontend import decorators
from ploud.frontend.config import CHOICES

import utils, validators
from models import Site, User, Host
from root import PloudApplicationRoot


@view_config(
    route_name='daction-changehostname',
    wrapper=ptah.wrap_layout('page-frontend'),
    decorator=decorators.require_object_login,
    renderer='ploud.frontend:newui/changehostname.pt')
class ChangeHostname(ptah.View):

    def update(self):
        request = self.request

        site = request.params.get('site')
        site = ptah.get_session().query(Site).filter_by(id=site).first()
        if site is None:
            return HTTPFound(location="/dashboard.html?message=Can't find site.")

        self.site = site

        self.host = ''
        for host in site.hosts:
            self.host = host.host
            break

        principal = authenticated_userid(request)
        user = User.getByURI(principal)
        if site.user_id != user.id:
            return HTTPFound(location="/dashboard.html?message=Can't find site.")

        pol = POLICIES[user.type]

        if not pol.vhosts:
            url = '/dashboard.html?message='
            url += 'Virtual hosting is not available for your type of '
            url += 'membership.'
            return HTTPFound(location=url)

        if 'form-change' not in request.POST:
            return

        hostname = request.POST.get('hostname','').strip().lower()
        PLOUD = ptah.get_settings('ploud', self.request.registry)
        if hostname.endswith('.%s'%PLOUD['domain']) and \
                hostname != '%s.%s'%(site.site_name, PLOUD['domain']):
            self.message = "%s domain is not allowed."%PLOUD['domain']
            return

        if hostname == self.host:
            return HTTPFound(location='/dashboard.html?message=Site now has new hostname.')


        conn = ploud_config.PLOUD_POOL.getconn()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT host FROM vhost WHERE id = %s", (site.id,))
        sites = [row[0] for row in cursor.fetchall()]
        if sites:
            cursor.execute(
                "DELETE FROM vhost WHERE id = %s", (site.id,))
            removeVirtualHosts(sites)

        cursor.execute("INSERT INTO vhost(id, host) VALUES(%s, %s)",
                       (site.id, hostname))
        addVirtualHosts((str(hostname),), 'plone41')
        pol.changeHostsPolicy((hostname,), site.site_name)

        cursor.close()
        conn.commit()
        ploud_config.PLOUD_POOL.getconn(conn)

        return HTTPFound(location='/dashboard.html?message=Site now has new hostname.')
