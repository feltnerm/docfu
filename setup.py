#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

settings = {}
settings.update(
    name="docfu",
    version='0.0.5',
    author='Mark Feltner',
    author_email='feltner.mj@gmail.com',
    license="MIT",
    url="https://github.com/feltnerm/docfu",
    packages=['docfu',],
    description="Generate static docs from a git repo.",
    long_description=open('README').read(),
    install_requires=[
        "Jinja2>=2.7",
        "distribute>=0.6.46",
        "Markdown>=2.3.1",
        "Pygments>=1.6",
        "argparse>=1.2.1",
        "mdx-smartypants>=1.3",
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
