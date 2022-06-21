#!/usr/bin/python3

import setuptools

install_requires = []

setuptools.setup(
    name = "MetroBuild",
    version = "v2022.06.1",
    packages = setuptools.find_packages(),
    install_requires = install_requires,
    entry_points = {
        'console_scripts': [
            'metro = buildtool:main'
        ]
    },
    include_package_data = True
    )
