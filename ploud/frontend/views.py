""" views """
import ptah
import os.path
import utils
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from root import IPloudApplicationRoot


@view_config(route_name='frontend-favicon')
class FaviconView(ptah.View):

    icon_path = os.path.join(
        os.path.dirname(__file__), 'assets', '_img-ui', 'favicon.ico')

    def __call__(self):
        response = self.request.response
        response.content_type='image/x-icon'
        response.body = open(self.icon_path).read()
        return response


@view_config(route_name='frontend-robots')
class RobotsView(ptah.View):

    robots_path = os.path.join(
        os.path.dirname(__file__), 'assets', 'robots.txt')

    def __call__(self):
        response = self.request.response
        response.content_type = 'text/plain'
        response.body = open(self.robots_path).read()
        return response


@view_config('', context=IPloudApplicationRoot)
def default(request):
    return HTTPFound(location='/index.html')


@view_config(
    route_name='frontend-home',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/homepage.pt')
def homepage(request):
    return {
        'isanon': 1 if authenticated_userid(request) else 0,
        'languages': utils.languages(),
    }


@view_config(route_name='frontend-themes')
def themes(request):
    return HTTPFound(location = '/themes/')


@view_config(
    route_name='frontend-policy',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/privacy-policy.pt')
def view(request):
    return {}

@view_config(
    route_name='frontend-toc',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/terms-of-service.pt')
def view(request):
    return {}

@view_config(
    route_name='frontend-disabled',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/disabled_site.pt')
def view(request):
    return {}

@view_config(
    route_name='frontend-404',
    wrapper=ptah.wrap_layout('page-frontend'),
    renderer='ploud.frontend:newui/404.pt')
def view(request):
    request.response.status = 404
    return {}
