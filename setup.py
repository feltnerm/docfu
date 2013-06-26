#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

settings = {}
settings.update(
    name="docfu",
    version='0.3',
    author='Mark Feltner',
    author_email='feltner.mj@gmail.com',
    license="MIT",
    url="https://github.com/feltnerm/docfu",
    packages=['docfu',],
    data_files=[
        'README.rst',
    ],
    description="Generate static docs from a git repo.",
    long_description=open('README.rst').read(),
    install_requires=[
        "Jinja2>=2.7",
        "Pygments>=1.6",
        "argparse>=1.2.1",
        "markdown2>=2.1.0",
        "smartypants>=1.6.0.3"        
    ],
    classifiers=(
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.1',
        #'Programming Language :: Python :: 3.2', 
    ),
    entry_points={
        'console_scripts': [
            'docfu = docfu.cli:main',
        ],     
    }
)

setup(**settings)
