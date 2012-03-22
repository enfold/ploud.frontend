""" membership """
import ptah
from pyramid.view import view_config
from pyramid.security import authenticated_userid

from models import User


@view_config(
    route_name='frontend-membership',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/membership.pt')
class MembershipView(ptah.View):

    policy = 0

    def update(self):
        uri = authenticated_userid(self.request)
        user = User.getByURI(uri)
        if user is not None:
            info = {'email': user.email,
                    'policy': getattr(user, 'type', 0)}
            self.policy = info['policy']
        else:
            info = {'email': 'anonymous subscription',
                    'policy': 98}
        self.user = user
        self.isAnon = user is None
        return info


@view_config(
    route_name='frontend-membership1',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/membership-free.pt')
def view(request):
    return {}

@view_config(
    route_name='frontend-membership2',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/membership1.pt')
def view(request):
    return {}

@view_config(
    route_name='frontend-membership3',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/membership2.pt')
def view(request):
    return {}
