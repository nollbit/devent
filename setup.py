#coding: UTF-8
__author__ = 'johanm'

from distutils.core import setup

setup(
    name='devent',
    version='0.0.3',
    author='Johan Mjones',
    author_email='johan.mjones@gmail.com',
    packages=['devent'],
    url='https://github.com/nollbit/devent',
    license='LICENSE',
    description='Distributed events under Gevent using Redis',
    long_description=open('README.md').read(),
    install_requires=[
        'redis>=2.6.2',
        'gevent>=0.3.16',
    ]
)