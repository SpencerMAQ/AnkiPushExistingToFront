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
name_of_deck = ''
deck_id = mw.col.decks.id(name_of_deck)
deck = mw.col.decks.select(deck_id)

deck_note = deck.note()

## The name of the field where the add-on
## will search
field_to_match = ''

for (name_of_field, contents) in deck_note.items():
    if name_of_field == field_to_match:
        ## change due value to 0


