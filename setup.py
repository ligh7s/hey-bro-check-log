#!/usr/bin/env python3
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


with open('README.md') as desc:
    long_description = desc.read()


setup(
    name='heybrochecklog',
    version='1.2.3',
    description='A python tool for evaluating and working with EAC/XLD CD rip logs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPLv3',
    author='lights',
    author_email='lights@tutanota.de',
    url='https://github.com/ligh7s/hey-bro-check-log',
    keywords='logchecker eac xld cd rips',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
    ],
    packages=[
        'heybrochecklog',
        'heybrochecklog.resources',
        'heybrochecklog.resources.eac',
        'heybrochecklog.resources.eac95',
        'heybrochecklog.markup',
        'heybrochecklog.score',
        'heybrochecklog.score.modules',
    ],
    include_package_data=True,
    python_requires='>=3.5',
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    install_requires=[
        'chardet'
    ],
    entry_points={
        'console_scripts': [
            'heybrochecklog=heybrochecklog:runner',
        ],
    },
)
