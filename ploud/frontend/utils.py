""" utils """
import operator
import ptah
import transaction
from datetime import datetime
from ploud.utils import ploud_config, maintenance
from ploud.utils.policy import POLICIES
from ploud.utils.disable import disableVhosts, enableVhosts
from ploud.utils.vhost import addVirtualHosts, removeVirtualHosts

from ploud.frontend import models, tmpl


def disableHost(site):
    names = [str(host.host)
             for host in
                ptah.get_session().query(models.Host).filter_by(id=site.id)]
    site.disabled = True

    # we have to commit site changes because
    # next call update file on filesystem and we won't able
    # to rollback change
    #transaction.commit()
    disableVhosts(names)


def enableHost(site):
    names = [str(host.host)
             for host in
                ptah.get_session().query(models.Host).filter_by(id=site.id)]
    site.disabled = False

    # we have to commit site changes because
    # next call update file on filesystem and we won't able
    # to rollback change
    #transaction.commit()
    enableVhosts(names)


rfc822_specials = '()<>@,;:\\"[]'

def isValidMailAddress(addr):
    """Returns True if the email address is valid and False if not."""
    # First we validate the name portion (name@domain)
    c = 0
    while c < len(addr):
        if addr[c] == '@':
            break
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in rfc822_specials:
            return False
        c = c + 1

    # check whether we have any input and that the name did not end with a dot
    if not c or addr[c - 1] == '.':
        return False

    # check also starting and ending dots in (name@domain)
    if addr.startswith('.') or addr.endswith('.'):
        return False

    # Next we validate the domain portion (name@domain)
    domain = c = c + 1
    # Ensure that the domain is not empty (name@)
    if domain >= len(addr):
        return False
    count = 0
    while c < len(addr):
        # Make sure that domain does not end with a dot or has two dots in a row
        if addr[c] == '.':
            if c == domain or addr[c - 1] == '.':
                return False
            count = count + 1
        # Make sure there are only ASCII characters
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127:
            return False
        # A RFC-822 address cannot contain certain ASCII characters
        if addr[c] in rfc822_specials:
            return False
        c = c + 1
    if count >= 1:
        return True
    else:
        return False


def provision_site(user, site_type, site_name, template_id='', language='en'):
    # create site entry
    site = models.Site(user.id, site_type, site_name)
    site.last_accessed = datetime.now()
    Session = ptah.get_session()
    Session.add(site)
    Session.flush()

    # create host
    PLOUD = ptah.get_settings('ploud')

    hostname = '%s.%s'%(site_name, PLOUD['domain'])
    host = models.Host(site.id, hostname.lower())
    Session.add(host)
    addVirtualHosts((str(hostname),), 'plone41')
    POLICIES[user.type].changeHostsPolicy((hostname,), site_name)

    FE = ptah.get_settings('frontend')
    if FE['devmode']:
        transaction.commit()
        return site

    # Create the database.
    conn = ploud_config.CLIENTS_POOL.getconn()
    try:
        tmpl.create_site(conn, site.id, template_id=template_id, type=site_type)
    except NameError:
        tmpl.create_site(conn, site.id, type=site_type)
    conn.commit()
    ploud_config.CLIENTS_POOL.putconn(conn)
    transaction.commit()

    # change owner of new site
    if maintenance.maintence is not None:
        maintenance.maintence.execute(hostname, 'ploud-fix-owner,%s' % language)

    return site


def languages():
    langs = (
        {'name': 'Afrikaans',               'code': 'af',       'selected': False},
        {'name': 'Arabic',                  'code': 'ar',       'selected': False},
        {'name': 'Bulgarian',               'code': 'bg',       'selected': False},
        {'name': 'Bengali',                 'code': 'bn',       'selected': False},
        {'name': 'Catalan',                 'code': 'ca',       'selected': False},
        {'name': 'Czech',                   'code': 'cs',       'selected': False},
        {'name': 'Welsh',                   'code': 'cy',       'selected': False},
        {'name': 'Danish',                  'code': 'da',       'selected': False},
        {'name': 'German',                  'code': 'de',       'selected': False},
        {'name': 'Greek',                   'code': 'el',       'selected': False},
        {'name': 'English',                 'code': 'en',       'selected': True},
        {'name': 'Esperanto',               'code': 'eo',       'selected': False},
        {'name': 'Spanish',                 'code': 'es',       'selected': False},
        {'name': 'Estonian',                'code': 'et',       'selected': False},
        {'name': 'Basque',                  'code': 'eu',       'selected': False},
        {'name': 'Persian',                 'code': 'fa',       'selected': False},
        {'name': 'Finnish',                 'code': 'fi',       'selected': False},
        {'name': 'French',                  'code': 'fr',       'selected': False},
        {'name': 'Hebrew',                  'code': 'he',       'selected': False},
        {'name': 'Hindi',                   'code': 'hi',       'selected': False},
        {'name': 'Croatian',                'code': 'hr',       'selected': False},
        {'name': 'Hungarian',               'code': 'hu',       'selected': False},
        {'name': 'Armenian',                'code': 'hy',       'selected': False},
        {'name': 'Indonesian',              'code': 'id',       'selected': False},
        {'name': 'Italian',                 'code': 'it',       'selected': False},
        {'name': 'Japanese',                'code': 'ja',       'selected': False},
        {'name': 'Georgian',                'code': 'ka',       'selected': False},
        {'name': 'Kannada',                 'code': 'kn',       'selected': False},
        {'name': 'Korean',                  'code': 'ko',       'selected': False},
        {'name': 'Lithuanian',              'code': 'lt',       'selected': False},
        {'name': 'Maori',                   'code': 'mi',       'selected': False},
        {'name': 'Burmese',                 'code': 'my',       'selected': False},
        {'name': 'Dutch',                   'code': 'nl',       'selected': False},
        {'name': 'Norwegian Nynorsk',       'code': 'nn',       'selected': False},
        {'name': 'Norwegian',               'code': 'no',       'selected': False},
        {'name': 'Polish',                  'code': 'pl',       'selected': False},
        {'name': 'Brazilian Portuguese',    'code': 'pt-br',    'selected': False},
        {'name': 'Portuguese',              'code': 'pt',       'selected': False},
        {'name': 'Rhaeto-Romance',          'code': 'rm',       'selected': False},
        {'name': 'Romanian',                'code': 'ro',       'selected': False},
        {'name': 'Russian',                 'code': 'ru',       'selected': False},
        {'name': 'Slovak',                  'code': 'sk',       'selected': False},
        {'name': 'Slovenian',               'code': 'sl',       'selected': False},
        {'name': 'Samoan',                  'code': 'sm',       'selected': False},
        {'name': 'Albanian',                'code': 'sq',       'selected': False},
        {'name': 'Serbian in Latin script', 'code': 'sr-Latn',  'selected': False},
        {'name': 'Serbian',                 'code': 'sr',       'selected': False},
        {'name': 'Swedish',                 'code': 'sv',       'selected': False},
        {'name': 'Tamil',                   'code': 'ta',       'selected': False},
        {'name': 'Telugu',                  'code': 'te',       'selected': False},
        {'name': 'Tongan',                  'code': 'to',       'selected': False},
        {'name': 'Turkish',                 'code': 'tr',       'selected': False},
        {'name': 'Ukrainian',               'code': 'uk',       'selected': False},
        {'name': 'Vietnamese',              'code': 'vi',       'selected': False},
        {'name': 'Chinese (China)',         'code': 'zh-cn',    'selected': False},
        {'name': 'Chinese (Hongkong)',      'code': 'zh-hk',    'selected': False},
        {'name': 'Chinese',                 'code': 'zh',       'selected': False},
        {'name': 'Chinese (Taiwan)',        'code': 'zh-tw',    'selected': False},
    )
    langs = sorted(langs, key=operator.itemgetter('name'))
    return langs
