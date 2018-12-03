from __future__ import absolute_import, unicode_literals

import time
import random

from .exceptions import LockError


def retry_on_lock_error(retries):
    def decorator(function):
        def wrapper():
            retry_count = 0

            while True:
                try:
                    return function()
                except LockError:
                    if retry_count == retries:
                        raise
                    else:
                        retry_count = retry_count + 1
                        timeout = 2 ** retry_count
                        time.sleep(timeout)
                        # Add random jitter
                        time.sleep(random.uniform(0.0, 1.0))
        return wrapper
    return decorator
