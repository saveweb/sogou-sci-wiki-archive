import logging
import requests
import time
import re
import sys
import functools

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 32

sess = requests.Session()

def _assert(expr, msg=''):
    if not expr:
        raise AssertionError(msg)


def retry(try_count=3, retry_interval=2, retry_interval_step=3):
    def _retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _retry_interval = retry_interval

            for i in range(try_count):
                try:
                    _result = func(*args, **kwargs)
                    if i > 0:
                        logger.warning('(Try %d/%d) %r success', i + 1, try_count, func.__name__)

                    return _result
                except Exception as e:
                    if i < try_count - 1:
                        logger.warning('(Try %d/%d) %r got exception %r: %r', i + 1, try_count, func.__name__, type(e), e)

                        if _retry_interval < 0:
                            _retry_interval = 0

                        logger.warning('Wait %.2f s to retry', _retry_interval)
                        time.sleep(_retry_interval)
                        _retry_interval += retry_interval_step

                        logger.warning('(Try %d/%d) retrying ...', i + 2, try_count)
                    else:
                        raise e

        return wrapper

    return _retry


@retry(try_count=10, retry_interval=1, retry_interval_step=5)
def http_get_request(*args, **kwargs):
    # default kwargs
    kwargs_real = {
        'timeout': DEFAULT_TIMEOUT,
    }
    kwargs_real.update(kwargs)

    logger.debug('http_get_request: args=%r, kwargs=%r, cookies=%r', args, kwargs_real, sess.cookies)
    r = sess.get(*args, **kwargs_real)

    return r
