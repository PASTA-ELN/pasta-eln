"""
Copied from https://github.com/Alir3z4/html2text
- which has a GPL-3.0 license
- simplified into four files, removed the library constraint
"""
from typing import Dict, Optional


class AnchorElement:
    __slots__ = ['attrs', 'count', 'outcount']

    def __init__(self, attrs: dict[str, Optional[str]], count: int, outcount: int):
        self.attrs = attrs
        self.count = count
        self.outcount = outcount


class ListElement:
    __slots__ = ['name', 'num']

    def __init__(self, name: str, num: int):
        self.name = name
        self.num = num
