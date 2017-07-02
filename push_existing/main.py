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
# from PyQt5 import QtWidgets, QtGui
from PyQt4 import QtCore, QtGui
# from pprint import pprint

__version__ = '1.0.0'

## NOTE: YOU MUST RESET THE SCHEDULER AFTER ANY DB CHANGES
## BY DOING mw.reset()

HOTKEY = "Ctrl+Shift+P"

## Select the deck you'd want to change
name_of_deck = ''
# deck_id = mw.col.decks.id(name_of_deck)
# deck = mw.col.decks.select(deck_id)
#
# deck_note = deck.note()

## The name of the field where the add-on
## will search
field_to_match = ''

# list_of_vocabs = []  # create an empty set, note: {} is an empty dictionary, set() = empty set


class TextEditor(QtGui.QLineEdit):
    def __init__(self):
        super(TextEditor, self).__init__(mw)    # I have no idea why I put mw there

        self.vocabulary_text = QtGui.QTextEdit(self)
        self.clr_btn = QtGui.QPushButton('Clear')
        self.resched_btn = QtGui.QPushButton('Reschedule')

        # temp button
        self.show_contents = QtGui.QPushButton('Show Contents')

        self.list_of_vocabs = []

        self.init_ui()

    def init_ui(self):
        v_layout = QtGui.QVBoxLayout()
        h_layout = QtGui.QHBoxLayout()

        # buttons lined horizontally
        # to be added later to v_layout
        h_layout.addWidget(self.clr_btn)
        h_layout.addWidget(self.resched_btn)
        h_layout.addWidget(self.show_contents)

        v_layout.addWidget(self.vocabulary_text)

        v_layout.addLayout(h_layout)

        self.vocabulary_text.textChanged.connect(self.value_changed)
        self.show_contents.clicked.connect()

    def value_changed(self):
        self.vocabulary_text.setText(str(self.vocabulary_text.text()))
        # list_of_vocabs = mw.text.text()

        self.list_of_vocabs = []    # empty it before filling it again

        for line in self.vocabulary_text.text():
            self.list_of_vocabs.append(line)

    def show_contents(self):
        showInfo(str(self.list_of_vocabs))


def enter_vocab():
    # showInfo("hahahaha")
    mw.text = QtGui.QLineEdit()
    mw.text.textChanged.connect(value_changed)
    mw.text.show()
    # list_of_vocabs = mw.text.text()

# def value_changed():
#     mw.text.setText(str(mw.text.text()))
#     # list_of_vocabs = mw.text.text()
#
#     for line in mw.text.text():
#         list_of_vocabs.append(line)

# def show_contents():
#     showInfo(str(list_of_vocabs))


# for (name_of_field, contents) in deck_note.items():
#     if name_of_field == field_to_match:
#         ## change due value to 0
#         pass

## I might need to use SQLITE for changing the due value of the said cards
## and unsuspend them simultaneously

run_action = QAction("Push Existing Vocab", mw)
run_action.setShortcut(QKeySequence(HOTKEY))
mw.form.menuTools.addAction(run_action)

run_action.triggered.connect(enter_vocab)

show_action = QAction('Show Contents', mw)
mw.form.menuTools.addAction(show_action)

show_action.triggered.connect(show_contents)