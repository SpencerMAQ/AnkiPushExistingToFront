# -*- coding: utf-8 -*-

# This file is part of the Push Existing Vocab add-on for Anki
# Copyright: SpencerMAQ (Michael Spencer Quinto) <spencer.michael.q@gmail.com> 2017
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
import logging
from functools import wraps
from time import time

from .main import main_logger


FORMAT = logging.Formatter('%(levelname)s \t| %(asctime)s: \t%(message)s')


def setup_logger(name, log_file, _format=FORMAT, level=logging.DEBUG):
    """Create two or more loggers because writing to a CSV
    Causes the Characters to become messed up even with the
    correct encoding

    Note that the log files are always in UTF-8, never
    set by the user, i.e. even if the files read are in shift JIS
    the log files are still in UTF-8

    Args:
        name:           Name of the logger
        log_file:       Path to the log file
        _format:        String format
        level:          DEBUG by default
    """
    handler = logging.FileHandler(log_file)
    handler.setFormatter(_format)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


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
