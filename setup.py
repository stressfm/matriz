#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matriz
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

with open(path.join(here, 'HISTORY.rst'), encoding='utf8') as f:
    history = f.read().replace('.. :changelog:', '')

with open(path.join(here, 'LICENSE'), encoding='utf8') as f:
    licence = f.read()


test_requirements = [
    'coverage',
    'bumpversion',
    'twine',
]


setup(
    name='matriz',
    version=matriz.__version__,
    description='Networked Music Performance software',
    long_description=readme + '\n\n'+ history,
    author=matriz.__author__,
    author_email=matriz.__author_email__,
    url=matriz.__url__,
    license=license,
    packages=find_packages(exclude=('tests*', 'docs')),
    extras_require={
        'server': [
            'Flask',
            'Flask-uWSGI-WebSocket',
            'gevent',
            'greenlet',
            'itsdangerous',
            'Jinja2',
            'MarkupSafe',
            'uWSGI',
            'Werkzeug',
            ],
    },
    entry_points={
        'console_scripts': [
            'matriz = matriz.client:main',
        ]
    },
    include_package_data=True,
    install_requires=[
        'argparse==1.2.1',
        'decorator==3.4.0',
        'wheel==0.24.0',
        'backports.ssl-match-hostname==3.5.0.1',
        'six==1.10.0',
        'websocket-client==0.35.0',
        'wheel==0.24.0',
        'JACK-Client==0.4.0',
        'miniupnpc==1.9',
    ],
    zip_safe=False,
    keywords='matriz, networked music performance',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Artistic Software',
        'Topic :: Education',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
