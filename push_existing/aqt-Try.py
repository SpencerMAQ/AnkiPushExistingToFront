# -*- coding: utf-8 -*-

# This file is part of the Push Existing Vocab add-on for Anki
# Copyright: SpencerMAQ (Michael Spencer Quinto) 2017
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

# NOTE: I've limited the number of replacements to the num of vocabs just so that this won't screw things just in case
# NOTE: This script unsuspends suspended cards as well but doesn't work for some vocabs dunno why

from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo          # TODO: temporary import
from anki.utils import intTime
import csv
import os
import codecs

# Credits to Alex Yatskov (foosoft)
# I'm not even sure what this does
from PyQt4 import QtCore
try:
    _from_utf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _from_utf8(s):
        return s

__version__ = '0.0'
# July 26 2017

HOTKEY = 'Shift+P'
TAG_TO_ADD = 'Rescheduled_by_Push_Existing_Vocab_add-on_for_Anki'

# ===================== TEMPORARY STUFF ===================== #
# just so I can get the namespaces inside  Collection
# manually typing them is very hard, and I'm very lazy
# TODO: comment out when porting

if False:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from anki.storage import Collection

    class Temporary:
        def __init__(self):
            self.col = Collection('', log=True)

    mw = Temporary()
# ===================== TEMPORARY STUFF ===================== #

#  ===================== TO_DO_LIST ===================== #

# TODO: Include total count of vocab pasted
# TODO: total count of cards brought to front
# TODO: display number of cards that failed to be brought to front
# TODO: maybe this'd work better if you did by note type instead of deck? (or maybe both)
# TODO: display the vocabs that were found (and total number)
# TODO: display the vocabs that were NOT found (and total number)

# TODO: (IMPORTANT) add functionality to tag the cards that were moved by adding tag: movedByPushToFrontPlugin

# TODO: drop-down menu of decks and note types
# TODO: drop-down menu of delimiter
# TODO: Make this app use a QMainWindow by creating a new QApplication instance

# TODO: include functionaly for user to push only CERTAIN CARDS, not entire notes (DONE!)

# TODO: convert the vocab lists into sets to avoid rescheduling the same card twice

# TODO: (VERY IMPORTANT) Include a log file of the replacements done, number of replacements, what were not replaced, etc.

# FIXME: The CSV File needs a placeholder as the first line

#  ===================== TO_DO_LIST ===================== #


class TextEditor(QDialog):
    def __init__(self, parent):
        """
        Initialize the UI
        :param parent:      global mw from aqt
        """

        # QDialog args from http://pyqt.sourceforge.net/Docs/PyQt4/qdialog.html#QDialog
        # __init__ (self, QWidget parent = None, Qt.WindowFlags flags = 0)
        super(TextEditor, self).__init__(parent)

        self.matched_vocab = []                                 # matched and rescheduled
        self.list_of_vocabs = []                                # list of mined vocab
        self.unmatched_vocab = []
        self.matchned_but_not_rescheduled = []

        # associated with a drop-down widget where the drop-down displays all decks and subdecks
        self.selected_deck = ''                                 # TODO: to be filled in by a signal
        self.field_tomatch = ''                                 # TODO: to be filled in by a signal
        self.selected_model = ''                                # TODO: to be filled in by a signal
        self.number_of_cards_to_resched_per_note = 1
        self.number_of_notes_in_deck = 0

        # FIXME: Not needed at all
        self.vocabulary_text = QPlainTextEdit(self)             # QTextEdit 1st arg = parent

        # setWindowTitle is probably a super method from QtGui
        self.setWindowTitle('Push Existing Vocab add-on')

        self.init_buttons()
        self.init_signals()
        self.init_ui()

    def init_buttons(self):
        # ===================== PERMANENT ===================== #
        self.import_btn = QPushButton('Import CSV')
        self.clear_list = QPushButton('Clear List')
        self.anki_based_reschedule_button = QPushButton('Anki-Based Resched')

        self.show_contents = QPushButton('Show Contents')

        # ===================== TEMPORARY ===================== #
        # self.resched_btn = QPushButton('Reschedule')
        # self.clr_btn = QPushButton('Clear Text')  # works
        # self.write_to_txt_btn = QPushButton('Write to CSV')
        # self.write_to_list_btn = QPushButton('Write to List') # FIXME: Probably unnecessary

        # ===================== TO BE TRANSFERRED TO LOGGING ===================== #
        self.show_unmatched_cards = QPushButton('Cards without any matches')
        self.show_reschd_matched_cards = QPushButton('Show Rescheduled Matches')
        self.show_nonrschd_matched_cards = QPushButton('Show Matched but not Reschedued')

    def init_signals(self):
        # ===================== PERMANENT ===================== #
        self.clear_list.clicked.connect(self.reset_list)
        self.show_contents.clicked.connect(self.show_contents_signal)
        self.import_btn.clicked.connect(lambda: self.import_csv(delimiter='\n'))
        self.anki_based_reschedule_button.clicked.connect(self.anki_based_reschedule)
        # TODO: add an additional LineEdit(or combobox) box where I can input what the delimiter will be

        self.show_unmatched_cards.clicked.connect(self.show_not_matched)
        self.show_reschd_matched_cards.clicked.connect(self.show_rescheduled)
        self.show_nonrschd_matched_cards.clicked.connect(self.show_not_rescheduled)

        # ===================== TEMPORARY ===================== #
        # self.clr_btn.clicked.connect(self.clear_text)
        # self.vocabulary_text.textChanged.connect(self.value_changed)
        # self.write_to_list_btn.clicked.connect(self.write_to_list)
        # self.write_to_txt_btn.clicked.connect(self.csv_write)
        # self.resched_btn.clicked.connect(self.reschedule_cards_alternate)

    def init_ui(self):
        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()

        # buttons lined horizontally to be added later to v_layout
        # ===================== PERMANENT ===================== #
        h_layout.addWidget(self.import_btn)
        h_layout.addWidget(self.clear_list)
        h_layout.addWidget(self.show_contents)
        h_layout.addWidget(self.anki_based_reschedule_button)

        h_layout.addWidget(self.show_unmatched_cards)
        h_layout.addWidget(self.show_reschd_matched_cards)
        h_layout.addWidget(self.show_nonrschd_matched_cards)

        # ===================== TEMPORARY ===================== #
        # h_layout.addWidget(self.clr_btn)
        # h_layout.addWidget(self.resched_btn)
        # h_layout.addWidget(self.write_to_txt_btn)                   # CSV Write
        # h_layout.addWidget(self.write_to_list_btn)                # FIXME: Temp

        # ===================== PERMANENT (V-Layout) ===================== #
        v_layout.addWidget(self.vocabulary_text)

        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)
        self.show()

    # # FIXME: doesn't fucking work
    # def value_changed(self):
    #     self.list_of_vocabs[:] = []
    #
    #     for line in self.vocabulary_text.toPlainText():
    #         self.list_of_vocabs.append(line)

    # temporary, only created this so that I'd see what the contents are
    # def csv_write(self):
    #     filename = QFileDialog.getSaveFileName(self,
    #                                            'Save CSV',
    #                                            os.getenv('HOME'),
    #                                            'TXT(*.txt)'
    #                                            )
    #
    #     if filename:
    #         with open(filename, 'w') as file:
    #         # with open(filename, 'w', encoding='utf-8') as file:
    #
    #             # csvwriter = csv.writer(file, delimiter='\n', quotechar='|')
    #             for line in self.list_of_vocabs:
    #                 file.write(line.encode('utf-8'))

    # TODO: Combobox for delimiter
    # TODO: use csv writer so I can specify the delimiter
    def import_csv(self, delimiter='\n'):
        del self.list_of_vocabs[:]

        # getOpenFileName (QWidget parent = None, QString caption = '',
        # QString directory = '', QString filter = '', Options options = 0)
        filename = QFileDialog.getOpenFileName(self,
                                               'Open CSV',
                                               os.getenv('HOME'),
                                               'TXT(*.csv *.txt)'
                                               )

        if filename:
            with codecs.open(filename, 'r', encoding='utf-8') as file:

                # program doesn't resched the first vocab in the line
                # csvreader = csv.reader(file, delimiter=delimiter, quotechar='|')
                for line in file:
                    # line = line.decode('utf-8')
                    self.list_of_vocabs.append(line)

        # -1 because of necessary placeholder first line
        if self.list_of_vocabs:
            showInfo('Successfully Imported {} lines from CSV'.format(len(self.list_of_vocabs)-1))
        else:
            showInfo('Nothing Imported')

    def show_contents_signal(self):
        # FiXME: Should show the entire table, not one by one
        list_of_vocabs = self.list_of_vocabs

        if not list_of_vocabs:
            showInfo('The list is empty')

        # FiXME: doesn't remove placeholder from the list, probably because of unicode
        try:
            list_of_vocabs.remove('placeholder')
        except ValueError:
            pass

        try:
            showInfo(_from_utf8(*list_of_vocabs))
        except:
            for vocab in list_of_vocabs:
                showInfo(_from_utf8(vocab))
            # raise

    # def clear_text(self):
    #     self.vocabulary_text.clear()
    #     self.vocabulary_text.setText('')

    def reset_list(self):
        del self.list_of_vocabs[:]

        showInfo('Succesfully reset the list of cards\n'
                 'Please import a text file to fill the list again')

    def show_rescheduled(self):
        for matched in self.matched_vocab:
            showInfo(_from_utf8(matched))

    def show_not_rescheduled(self):
        for matched_but_not_res in self.matchned_but_not_rescheduled:
            showInfo(_from_utf8(matched_but_not_res))

    def show_not_matched(self):
        for unmatched in self.unmatched_vocab:
            showInfo(_from_utf8(unmatched))

    # NOTE: this seems to be slower than my original function
    # might need to recode this
    # TODO: I might recode this to use executemany instead, I doubt that'll speed things up though
    # FIXME: (VERY IMPORTANT!!!) it appears that the first vocab on \
    # the list is not rescheduled (wheter suspended or not)
    # it appears that the fix is simply to add a newline at the beginning of the list
    def anki_based_reschedule(self):
        """
        Main function of the program
        Checks every Note > Field if it is inside the
        list of mined words and sets the due date to zero accdngly
        Version 3: same as version 2 except this one uses built-in Anki modules

        :return:    None
        """
        # FIXME: Temp, will replace with combobox
        self.field_tomatch = 'Expression_Original_Unedited'
        self.selected_model = 'Japanese-1b811 example_sentences'

        self.number_of_replacements = 0

        mid = mw.col.models.byName(self.selected_model)['id']       # model ID
        nids = mw.col.findNotes('mid:' + str(mid))                  # returns a list of noteIds
        ctr = 0

        list_of_vocabs = [_from_utf8(vocab) for vocab in self.list_of_vocabs if vocab != u'placeholder']

        if not list_of_vocabs:
            showInfo('The List is empty\n'
                     'Please Import a File before clicking this button')
            return

        dict_of_note_first_fields = {
            mw.col.getNote(note_id)[self.field_tomatch].strip().strip('<span>').strip('</span>'):
                note_id
                for note_id in nids
            }

        list_of_deck_vocabs_20k = dict_of_note_first_fields.keys()

        if not list_of_deck_vocabs_20k:
            showInfo('The model {} contains no notes\n'
                     'Please try a new note type'.format(self.selected_model))
            return

        self.number_of_notes_in_deck = len(list_of_deck_vocabs_20k)

        for vocab in list_of_vocabs:
            if vocab.strip() in list_of_deck_vocabs_20k and vocab != 'placeholder':
                nid = dict_of_note_first_fields[_from_utf8(vocab.strip())]
                cids = mw.col.findCards('nid:' + str(nid))

                # num of cards to resched per note (default = 1)
                number_of_cards_to_resched_ctr = 0
                for card_id in cids:
                    number_of_cards_to_resched_ctr += 1

                    if number_of_cards_to_resched_ctr >= self.number_of_cards_to_resched_per_note + 1:
                        break

                    card = mw.col.getCard(card_id)

                    if card.type == 0 or card.queue == -1 or card.queue == -2 or card.queue == -3:
                        self.matched_vocab.append(vocab)
                        self.number_of_replacements += 1
                        ctr += 1

                        mw.col.sched.unsuspendCards([card_id])
                        mw.col.sched.sortCards([card_id], start=ctr, step=1)

                    elif card.type != 0:
                        self.matchned_but_not_rescheduled.append(vocab)

                if ctr == len(list_of_vocabs) + 1:
                    break

            else:
                self.unmatched_vocab.append(vocab)

        mw.reset()
        showInfo('Successfully Rescheduled {} cards'.format(self.number_of_replacements))

        if self.matchned_but_not_rescheduled:
            showInfo('Did not reschedule {} cards because they were either learning or due cards'
                     .format(len(self.matchned_but_not_rescheduled)))
        if self.unmatched_vocab:
            showInfo('Unable to find {} cards'.format(len(self.unmatched_vocab)))

    def reschedule_cards_alternate(self):
        """
        Main function of the program
        Checks every Note > Field if it is inside the
        list of mined words and sets the due date to zero accdngly
        Version 2: creates a dictionary of the cards inside the model,
        Then a for loop of the vocabs from the CSV file checks if the
        vocab is inside the dictionary

        :return:    None
        """

        # TODO: Use a combobox for the model instead of this primitive shit
        self.field_tomatch = 'Expression_Original_Unedited'
        self.selected_model = 'Japanese-1b811 example_sentences'

        # TODO: Add a Push Button for this
        self.number_of_replacements = 0

        mid = mw.col.models.byName(self.selected_model)['id']       # model ID
        nids = mw.col.findNotes('mid:' + str(mid))                  # returns a list of noteIds

        ctr = 0

        # list comprehension of tuples in format: nid, first field for that nid (reversed)
        # TODO: how to ensure that all html is stripped? Is there a module for that? (beautifulsoup perhaps?)
        dict_of_note_first_fields = {mw.col.getNote(note_id)[self.field_tomatch].strip().strip('<span>').strip('</span>') :
                                        note_id
                                        for note_id in nids}

        list_of_deck_vocabs_20k = dict_of_note_first_fields.keys()
        list_of_vocabs = [_from_utf8(vocab) for vocab in self.list_of_vocabs]

        self.number_of_notes_in_deck = len(list_of_deck_vocabs_20k)

        for vocab in list_of_vocabs:
            if vocab.strip() in list_of_deck_vocabs_20k and vocab != 'placeholder':
                nid = dict_of_note_first_fields[_from_utf8(vocab.strip())]
                cids = mw.col.findCards('nid:' + str(nid))

                # FIXME: Probably uncessary, only did this because of a prev bug
                try:
                    first_card_id = cids[0]
                except IndexError:
                    first_card_id = cids

                card = mw.col.getCard(first_card_id)

                # FIXME: this if might not be needed, the if next to this might be the only needed clause
                if card.type == 0 or card.queue == -1 or card.queue == -2 or card.queue == -3:
                    self.matched_vocab.append(vocab)
                    self.number_of_replacements += 1
                    ctr += 1

                    # NOTE: You can't use LIMIT inside this SQL operation because they only execute one at a time
                    # Same as type, but -1=suspended, -2=user buried, -3=sched buried
                    mw.col.db.execute(''' UPDATE cards
                                            SET due = ?,
                                                mod = ?,
                                                usn = -1,
                                                type = 0,
                                                queue = 0
                                            WHERE
                                                id = ?
                                        ''',
                                            ctr,
                                            intTime(),
                                            int(first_card_id)
                                      )

                elif card.type != 0:
                    # cards that weren't rescheduled because they're learning/mature
                    self.matchned_but_not_rescheduled.append(vocab)

                # NOTE: break when the number of replacements is the same as the list length
                if ctr == len(list_of_vocabs) + 2:
                    break

            else:
                self.unmatched_vocab.append(vocab)

        mw.reset()
        showInfo('Successfully Rescheduled {} cards'.format(self.number_of_replacements))


def init_window():
    mw.texteditor = TextEditor(mw)

run_action = QAction('Push Existing Vocabulary', mw)
run_action.setShortcut(QKeySequence(HOTKEY))
run_action.triggered.connect(init_window)

mw.form.menuTools.addAction(run_action)

# TODO: vvv What's that?
# https://www.python.org/dev/peps/pep-0350/
