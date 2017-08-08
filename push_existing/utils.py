# -*- coding: utf-8 -*-

# This file is part of the Push Existing Vocab add-on for Anki
# Copyright: SpencerMAQ (Michael Spencer Quinto) <spencer.michael.q@gmail.com> 2017
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

from functools import wraps
from time import time

from .main import main_logger


def calculate_time(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        before = time()
        f(*args, **kwargs)
        after = time()
        elapsed = after - before
        main_logger.info('function "{}" took {} seconds'
                         .format(f.__name__, elapsed))
    return wrap
