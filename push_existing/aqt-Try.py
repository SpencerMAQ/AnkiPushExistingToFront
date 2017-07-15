# -*- coding: utf-8 -*-

# This file is part of the Push Existing Vocab add-on for Anki
# Copyright: SpencerMAQ (Michael Spencer Quinto) <spencer.michael.q@gmail.com> 2017
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

from aqt.qt import *
from aqt import mw
from anki.hooks import addHook
from aqt.utils import showInfo      # TODO: temporary import
import csv
import os

from PyQt5.QtWidgets import *       # TODO: temporary import
from PyQt5.QtGui import *           # TODO: temporary import

__version__ = '1.0.0'
# July 15 2017

# ## NOTE: YOU MUST RESET THE SCHEDULER AFTER ANY DB CHANGES
# ## BY DOING mw.reset()

HOTKEY = "Shift+P"

# deck_id = mw.col.decks.id(name_of_deck)
# deck = mw.col.decks.select(deck_id)
#
# deck_note = deck.note()

# ===================== FIELDS =====================

# ## The name of the field where the add-on
# ## will search
field_to_match = ''     # e.g. expression
# ## Select the deck you'd want to change
name_of_deck = ''

#############################################################

#  ===================== TO_DO_LIST =====================

# TODO: Include total count of vocab pasted
# TODO: total count of cards brought to front
# TODO: display number of cards that failed to be brought to front
# TODO: maybe this'd work better if you did by note type instead of deck? (or maybe both)
# TODO: display the vocabs that were found (and total number)
# TODO: display the vocabs that were NOT found (and total number)
# TODO: add functionality to tag the cards that were moved by adding tag: movedByPushToFrontPlugin
# TODO: drop-down menu of decks and note types
# TODO: drop-down menu of delimiter

# TODO: include functionaly for user to push only CERTAIN CARDS, not entire notes

# =====================  =====================  =====================


class TextEditor(QDialog):
    # mw is passed as parent
    def __init__(self, parent):

        # QDialog args from http://pyqt.sourceforge.net/Docs/PyQt4/qdialog.html#QDialog
        # __init__ (self, QWidget parent = None, Qt.WindowFlags flags = 0)
        super(TextEditor, self).__init__(parent)

        self.list_of_vocabs = []
        # associated with a drop-down widget where the drop-down displays all decks and subdecks
        self.selected_deck = ''                                 # TODO: to be filled in by a signal
        self.selected_model = ''
        self.field_tomatch= ''

        self.vocabulary_text = QTextEdit(self)                  # QTextEdit 1st arg = parent

        # ===================== BUTTONS =====================
        self.clr_btn = QPushButton('Clear Text')                # works
        self.resched_btn = QPushButton('Reschedule')
        self.write_to_list_btn = QPushButton('Write to List')
        self.write_to_txt_btn = QPushButton('Write to CSV')
        self.import_btn = QPushButton('Import CSV')
        self.clear_list = QPushButton('Clear List')

        # FIXME: temp button
        self.show_contents = QPushButton('Show Contents')

        # ===================== SIGNALS =====================
        self.write_to_list_btn.clicked.connect(self.write_to_list)
        self.resched_btn.clicked.connect(self.reschedule_cards)
        self.clr_btn.clicked.connect(self.clear_text)
        self.write_to_txt_btn.clicked.connect(self.csv_write)
        # TODO: add an additional LineEdit box where I can input what the delimiter will be
        self.import_btn.clicked.connect(lambda: self.import_csv(delimiter='\n'))
        self.show_contents.clicked.connect(self.show_contents_signal)
        self.clear_list.clicked.connect(self.reset_list)

        self.vocabulary_text.textChanged.connect(self.value_changed)

        # setWindowTitle is probably a super method from QtGui
        self.setWindowTitle('Push')

        self.init_ui()

    def init_ui(self):
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        # buttons lined horizontally
        # to be added later to v_layout
        h_layout.addWidget(self.clr_btn)
        h_layout.addWidget(self.resched_btn)
        h_layout.addWidget(self.show_contents)
        h_layout.addWidget(self.write_to_list_btn)
        h_layout.addWidget(self.write_to_txt_btn)
        h_layout.addWidget(self.import_btn)
        h_layout.addWidget(self.clear_list)

        v_layout.addWidget(self.vocabulary_text)

        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

        self.show()

    # FIXME: doesn't fucking work
    def value_changed(self):
        # self.vocabulary_text.setText(str(self.vocabulary_text.toPlainText()))
        # list_of_vocabs = mw.text.text()

        self.list_of_vocabs[:] = []    # empty it before filling it again

        for line in self.vocabulary_text.toPlainText():
            self.list_of_vocabs.append(line)

    # temporary
    # only created this so that I'd see what the contents are
    # FIXME: works but the file is empty
    def csv_write(self):
        filename = QFileDialog.getSaveFileName(self,
                                               'Save CSV',
                                               os.getenv('HOME'),
                                               'TXT(*.csv *.txt)'
                                               )
        showInfo(filename)
        if filename:
            if filename != '':   # what does this do again?
                with open(filename, 'w') as file:

                    # csvwriter = csv.writer(file, delimiter='\n', quotechar='|')
                    for line in self.list_of_vocabs:
                        # showInfo(line)
                        file.write(line)

    # works!
    def import_csv(self, delimiter='\n'):
        # getOpenFileName (QWidget parent = None, QString caption = '',
        # QString directory = '', QString filter = '', Options options = 0)
        filename = QFileDialog.getOpenFileName(self,
                                               'Open CSV',
                                               os.getenv('HOME'),
                                               'TXT(*.csv *.txt)'
                                               )

        if filename:
            if filename != '':   # what does this do again?
                with open(filename, 'r') as file:

                    csvreader = csv.reader(file, delimiter=delimiter, quotechar='|')
                    for line in csvreader:
                        self.list_of_vocabs.append(line)

    def write_to_list(self):
        for line in self.vocabulary_text.toPlainText():
            self.list_of_vocabs.append(line)

    #
    def show_contents_signal(self):
        # showInfo(str(len(self.list_of_vocabs)))
        showInfo(str(self.list_of_vocabs))

    # works
    def clear_text(self):
        self.vocabulary_text.clear()
        self.vocabulary_text.setText('')

    def reset_list(self):
        # how to empty list
        # https://stackoverflow.com/questions/1400608/how-to-empty-a-list-in-python
        self.list_of_vocabs[:] = []

    # MAIN
    def reschedule_cards(self):
        # did = mw.col.decks.id("Board_Exam_Rev")
        # print(dir(mw.col.decks.id("Board_Exam_Rev")))
        # deck = mw.col.decks.byName("Board_Exam_Rev")

        # NOTE: REPL STUFF
        # from pprint import pprint
        #
        # pprint(dir(mw.col.decks))

        did = mw.col.decks.id(self.selected_deck)   # returns the deck ID of the selected deck
        mw.col.decks.select(did)                    # select the deck based on ID

        deck = mw.col.decks.byName(self.selected_deck)

        ids = mw.col.findCards(did) # lol, is this even legal
        '''
        from collection.py
            def findCards(self, query, order=False):
                return anki.find.Finder(self).findCards(query, order)
        '''

        '''
        from anki/find.py
                def findCards(self, query, order=False):
                    "Return a list of card ids for QUERY."
                    tokens = self._tokenize(query)
                    preds, args = self._where(tokens)
                    if preds is None:
                        raise Exception("invalidSearch")
                    order, rev = self._order(order)
                    sql = self._query(preds, order)
                    try:
                        res = self.col.db.list(sql, *args)
                    except:
                        # invalid grouping
                        return []
                    if rev:
                        res.reverse()
                    return res
        '''
        for id in ids:
            card = mw.col.getCard(id)

        # pprint(deck.values)

        # get model of deck
        model = mw.col.models.byName(self.selected_model)

        # maybe SQLite would be better lol?

        for c, name in enumerate()


def init_window():
    mw.texteditor = TextEditor(mw)

run_action = QAction('Push Existing Vocabulary', mw)
run_action.setShortcut(QKeySequence(HOTKEY))
run_action.triggered.connect(init_window)

mw.form.menuTools.addAction(run_action)

# ## I might need to use SQLITE for changing the due value of the said cards
# ## and unsuspend them simultaneously
# https://www.python.org/dev/peps/pep-0350/
