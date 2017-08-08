# -*- coding: utf-8 -*-

# This file is part of the Push Existing Vocab add-on for Anki
# Copyright: SpencerMAQ (Michael Spencer Quinto) <spencer.michael.q@gmail.com> 2017
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
from aqt.addons import AddonManager
from aqt import mw
import logging
import os
import sys
from functools import wraps
from time import time


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


addon_mgr_instance = AddonManager(mw)
ADD_ON_PATH = addon_mgr_instance.addonsFolder()
PUSH_EXISTING_PATH = ADD_ON_PATH + r'\push_existing'

if not os.path.exists(PUSH_EXISTING_PATH):
    os.makedirs(PUSH_EXISTING_PATH)
NEW_PATH = os.path.join(ADD_ON_PATH, 'push_existing')
LOG_PATH = os.path.join(NEW_PATH, 'push_existing.log')
main_logger = setup_logger('main_logger', LOG_PATH)

del addon_mgr_instance


# https://stackoverflow.com/questions/11731136/python-class-method-decorator-w-self-arguments
def calculate_time(f):
    @wraps(f)
    def wrap(self):
        before = time()
        f(self)
        after = time()
        elapsed = after - before
        main_logger.info('function "{}" took {} seconds'
                         .format(f.__name__, elapsed))
    return wrap
