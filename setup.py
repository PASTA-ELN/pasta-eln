#!/usr/bin/env python
from __future__ import annotations

from setuptools import setup

import releaseVersion

if __name__ == '__main__':
    setup(name='pasta_eln', version=releaseVersion.getVersion()[1:])
