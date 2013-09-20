#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

from mongorm import VERSION


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = '.'.join(map(str, VERSION))

if __name__ == '__main__':
    setup(
        name='mongorm',
        version=version,
        author='Rahul AG',
        author_email='r@hul.ag',
        description=('An extremely thin ORM-ish wrapper over pymongo.'),
        long_description=read('README.rst'),
        license = 'BSD',
        keywords = 'mongodb orm',
        url = 'https://github.com/rahulg/mongorm',
        packages=['mongorm', 'tests'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Topic :: Database :: Front-Ends',
            'License :: OSI Approved :: BSD License',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent'
        ],
        test_suite='tests',
        install_requires=[
            'pymongo',
            'inflection'
        ],
    )
