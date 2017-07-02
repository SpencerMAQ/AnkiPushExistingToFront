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
# from PyQt4 import QtCore, QtGui
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

class TextEditor(QDialog):
    def __init__(self, mw):
        super(TextEditor, self).__init__()

        if mw:
            self.run_action = QAction("Push Existing Vocab", mw)
            self.run_action.setShortcut(QKeySequence(HOTKEY))

            self.run_action.triggered.connect(lambda: self.init_ui(mw))

            mw.form.menuTools.addAction(self.run_action)

        self.list_of_vocabs = []

        self.clr_btn = QPushButton('Clear')
        self.resched_btn = QPushButton('Reschedule')

        self.resched_btn.clicked.connect(self.reschedule_cards)
        self.clr_btn.clicked.connect(self.clear_text)

        # temp button
        self.show_contents = QPushButton('Show Contents')


    def init_ui(self, mw):
        # showInfo('the fuck')

        # QTextEdit 1st arg = parent
        self.vocabulary_text = QTextEdit(mw)


        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        # buttons lined horizontally
        # to be added later to v_layout
        h_layout.addWidget(self.clr_btn)
        h_layout.addWidget(self.resched_btn)
        h_layout.addWidget(self.show_contents)

        v_layout.addWidget(self.vocabulary_text)

        v_layout.addLayout(h_layout)

        # signals
        self.vocabulary_text.textChanged.connect(self.value_changed)
        self.show_contents.clicked.connect(self.show_contents_signal)

        self.show()

    def value_changed(self):
        self.vocabulary_text.setText(str(self.vocabulary_text.toPlainText()))
        # list_of_vocabs = mw.text.text()

        self.list_of_vocabs = []    # empty it before filling it again

        for line in self.vocabulary_text.toPlainText():
            self.list_of_vocabs.append(line)

    def show_contents_signal(self):
        showInfo(str(self.list_of_vocabs))

    def clear_text(self):
        self.vocabulary_text.clear()

    def reschedule_cards(self):
        pass


mw.texteditor = TextEditor(mw)

## I might need to use SQLITE for changing the due value of the said cards
## and unsuspend them simultaneously
