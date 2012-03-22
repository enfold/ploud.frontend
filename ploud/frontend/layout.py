from ptah import view
from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget, authenticated_userid

import ptah
import ptah.cms
from ploud.utils.policy import POLICIES
from ploud.frontend.config import LAYER
from ploud.frontend.root import PloudApplicationRoot

import config
from models import User


ptah.layout.register(
    'workspace', context=PloudApplicationRoot, parent='page-frontend',
    renderer = 'ploud.frontend:newui/layout-workspace.pt')


#ptah.layout('', PloudApplicationRoot, parent='page-frontend', layer=LAYER)
#class Fake(view.Layout):
#    def render(self, content):
#        return content


@ptah.layout('page-frontend',
             PloudApplicationRoot,
             renderer="ploud.frontend:newui/layout.pt")

class MainLayout(ptah.View):

    manager = False

    def update(self):
        super(MainLayout, self).update()

        self.principal = principal = authenticated_userid(self.request)
        self.user = User.getByURI(principal)
        self.isanon = not self.user

        if principal and self.user is None:
            headers = forget(self.request)
            return HTTPFound(location='/', headers=headers)

        if not self.isanon:
            self.membership = self.user.membership_label()
            self.policy = POLICIES.get(self.user.type, 0)
            if self.user.type in (1, 2):
                self.policy_id = self.user.type
            else:
                self.policy_id = 'free'

            price = config.PRICES.get(self.policy.id, 'free')
            if price == 'free':
                self.price = 'free'
            else:
                self.price = '$%s'%price

            self.removes =  self.policy.removes - self.user.removes
            self.transfers =  self.policy.transfers - self.user.transfers
            sites = len([s for s in self.user.sites if not s.removed])
            self.sites = self.policy.sites - sites

            MANAGE = ptah.get_settings(ptah.CFG_ID_PTAH, self.request.registry)
            self.manager = self.user.email in MANAGE['managers']
            self.principal = self.user.email


@ptah.layout(
    'page', PloudApplicationRoot,
    renderer='ploud.frontend:newui/layout-page.pt')
class FrontendLayout(ptah.View):

    manager = False

    def update(self):
        super(FrontendLayout, self).update()

        self.principal = principal = authenticated_userid(self.request)
        self.user = User.getByURI(principal)
        self.isanon = not self.user

        if principal and self.user is None:
            headers = forget(self.request)
            return HTTPFound(location='/', headers=headers)

        if not self.isanon:
            self.membership = self.user.membership_label()
            self.policy = POLICIES.get(self.user.type, 0)
            if self.user.type in (1, 2):
                self.policy_id = self.user.type
            else:
                self.policy_id = 'free'

            price = config.PRICES.get(self.policy.id, 'free')
            if price == 'free':
                self.price = 'free'
            else:
                self.price = '$%s'%price

            self.removes =  self.policy.removes - self.user.removes
            self.transfers =  self.policy.transfers - self.user.transfers
            sites = len([s for s in self.user.sites if not s.removed])
            self.sites = self.policy.sites - sites

            MANAGE = ptah.get_settings(ptah.CFG_ID_PTAH, self.request.registry)
            self.manager = self.user.email in MANAGE['managers']
            self.principal = self.user.email
