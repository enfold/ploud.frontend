""" config """
import string
import logging
from datetime import timedelta

import ptah
from ptah import config

log = logging.getLogger('ploud.frontend')

LAYER='frontend'

PRICES = {
    1: 20,
    2: 60
}

LOGIN_TOKEN_TYPE = ptah.token.TokenType(
    '27b6b7a9-911e-47ab-af8c-e06994d243b8', timedelta(minutes=10),
    title = 'Ploud login service')

MNGLOGIN_TOKEN_TYPE = ptah.token.TokenType(
    '30bbfc0e6a7f48b48575c163cd7d548f', timedelta(minutes=10),
    title = 'Ploud manager login service')

PASSWORD_RESET_TOKEN_TYPE = ptah.token.TokenType(
    '1bd5aeee19374a13b07b8d2db454a5b1', timedelta(minutes=10),
    title = 'Password reset token')


ALLOWED_SITE_NAME_CHARS = ''.join((
    string.lowercase,
    string.digits,
    '-',
    '_',
))

CHOICES = (
    ('plone41', 'Plone 4.1'),
)

ptah.register_settings(
    'frontend',

    ptah.form.TextField(
        'host',
        title = 'Host',
        description = 'Ploud frontend host.',
        default = 'http://ploud.com'),

    ptah.form.TextField(
        'email_from',
        title = 'From email',
        default = 'Ploud.com <no-reply@ploud.com>'),

    ptah.form.LinesField(
        'reserved_sitenames',
        title = 'Reserved site names',
        default = ('demo', 'desktop', 'enfold','static',
                   'ww','www', 'wwww', 'support', 'login', 'rest',)),

    ptah.form.BoolField(
        'validation',
        title = 'Validation',
        description = 'Ploud user validation.',
        default = True),

    ptah.form.BoolField(
        'devmode',
        title = 'Development mode',
        default = False),

    title = 'Ploud frontend configuration',
    ttw = True,
)
