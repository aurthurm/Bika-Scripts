#!/usr/bin/env python

from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session='hack')
reqs = [str(ir.req) for ir in install_reqs]

setup(name='bikafiler',
      version='2.1.0',
      author='Aurthur Musendame',
      author_email='aurthurmusendame@gmail.com',
      packages=['bikafiler'],
      install_requires=reqs,
      entry_points={
          'console_scripts': [
              'bikafiler = bikafiler.__main__:main'
          ]
      })
      