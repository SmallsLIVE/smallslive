#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='music_club',
    version='0.0.1',
    description=('Sample application for a music club'),
    author='Filip Jukic',
    author_email='filip@appsembler.com',
    url='https://github.com/SmallsLIVE/smallslive/',
    packages=[
        'smallslive',
    ],
    package_dir={'smallslive': 'smallslive'},
    include_package_data=True,
    install_requires=open('requirements.txt').read().splitlines(),
    license='BSD',
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)