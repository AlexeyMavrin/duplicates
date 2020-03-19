#!/usr/bin/env python
# encoding: utf-8

import setuptools
from setuptools.command.test import test


class TestCommand(test, object):

    def run(self):
        # run the unit test to make sure that there is no regression
        import test_all
        test_all.main()


setuptools.setup(
    cmdclass={'test': TestCommand},
    name='duplicates',
    version='2.0',
    description='Duplicates search and removal. The wrapper over duplicate-file-finder. Converted for Python3.',
    author='Alexey Mavrin',
    author_email='alexeymavrin@gmail.com',
    platforms=['mac', 'linux', 'windows'],
    packages=setuptools.find_packages(exclude=["*.tests"]),  # automatically add packages (except tests)
    package_dir={'duplicates': 'duplicates'},  # where the package in source tree
    include_package_data=False,  # check MANIFEST.in for explicit rules
    install_requires=['humanize', ],
    license='MIT License',
    entry_points={
        'console_scripts': [
            'duplicates = duplicates.duplicates:main',
        ]
    }
)
