#!/usr/bin/env python

import sys
from setuptools import setup
import commit


if __name__ == '__main__':
    setup(name='pasta_eln',
          version=commit.get_version()
    )
