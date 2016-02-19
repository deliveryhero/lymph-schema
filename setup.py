# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as f:
    description = f.read()


setup(
    name='lymph-schema',
    version='0.4.0-dev',
    url='http://github.com/deliveryhero/lymph-schema/',
    packages=find_packages(),
    namespace_packages=['lymph'],
    author=u'© Delivery Hero Holding GmbH',
    license=u'Apache License (2.0)',
    maintainer=u'Mouad Benchchaoui',
    maintainer_email=u'mouad.benchchaoui@deliveryhero.com',
    long_description=description,
    include_package_data=True,
    install_requires=[
        'lymph>=0.14.0',
        'marshmallow>=2.4.2',
        'typing>=3.5',
        'fake-factory>=0.5.1',
    ],
    entry_points={
        'lymph.cli': [
            'gen-schema = lymph.schema.cli.generator:SchemaGenerator',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ]
)
