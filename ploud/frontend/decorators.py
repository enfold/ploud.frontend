"""Decorators to alter the behavior of view functions."""
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid


def require_object_login(view):
    """Require that the user be logged in to access the view function."""

    def wrapper(context, request):
        email = authenticated_userid(request)
        if email is None:
            return HTTPFound(location='/index.html')
        else:
            return view(context, request)

    return wrapper
