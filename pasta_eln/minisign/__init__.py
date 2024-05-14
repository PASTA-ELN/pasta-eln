"""
Minisign
from https://github.com/x13a/py-minisign
"""

__version__ = '0.10'

from .exceptions import (
    Error,
    ParseError,
    VerifyError,
)
from .minisign import (
    KeyPair,
    PublicKey,
    SecretKey,
    Signature,
)
