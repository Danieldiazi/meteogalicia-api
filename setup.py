
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import os
import sys
from setuptools import setup, find_packages

# Package meta-data.
NAME = "MeteoGalicia-API"
DESCRIPTION = (
    "Python library for get info from MeteoGalicia web service. MeteoGalicia is the meteorological agency for Galicia, Spain"
)
URL = "https://github.com/danieldiazi/meteogalicia-api"
EMAIL = "dandiazde@gmail.com"
AUTHOR = "danieldiazi"
VERSION = "0.0.6"

here = lambda *a: os.path.join(os.path.dirname(__file__), *a)
requirements = [x.strip() for x in open(here('requirements.txt')).readlines()]


here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=long_description,
      long_description_content_type="text/markdown",
      keywords='MeteoGalicia',
      author=AUTHOR,
      author_email=EMAIL,
      url=URL,
      install_requires=requirements,
      license="GPLv3",
      zip_safe=False,
      platforms=["any"],
      packages=find_packages(),
      classifiers=[
        
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
      ],
)