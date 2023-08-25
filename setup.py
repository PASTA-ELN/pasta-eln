#!/usr/bin/env python
from setuptools import setup
import releaseVersion

if __name__ == '__main__':
    setup(name='pasta_eln',
          version=releaseVersion.get_version()[1:]
    )
