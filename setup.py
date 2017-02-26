#!/usr/bin/env python

"""pydistcp: python WebHDFS inter/intra-cluster data copy tool."""

import os
import sys
import re
from setuptools import find_packages, setup

sys.path.insert(0, os.path.abspath('src'))

def _get_version():
  """Extract version from package."""
  with open('ahdp/__init__.py') as reader:
    match = re.search(
      r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
      reader.read(),
      re.MULTILINE
    )
    if match:
      return match.group(1)
    else:
      raise RuntimeError('Unable to extract version.')

def _get_long_description():
  """Get README contents."""
  with open('README.md') as reader:
    return reader.read()

setup(
  name='ahdp',
  version=_get_version(),
  description=__doc__,
  long_description=_get_long_description(),
  author='Yassine Azzouz',
  author_email='yassine.azzouz@agmail.com',
  url='https://github.com/yassineazzouz/ahdp',
  license='GPLv3',
  packages=find_packages(),
  classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
  ],
  install_requires=[
  ],
  extras_require={
    'ansible': ['ansible>=1.9.2'],
    'client': ['pywhdfs>=1.0.0','impyla>=0.12.0','sasl>=0.2.0','thrift_sasl>=0.2.0'],
  },
)
