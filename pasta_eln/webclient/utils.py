""" Common utility functions """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: utils.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.

from asyncio import CancelledError, IncompleteReadError, InvalidStateError, LimitOverrunError, \
  TimeoutError as AsyncTimeoutError
from functools import wraps
from json import JSONDecodeError
from typing import Any, Callable
from xml.etree.ElementTree import ParseError

from aiohttp import ClientConnectorError, InvalidURL
from requests.exceptions import ConnectionError as RequestsConnectionError, InvalidSchema, MissingSchema


def handle_dataverse_exception_async(wrapped: Callable[..., Any]) -> Callable[..., Any]:
  """
  Handle exceptions from dataverse client methods.
  Args:
    wrapped (Callable): The wrapped function where the exceptions can be raised.

  Returns:
    The wrapper function which handles the exceptions.
  """

  @wraps(wrapped)
  async def wrapper(self: Any, *args: object, **kwargs: object) -> Any:
    try:
      return await wrapped(self, *args, **kwargs)
    except (
        RequestsConnectionError, InvalidURL, MissingSchema, InvalidSchema, TypeError, FileNotFoundError, AttributeError,
        ParseError) as e:
      self.logger.error(e)
      return False, str(e)

  return wrapper


def handle_http_client_exception(wrapped: Callable[..., Any]) -> Callable[..., Any]:
  """
  Handle exceptions from http client methods.
  Args:
    wrapped (Callable): The wrapped function where the exceptions can be raised.

  Returns:
    The wrapper function which handles the exceptions.
  """

  @wraps(wrapped)
  async def wrapper(self: Any, *args: object, **kwargs: object) -> Any:
    try:
      return await wrapped(self, *args, **kwargs)
    except AsyncTimeoutError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session request timeout for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except CancelledError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session request cancelled for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except InvalidStateError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session request in invalid state for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except IncompleteReadError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session request incomplete read for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except LimitOverrunError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session request limit overrun for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except TypeError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session type error for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except ClientConnectorError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"ClientConnectorError for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except InvalidURL as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session InvalidURL for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except JSONDecodeError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session JSONDecodeError for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except AssertionError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session AssertionError for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except ValueError as e:
      url = kwargs['base_url'] if 'base_url' in kwargs else args[0]
      error = f"Client session ValueError for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}

  return wrapper
