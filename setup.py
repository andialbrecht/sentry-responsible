#!/usr/bin/env python

from setuptools import setup, find_packages


install_requires = [
    'sentry>=5.0.14,<5.4',
]


with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()


setup(
    name='sentry-responsible',
    version='0.2.0',
    author='Andi Albrecht',
    author_email='albrecht.andi@gmail.com',
    url='https://github.com/andialbrecht/sentry-responsible',
    description='A Sentry extension which allows you to assign responsibilities for sentry events.',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'sentry.apps': [
            'sentry_responsible = sentry_responsible',
            ],
        'sentry.plugins': [
            'sentry_responsible = sentry_responsible.plugin:ResponsiblePlugin'
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Software Development'
    ],
)
