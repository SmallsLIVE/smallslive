#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='smallslive',
    version='0.0.1',
    description=('Sample application for a music club'),
    author='Filip Jukic',
    author_email='filip@appsembler.com',
    url='https://github.com/SmallsLIVE/smallslive/',
    packages=find_packages(),
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