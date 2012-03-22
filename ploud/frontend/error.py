""" errors logging """
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

import ptah
from ptah import config, view, form, manage
from ploud.frontend import models, decorators
from ploud.frontend.root import PloudApplicationRoot
from ploud.frontend.models import Error


@manage.module('ploud-errors')
class PloudErrors(manage.PtahModule):
    """Ploud errors module."""

    title = 'Ploud errors'

    def __getitem__(self, key):
        try:
            eid = int(key)
        except:
            raise KeyError(key)

        error = ptah.get_session().query(Error).filter_by(id=eid).first()
        error.__parent__ = self
        error.__name__ = key
        return error


@view_config(
    context=PloudErrors, wrapper=ptah.wrap_layout(),
    renderer='ploud.frontend:newui/errorsmod.pt')
class ErrorsModuleView(ptah.View):

    def update(self):
        count = ptah.get_session().query(models.Error).count()
        self.errors = ptah.get_session().query(Error)\
            .order_by(Error.time.desc()).slice(0,50)


@view_config(
    context=Error, wrapper=ptah.wrap_layout(),
    renderer='ploud.frontend:newui/error.pt')
class ErrorView(form.Form):

    def fixed(self):
        return self.context.fixed

    def unfixed(self):
        return not self.context.fixed

    @form.button('Resolve', actype=form.AC_INFO, condition=unfixed)
    def resolveHandler(self):
        self.context.fixed = True
        self.message('Error has been marked as fixed.')

    @form.button('Re-Open', actype=form.AC_INFO, condition=fixed)
    def openHandler(self):
        self.context.fixed = False
        self.message('Error has been re-opened.')

    @form.button('Remove', actype=form.AC_DANGER)
    def removeHandler(self):
        ptah.get_session().delete(self.context)
        self.message('Error has been removed.')
        return HTTPFound(location='../')


@view_config(
    'errors.html', context=PloudApplicationRoot,
    wrapper=ptah.wrap_layout(),
    decorator=decorators.require_object_login,
    renderer='ploud.frontend:newui/errors.pt')
class ErrorsView(ptah.View):

    error = None
    errors = None

    title = 'Ploud Errors'

    def update(self):
        eid = None
        error = None
        errors = None
        try:
            eid = int(self.request.GET.get('eid'))
        except:
            pass

        if eid:
            error = ptah.get_session().query(Error).filter_by(id=eid).first()
            if error is not None:
                self.error = error
                return

        count = ptah.get_session().query(Error).count()
        self.errors = ptah.get_session().query(Error)\
            .order_by(Error.time.desc()).slice(0,50)
