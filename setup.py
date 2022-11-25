#!/usr/bin/env python

import sys
from setuptools import setup
import versioneer

from _pasta_eln_buildsupport.setup import (
    BuildManPage,
)

cmdclass = versioneer.get_cmdclass()
cmdclass.update(build_manpage=BuildManPage)

if __name__ == '__main__':
    setup(name='pasta_eln',
          version=versioneer.get_version(),
          cmdclass=cmdclass,
    )
