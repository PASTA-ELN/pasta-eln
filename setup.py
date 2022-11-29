#!/usr/bin/env python
from setuptools import setup
import commit


if __name__ == '__main__':
    setup(name='pasta_eln',
          version=commit.get_version()[1:]
    )
