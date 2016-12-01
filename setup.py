#!/usr/bin/env python
import re
import os

from setuptools import setup


with open("README.rst") as fp:
    long_desc = fp.read()

with open("vismalib/__init__.py") as fp:
    version = re.search('__version__\s+=\s+"([^"]+)', fp.read()).group(1)

if __name__ == "__main__":
    setup(
        name="vismalib",
        version=version,
        description="A pythonic interface to Visma's eAccounting API",
        long_description=long_desc,
        license="MIT",
        author="Andreas Runfalk",
        author_email="andreas@runfalk.se",
        url="https://www.github.com/runfalk/vismalib",
        packages=["vismalib"],
        install_requires=[
            "requests>=2.4.2",
            "requests_oauthlib"
        ],
        classifiers=(
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Topic :: Utilities",
        )
    )
