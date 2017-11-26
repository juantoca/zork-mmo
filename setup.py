#!/usr/bin/env python

from setuptools import setup, find_packages


setup(name='Conversational-Server',
      version='1.0',
      description='Text-based conversational server',
      author='Juan Toca',
      author_email='elan17.programacion@gmail.com',
      packages=find_packages(),
      provides=["Server"],
      install_requires=["Crypt-Connection", "peewee", "pycryptodome", "pyTelegramBotAPI"],
      dependency_links=['https://github.com/elan17/Crypt-Connection/tarball/master/#egg=Crypt-Connection']
      )
