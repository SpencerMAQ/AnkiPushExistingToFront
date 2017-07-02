# -*- coding: utf-8 -*-

"""
This file is part of the Push Existing Vocab add-on for Anki
Copyright: SpencerMAQ 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from aqt.qt import *

from aqt import mw

## NOTE: YOU MUST RESET THE SCHEDULER AFTER ANY DB CHANGES
## BY DOING mw.reset()

## Select the deck you'd want to change
deck_to_change = ''
deck_id = mw.col.decks.id(deck_to_change)
mw.col.decks.select(deck_id)

## The name of the field where the add-on
## will search
field_to_match = ''



