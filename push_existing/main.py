# -*- coding: utf-8 -*-

"""
This file is part of the Push Existing Vocab add-on for Anki
Copyright: SpencerMAQ 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from aqt.qt import *
from aqt import mw
from anki.hooks import addHook
from aqt.utils import showInfo

__version__ = '1.0.0'

## NOTE: YOU MUST RESET THE SCHEDULER AFTER ANY DB CHANGES
## BY DOING mw.reset()

HOTKEY = "Ctrl+Shift+P"

## Select the deck you'd want to change
name_of_deck = ''
deck_id = mw.col.decks.id(name_of_deck)
deck = mw.col.decks.select(deck_id)

deck_note = deck.note()

## The name of the field where the add-on
## will search
field_to_match = ''

list_of_vocabs = []  # create an empty set, note: {} is an empty dictionary, set() = empty set


def enter_vocab():
    showInfo("hahahaha")


for (name_of_field, contents) in deck_note.items():
    if name_of_field == field_to_match:
        ## change due value to 0
        pass

## I might need to use SQLITE for changing the due value of the said cards
## and unsuspend them simultaneously

run_action = QAction("Push Existing Vocab", mw)
run_action.setShortcut(QKeySequence(HOTKEY))
mw.form.menuTools.addAction(run_action)

run_action.triggered.connect(enter_vocab)