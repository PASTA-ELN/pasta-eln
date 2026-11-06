#!/usr/bin/env python
""" setup to generate version number"""
from __future__ import annotations

from email.parser import Parser
from pathlib import Path

from setuptools import setup


def version() -> str:
  """Version from PKG-INFO inside an sdist, otherwise from the git tags"""
  pkgInfo = Path(__file__).parent/'PKG-INFO'
  if pkgInfo.exists():
    return Parser().parsestr(pkgInfo.read_text(encoding='utf-8'))['Version']
  import releaseVersion
  return releaseVersion.getVersion()[1:]


if __name__ == '__main__':
  setup(name='pasta_eln', version=version())
