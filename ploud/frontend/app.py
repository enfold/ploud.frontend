""" wsgi app """
import ptah
import transaction
from pyramid.config import Configurator
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS
from pyramid.i18n import TranslationStringFactory

from ploud.frontend.models import User
from ploud.frontend.root import PloudApplicationRoot
from ploud.themegallery.permissions import GALLERY_ACL
from ploud.themegallery.gallery import ThemeGallery, ThemeGalleryPolicy

MessageFactory = _ = TranslationStringFactory('ploud.frontend')


class ApplicationPolicy(object):

    __name__ = ''
    __parent__ = None

    def __init__(self, request):
        self.request = request


def main(global_config, **settings):
    """ This is your application startup.
    """

    # mount application to '/' location wit custom ApplicationRoot
    factory = ptah.cms.ApplicationFactory(
        PloudApplicationRoot,
        '/', 'root', 'Ptah CMS', ApplicationPolicy, default_root=True)

    config = Configurator(root_factory=factory, settings=settings)
    config.scan('ploud.themegallery')
    config.scan('ploud.frontend')
    config.scan('ploud.utils')

    # init sqlalchemy
    config.ptah_init_sql()

    # init ptah settings
    config.ptah_init_settings()

    # enable rest api
    config.ptah_init_rest()

    # enable ptah manage
    config.ptah_init_manage()

    # populate db
    config.ptah_populate()

    # frontend routes
    config.add_route(
        'login', '/sso-login/{site}/', use_global_views=True)

    config.add_route(
        'frontend-membership', '/membership.html', use_global_views=True)
    config.add_route(
        'frontend-membership1', '/membership-free.html', use_global_views=True)
    config.add_route(
        'frontend-membership2', '/membership-1.html', use_global_views=True)
    config.add_route(
        'frontend-membership3', '/membership-2.html', use_global_views=True)

    config.add_route(
        'dactions-vtransfer', '/actions.html/validateTransfer',
        use_global_views=True)
    config.add_route(
        'dactions-transfer', '/actions.html/transfer', use_global_views=True)
    config.add_route(
        'dactions-remove', '/actions.html/remove', use_global_views=True)
    config.add_route(
        'dactions-login', '/actions.html/login', use_global_views=True)
    config.add_route(
        'dashboard', '/dashboard.html', use_global_views=True)

    config.add_route(
        'frontend-login', '/login.html', use_global_views=True)
    config.add_route(
        'frontend-login-val', '/login.html/validate', use_global_views=True)
    config.add_route(
        'frontend-logout', '/logout.html', use_global_views=True)
    config.add_route(
        'frontend-resetpw', '/reset-password.html', use_global_views=True)
    config.add_route(
        'frontend-rpw-v','/reset-password.html/validate', use_global_views=True)
    config.add_route(
        'frontend-changepw', '/change-password.html', use_global_views=True)

    config.add_route(
        'frontend-home', '/index.html', use_global_views=True)
    config.add_route(
        'frontend-favicon', '/favicon.ico')
    config.add_route(
        'frontend-robots', '/robots.txt')
    config.add_route(
        'frontend-policy', '/privacy-policy.html', use_global_views=True)
    config.add_route(
        'frontend-toc', '/terms-of-service.html', use_global_views=True)
    config.add_route(
        'frontend-disabled', '/disabled.html', use_global_views=True)
    config.add_route(
        'frontend-404', '/404.html', use_global_views=True)
    config.add_route(
        'frontend-themes', '/themes', use_global_views=True)

    config.add_route(
        'signup-validate', '/signup/validate', use_global_views=True)
    config.add_route(
        'validate', '/validate', use_global_views=True)

    config.add_route(
        'daction-changehostname', '/changehostname.html', use_global_views=True)

    config.add_static_view('_ploud', 'ploud.frontend:assets')

    # theme gallery
    themeGalleryFactory = ptah.cms.ApplicationFactory(
        ThemeGallery, '/themes/', 'themes', 'Theme gallery',
        ThemeGalleryPolicy, config=config, parent_factory=factory)

    config.add_route(
        'ploud-theme-gallery', '/themes/*traverse',
        factory=themeGalleryFactory, use_global_views = True)

    # set ptah mailer
    from pyramid_mailer.interfaces import IMailer
    mailer = config.registry.getUtility(IMailer)
    config.ptah_init_mailer(mailer.direct_delivery)

    # give managers all permissions
    #acl = [(Allow, Everyone, ptah.cms.View)]
    #PTAH = config.ptah_get_settings(ptah.CFG_ID_PTAH)
    #for login in PTAH['managers']:
    #    user = User.get(login)
    #    if user is not None:
    #        acl.append((Allow, user.__uri__, ALL_PERMISSIONS))

    #        # theme gallery
    #        GALLERY_ACL.allow(user.__uri__, ALL_PERMISSIONS)

    #ApplicationPolicy.__acl__ = acl

    return config.make_wsgi_app()
