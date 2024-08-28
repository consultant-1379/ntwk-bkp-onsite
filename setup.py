#!/usr/bin/env python

##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

import io
import os
import sys

from setuptools import find_packages, setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))  # noqa

import network_backup_onsite

PLATFORM_NAME = str(sys.platform).lower()

tests_require = ["pytest", "mock"]

# when distributing to linux
requires = ["enum34", "psutil", "requests==2.20.0", "pexpect"]

# when distributing to solaris
# requires = ["enum34", "psutil", "requests==2.20.0"]

with io.open('README.md', 'r+', encoding="utf-8") as readme:
    long_description = readme.read()


# classifiers: https://pypi.org/pypi?%3Aaction=list_classifiers
def main():
    setup(
        name="enmaas-ntwk-bkp-onsite",
        description="A backup & restore application for ENMaaS",
        long_description=long_description,
        version=network_backup_onsite.__version__,
        license="Proprietary",
        platforms=["unix", "linux", "osx", "cygwin", "win32"],
        author="NEMESIS",
        author_email="nemesis@ericsson.com",
        url="https://gerrit.ericsson.se/#/admin/projects/ENMaaS/ntwk-bkp-onsite",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        package_data={"network_backup_onsite": ["config/config.cfg"]},
        python_requires=">=2.7",
        entry_points={"console_scripts": ["ntwk_bkp_onsite = network_backup_onsite.cli:main"]},
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: Other/Proprietary License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: System :: Archiving :: Backup",
        ],
        install_requires=requires,
        setup_requires=["pytest-runner"],
        tests_require=tests_require,
        zip_safe=False
    )


if __name__ == "__main__":
    main()
