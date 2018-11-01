import logging
import sys


_error_logger = logging.getLogger('<app_error>')
_error_logger.setLevel(logging.WARNING)
_error_logger.addHandler(logging.StreamHandler(sys.stderr))

exception = _error_logger.exception
error = _error_logger.error
warn = _error_logger.warning

_debug_logger = logging.getLogger('<app_debug>')
_debug_logger.setLevel(logging.DEBUG)
_debug_logger.addHandler(logging.StreamHandler(sys.stdout))

debug = _debug_logger.debug
info = _debug_logger.info
log = _debug_logger.log
