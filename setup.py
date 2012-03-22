import os
from setuptools import setup, find_packages

requires = [
    'setuptools',
    'ptah',
    'pyramid',
    'pyramid_beaker',
    'pyramid_mailer',
    'psycopg2',
    'simplejson',

    'ploud.utils',
    ]


setup(name='ploud.frontend',
      version='0.0',
      description='ploud frontend',
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg',
      packages=find_packages(),
      namespace_packages=['ploud'],
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      entry_points = {
        'paste.app_factory': [
            'main = ploud.frontend.app:main'],
        }
      )
