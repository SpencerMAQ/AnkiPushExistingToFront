# -*- coding: utf-8 -*-

# This file is part of the Push Existing Vocab add-on for Anki
# Copyright: SpencerMAQ (Michael Spencer Quinto) <spencer.michael.q@gmail.com> 2017
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

# import sys                        # TODO: temp import
# sys.path.append(r'C:\Users\Mi\AppData\Local\Programs\Python\Python35\Lib\anki\anki')
# sys.path.append(r'C:\Users\Mi\AppData\Local\Programs\Python\Python35\Lib\anki\aqt')
from aqt.qt import *
from aqt import mw
from anki.hooks import addHook
from aqt.utils import showInfo      # TODO: temporary import
# import csv
import os
import codecs
import time
from PyQt4 import QtCore

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

# from PyQt5.QtWidgets import *       # TODO: temporary import    =======
# from PyQt5.QtGui import *           # TODO: temporary import    =======
from anki.storage import Collection

__version__ = '1.0.0'
# July 19 2017

# ## NOTE: YOU MUST RESET THE SCHEDULER AFTER ANY DB CHANGES
# ## BY DOING mw.reset()

HOTKEY = "Shift+P"


# ===================== TEMPORARY STUFF ===================== #
# ===================== TEMPORARY STUFF ===================== #
# just so I can get the namespaces inside  Collection
# manually typing them is very hard, and I'm very lazy
# TODO: comment out when porting

# class Temporary:
#     def __init__(self):
#         self.col = Collection('', log=True)
#
# mw = Temporary()

# ===================== TEMPORARY STUFF ===================== #
# ===================== TEMPORARY STUFF ===================== #


# deck_id = mw.col.decks.id(name_of_deck)
# deck = mw.col.decks.select(deck_id)
#
# deck_note = deck.note()

# ===================== FIELDS ===================== #

# ## The name of the field where the add-on
# ## will search
field_to_match = ''     # e.g. expression
# ## Select the deck you'd want to change
name_of_deck = ''

#############################################################

#  ===================== TO_DO_LIST ===================== #

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

# =====================  =====================  ===================== #


class TextEditor(QDialog):
    # mw is passed as parent
    def __init__(self, parent):
        """
        Initialize the UI
        :param parent:      global mw from aqt
        """

        # QDialog args from http://pyqt.sourceforge.net/Docs/PyQt4/qdialog.html#QDialog
        # __init__ (self, QWidget parent = None, Qt.WindowFlags flags = 0)
        super(TextEditor, self).__init__(parent)

        self.list_of_vocabs = []                                # list of mined vocab
        self.list_of_deck_vocabs_20k = []

        self.matched_vocab = []                                 # matched and rescheduled
        self.matchned_but_not_rescheduled = []
        self.unmatched_vocab = []
        # associated with a drop-down widget where the drop-down displays all decks and subdecks
        self.selected_deck = ''                                 # TODO: to be filled in by a signal
        self.selected_model = ''                                # TODO: to be filled in by a signal
        self.field_tomatch = ''                                 # TODO: to be filled in by a signal

        self.vocabulary_text = QPlainTextEdit(self)                  # QTextEdit 1st arg = parent

        # ===================== BUTTONS ===================== #
        self.clr_btn = QPushButton('Clear Text')                # works
        self.resched_btn = QPushButton('Reschedule')
        self.write_to_list_btn = QPushButton('Write to List')
        self.write_to_txt_btn = QPushButton('Write to CSV')
        self.import_btn = QPushButton('Import CSV')
        self.clear_list = QPushButton('Clear List')

        self.show_reschd_matched_cards = QPushButton('Show Rescheduled Matches')
        self.show_nonrschd_matched_cards = QPushButton('Show Matched but not Reschedued')
        self.show_unmatched_cards = QPushButton('Cards without any matches')

        # FIXME: temp button
        self.show_contents = QPushButton('Show Contents')
        self.write_deck_vocabs20k_to_CSV = QPushButton('Write Deck Vocabs to CSV')

        # ===================== SIGNALS ===================== #
        # self.write_to_list_btn.clicked.connect(self.write_to_list)
        self.resched_btn.clicked.connect(self.reschedule_cards_alternate)
        # self.clr_btn.clicked.connect(self.clear_text)
        self.write_to_txt_btn.clicked.connect(self.csv_write)
        # TODO: add an additional LineEdit box where I can input what the delimiter will be
        self.import_btn.clicked.connect(lambda: self.import_csv(delimiter='\n'))
        self.show_contents.clicked.connect(self.show_contents_signal)
        self.clear_list.clicked.connect(self.reset_list)

        self.show_reschd_matched_cards.clicked.connect(self.show_rescheduled)
        self.show_nonrschd_matched_cards.clicked.connect(self.show_not_rescheduled)
        self.show_unmatched_cards.clicked.connect(self.show_not_matched)

        self.vocabulary_text.textChanged.connect(self.value_changed)

        # TODO: TEMP BUTTON
        self.write_deck_vocabs20k_to_CSV.clicked.connect(self.write_deck_vocab_to_csv_method)

        # setWindowTitle is probably a super method from QtGui
        self.setWindowTitle('Push')

        self.init_ui()

    # FIXME: TEMPORARY
    def write_deck_vocab_to_csv_method(self):
        filename = QFileDialog.getSaveFileName(self,
                                               'Save CSV',
                                               os.getenv('HOME'),
                                               'TXT(*.txt)'
                                               )
        if filename:
            if filename != '':
                with open(filename, 'w') as file:

                    for _iter, line in enumerate(self.list_of_deck_vocabs_20k):
                        file.write(line.encode('utf-8'))
                        showInfo(_fromUtf8(line))
                        if _iter == 1:
                            break

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

        h_layout.addWidget(self.show_reschd_matched_cards)
        h_layout.addWidget(self.show_nonrschd_matched_cards)
        h_layout.addWidget(self.show_unmatched_cards)

        h_layout.addWidget(self.write_deck_vocabs20k_to_CSV)

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
        # for line in self.vocabulary_text.text():

            self.list_of_vocabs.append(line)

    # temporary
    # only created this so that I'd see what the contents are
    # works!
    def csv_write(self):
        filename = QFileDialog.getSaveFileName(self,
                                               'Save CSV',
                                               os.getenv('HOME'),
                                               'TXT(*.txt)'
                                               )
        # showInfo(filename)
        if filename:
            if filename != '':   # what does this do again?
                with open(filename, 'w') as file:
                # with open(filename, 'w', encoding='utf-8') as file:

                    # csvwriter = csv.writer(file, delimiter='\n', quotechar='|')
                    for line in self.list_of_vocabs:
                        # line = line.decode('utf-8')
                        # showInfo(line.encode('utf-8'))
                        file.write(line.encode('utf-8'))

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
                # why the heck does Py 2.7 not have an encoding parameter????!!!!!!
                # with open(filename, 'r') as file:
                with codecs.open(filename, 'r', encoding='utf-8') as file:

                    # csvreader = csv.reader(file, delimiter=delimiter, quotechar='|')
                    for line in file:
                        # line = line.decode('utf-8')
                        self.list_of_vocabs.append(line)

    # obsolete!?
    def write_to_list(self):
        self.list_of_vocabs[:] = []

        for line in self.vocabulary_text.toPlainText():
            self.list_of_vocabs.append(line)

    #
    def show_contents_signal(self):
        # showInfo(str(len(self.list_of_vocabs)))
        # showInfo(str(self.list_of_vocabs))
        for vocab in self.list_of_vocabs:
            showInfo(_fromUtf8(vocab))


    # works
    def clear_text(self):
        self.vocabulary_text.clear()
        self.vocabulary_text.setText('')

    def reset_list(self):
        # how to empty list
        # https://stackoverflow.com/questions/1400608/how-to-empty-a-list-in-python
        self.list_of_vocabs[:] = []

    def show_rescheduled(self):
        # showInfo(str(self.matched_vocab))
        for matched in self.matched_vocab:
            showInfo(_fromUtf8(matched))


    def show_not_rescheduled(self):
        # showInfo(str(self.matchned_but_not_rescheduled))
        for matched_but_not_res in self.matchned_but_not_rescheduled:
            showInfo(_fromUtf8(matched_but_not_res))

    def show_not_matched(self):
        # showInfo(str(self.unmatched_vocab))
        for unmatched in self.unmatched_vocab:
            showInfo(_fromUtf8(unmatched))

    def reschedule_cards_alternate(self):
        """
        Main function of the program
        Checks every Note > Field if it is inside the
        list of mined words and sets the due date to zero accdngly
        :return:    None
        """

        self.field_tomatch = 'Expression_Original_Unedited'
        self.selected_model = 'Japanese-1b811 example_sentences'

        self.number_of_replacements = 0

        mid = mw.col.models.byName(self.selected_model)['id']
        nids = mw.col.findNotes('mid:' + str(mid))      # returns a list of noteIds

        ctr = 0

        # list comprehension of tuples in format: nid, first field for that nid (reversed)
        dict_of_note_first_fields = {mw.col.getNote(note_id)[self.field_tomatch].strip().strip('<span>').strip('</span>') : mw.col.getNote(note_id)
                                     for note_id in nids}
        self.list_of_deck_vocabs_20k = dict_of_note_first_fields.keys()
        list_of_vocabs = [_fromUtf8(vocab) for vocab in self.list_of_vocabs]

        for vocab in list_of_vocabs:
            if vocab.strip() in self.list_of_deck_vocabs_20k:
                nid = dict_of_note_first_fields[_fromUtf8(vocab.strip())]

                cids = mw.col.findCards('nid:' + str(nid))

                try:
                    first_card_id = cids[0]
                except IndexError:
                    first_card_id = cids

                card = mw.col.getCard(first_card_id)

                if card.type == 0:
                    self.matched_vocab.append(vocab)
                    # card.due = 0
                    ctr += 1
                    self.number_of_replacements += 1

                    mw.col.db.execute(''' UPDATE cards
                                            SET due = ?,
                                                mod = ?,
                                                usn = -1
                                            WHERE
                                                id = ?
                                                    AND
                                                type = 0
                                        ''', ctr, str(int(time.time())), int(first_card_id)
                                      )

                elif card.queue == -1:
                    self.matched_vocab.append(vocab)
                    # card.due = 0
                    ctr += 1
                    self.number_of_replacements += 1

                    mw.col.db.execute(''' UPDATE cards
                                            SET due = ?,
                                                mod = ?,
                                                usn = -1,
                                                type = 0
                                            WHERE
                                                id = ?
                                                    AND
                                                type = 0
                                        ''', ctr, str(int(time.time())), int(first_card_id)
                                      )

                elif card.queue != -1:
                    self.matchned_but_not_rescheduled.append(vocab)

                elif card.type != 0:
                    # cards that weren't rescheduled because they're learning/mature
                    self.matchned_but_not_rescheduled.append(vocab)

            else:
                self.unmatched_vocab.append(vocab)

        mw.reset()


    # MAIN
    def reschedule_cards(self):
        """
        Main function of the program
        Checks every Note > Field if it is inside the
        list of mined words and sets the due date to zero accdngly
        :return:    None
        """
        # did = mw.col.decks.id("")
        # print(dir(mw.col.decks.id("")))
        # deck = mw.col.decks.byName("")

        # FIXME: recode this entire function such that you only check for
        # each vocab if they are in the collection
        # i.e. for vocab in list of vocabs

        self.field_tomatch = 'Expression_Original_Unedited'
        self.selected_model = 'Japanese-1b811 example_sentences'

        self.number_of_replacements = 0

        mid = mw.col.models.byName(self.selected_model)['id']
        nids = mw.col.findNotes('mid:' + str(mid))

        ctr = 0
        for note_id in nids:
            note = mw.col.getNote(note_id)
            # field to match:
            # note[self.field_tomatch]

            # list_of_vocabs = [i.encode('utf-8') for i in self.list_of_vocabs]
            list_of_vocabs = [_fromUtf8(vocab) for vocab in self.list_of_vocabs]

            # note[self.field_tomatch] is unicode OK

            # if unicode(note[self.field_tomatch], 'utf-8') in list_of_vocabs:
            # note_first_field = note[self.field_tomatch]

            if note[self.field_tomatch] in list_of_vocabs:

                # note is a dictionary containing all the fields
                # Note that from common sense, the Notes themselves
                # won't have due values because it is the cards that
                # are supposed to be studied
                cids = mw.col.findCards('nid:' + str(note_id))
                first_card_id = cids[0]
                # cids = card IDs (if there is more than one card)

                card = mw.col.getCard(first_card_id)

                # https://github.com/ankidroid/Anki-Android/wiki/Database-Structure
                # 0=new, 1=learning, 2=due
                # reschedule should be limited only to new cards, don't touch learning and due cards
                if card.type == 0:
                    # just for checking purposes, i.e. place the names of the rescheduled cards in a list
                    self.matched_vocab.append(note[self.field_tomatch])
                    # reschedule card
                    card.due = 0
                    ctr += 1
                    self.number_of_replacements += 1

                    mw.col.db.execute(  ''' UPDATE cards
                                            SET due = ?,
                                                mod = ?,
                                                usn = -1
                                            WHERE
                                                id = ? AND
                                                type = 0
                                        ''', ctr, time.time(), first_card_id
                                        )

                    '''
                    IMPORTANT NOTE TO SELF:
                    doing things like card.due = 0 doesn't work because
                    It doesn't tap into the database
                    '''

                elif card.queue == -1:
                    # just for checking purposes, i.e. place the names of the rescheduled cards in a list
                    self.matched_vocab.append(note[self.field_tomatch])
                    # reschedule card
                    card.due = 0
                    ctr += 1
                    self.number_of_replacements += 1

                    mw.col.db.execute(  ''' UPDATE cards
                                            SET due = ?,
                                                mod = ?,
                                                usn = -1
                                                type = 0
                                            WHERE
                                                id = ? AND
                                                type = 0
                                        ''', ctr, time.time(), first_card_id
                                        )
                elif card.queue != -1:
                    self.matchned_but_not_rescheduled.append(note[self.field_tomatch])

                elif card.type != 0:
                    # cards that weren't rescheduled because they're learning/mature
                    self.matchned_but_not_rescheduled.append(note[self.field_tomatch])

            # else:
                # FIXME: this adds the wrong vocab (every vocab from the 20k+ vocab
                # self.unmatched_vocab.append(note[self.field_tomatch])

        # pycharm can't detect reset
        mw.reset()
        '''
        ------from anki/find.py------
                def findCards(self, query, order=False):
                    "Return a list of card ids for QUERY."

        '''


def init_window():
    mw.texteditor = TextEditor(mw)

run_action = QAction('Push Existing Vocabulary', mw)
run_action.setShortcut(QKeySequence(HOTKEY))
run_action.triggered.connect(init_window)

mw.form.menuTools.addAction(run_action)

# ## I might need to use SQLITE for changing the due value of the said cards
# ## and unsuspend them simultaneously
# TODO: vvv What's that?
# https://www.python.org/dev/peps/pep-0350/
