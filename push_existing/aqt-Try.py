# -*- coding: utf-8 -*-

"""
This file is part of the Push Existing Vocab add-on for Anki
Copyright: SpencerMAQ (Michael Spencer Quinto) <spencer.michael.q@gmail.com> 2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

from aqt.qt import *    # imports the same modules as QtCore, QtGui
from aqt import mw
from anki.hooks import addHook
from aqt.utils import showInfo
import csv
import os

__version__ = '1.0.0'
# July 3 2017

## NOTE: YOU MUST RESET THE SCHEDULER AFTER ANY DB CHANGES
## BY DOING mw.reset()

HOTKEY = "Shift+P"


# deck_id = mw.col.decks.id(name_of_deck)
# deck = mw.col.decks.select(deck_id)
#
# deck_note = deck.note()

#################________FIELDS___________###################


## The name of the field where the add-on
## will search
field_to_match = ''     # e.g. expression
## Select the deck you'd want to change
name_of_deck = ''

#############################################################

####_________________TO_DO_LIST_________#####################
####
# Include total count of vocab pasted
# total count of cards brought to front
# display number of cards that failed to be brought to front
# maybe this'd work better if you did by note type instead of deck? (or maybe both)
# display the vocabs that were found (and total number)
# display the vocabs that were NOT found (and total number)
# add functionality to tag the cards that were moved by adding tag: movedByPushToFrontPlugin


# include functionaly for user to push only CERTAIN CARDS, not entire notes

#############################################################


class TextEditor(QDialog):
    def __init__(self, mw):

        # QDialog args from http://pyqt.sourceforge.net/Docs/PyQt4/qdialog.html#QDialog
        # __init__ (self, QWidget parent = None, Qt.WindowFlags flags = 0)
        super(TextEditor, self).__init__(mw)

        if mw:
            self.run_action = QAction("Push Existing Vocab", mw)
            self.run_action.setShortcut(QKeySequence(HOTKEY))

            self.run_action.triggered.connect(lambda: self.init_ui(mw))

            mw.form.menuTools.addAction(self.run_action)

        self.list_of_vocabs = []

        self.vocabulary_text = QTextEdit(mw)    # QTextEdit 1st arg = parent

        self.clr_btn = QPushButton('Clear') # works
        self.resched_btn = QPushButton('Reschedule')
        self.write_to_list_btn = QPushButton('Write to List')
        self.write_to_txt_btn = QPushButton('Write to CSV')

        self.write_to_list_btn.clicked.connect(self.write_to_list)
        self.resched_btn.clicked.connect(self.reschedule_cards)
        self.clr_btn.clicked.connect(self.clear_text)
        self.write_to_txt_btn.clicked.connect(self.csv_write)

        # temp button
        self.show_contents = QPushButton('Show Contents')


    def init_ui(self, mw):
        # showInfo(str(self))

        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        # buttons lined horizontally
        # to be added later to v_layout
        h_layout.addWidget(self.clr_btn)
        h_layout.addWidget(self.resched_btn)
        h_layout.addWidget(self.show_contents)
        h_layout.addWidget(self.write_to_list_btn)

        v_layout.addWidget(self.vocabulary_text)

        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

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

    def csv_write(self):
        filename = QFileDialog.getSaveFileName(self,
                                               'Save CSV', os.getenv('HOME'), 'CSV(*.csv')

        if filename[0] != '':   # what does this do again?
            with open(filename[0], 'w') as file:
                for line in self.vocabulary_text.toPlainText():
                    file.writelines(line)


    def write_to_list(self):
        for line in self.vocabulary_text.toPlainText():
            self.list_of_vocabs.append(line)

    def show_contents_signal(self):
        showInfo(str(self.list_of_vocabs))

    # works
    def clear_text(self):
        self.vocabulary_text.clear()

    def reschedule_cards(self):
        pass


mw.texteditor = TextEditor(mw)

## I might need to use SQLITE for changing the due value of the said cards
## and unsuspend them simultaneously