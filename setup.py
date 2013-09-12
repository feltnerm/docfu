#!/usr/bin/env python
# -*- coding: utf-8 -*-
import docfu

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

settings = {}
settings.update(
    name='docfu',
    version=docfu.__version__,
    author='Mark Feltner',
    author_email='feltner.mj@gmail.com',
    license='MIT',
    url='https://github.com/feltnerm/docfu',
    packages=['docfu', ],
    description='Generate static docs from a git repo.',
    long_description=open('README').read(),
    install_requires=[
        'argparse',
        'distribute',
        'Jinja2',
        'Markdown',
        'Pygments',
        'argparse',
        'mdx_smartypants',
        'GitPython'
    ],
    classifiers=(
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ),
    entry_points={
        'console_scripts': [
            'docfu = docfu.cli:main',
        ]
    }
)

setup(**settings)
