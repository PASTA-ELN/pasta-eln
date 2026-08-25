"""
Copied from https://github.com/Alir3z4/html2text
- which has a GPL-3.0 license
- simplified into four files, removed the library constraint
- This externally sourced file is not and will not be modified as part of this work.
"""
from typing import Dict, Optional


class AnchorElement:
    __slots__ = ['attrs', 'count', 'outcount']

    def __init__(self, attrs: dict[str, str | None], count: int, outcount: int):
        self.attrs = attrs
        self.count = count
        self.outcount = outcount


class ListElement:
    __slots__ = ['name', 'num']

    def __init__(self, name: str, num: int):
        self.name = name
        self.num = num
