# -*- coding: utf-8 -*-
from os import path
from codecs import open
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

with open(path.join(here, 'HISTORY.rst'), encoding='utf8') as f:
    history = f.read().replace('.. :changelog:', '')

with open(path.join(here, 'LICENSE'), encoding='utf8') as f:
    licence = f.read()


setup(
    name='matriz',
    version='0.1.0',
    description='Networked Music performance software',
    long_description=readme,
    author='Cláudio Rego, Hugo Martiniano, Vasco Pita',
    author_email='claudiojmrego@gmail.com, hugomartiniano@gmail.com, vasco.pitaf@gmail.com',
    url='https://github.com/stressfm/matriz',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    extras_require = {
        'server':  ["ReportLab>=1.2", "RXP"],
    }
)

