# -*- coding: utf-8 -*-

# This file is part of the Push Existing Vocab add-on for Anki
# Copyright: SpencerMAQ (Michael Spencer Quinto) <spencer.michael.q@gmail.com> 2017
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo
from aqt.addons import AddonManager
import csv                              # practically useless on py 2.7
import os
import sys
import logging

if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
    from functools import lru_cache

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
TAG_TO_ADD = 'Rescheduled_by_Push_Existing_Vocab'

# ===================== DO NOT EDIT BEYOND THIS LINE ===================== #
LOG_FORMAT = '%(levelname)s \t| %(asctime)s: \t%(message)s'

addon_mgr_instance = AddonManager(mw)
ADD_ON_PATH = addon_mgr_instance.addonsFolder()

if not os.path.exists(ADD_ON_PATH + '/push_existing'):
    os.makedirs(ADD_ON_PATH + '/push_existing')
NEW_PATH = os.path.join(ADD_ON_PATH, 'push_existing')
NEW_PATH = os.path.join(NEW_PATH, 'logging.log')

# DEBUG 10 INFO 20 WARNING 30 ERROR 40 CRITICAL 50
logging.basicConfig(filename=NEW_PATH,
                    level=logging.DEBUG,
                    format=LOG_FORMAT)

logger = logging.getLogger()

del addon_mgr_instance

# ===================== TEMPORARY STUFF ===================== #
# just so I can get the namespaces inside  Collection
# manually typing them is very hard, and I'm very lazy

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

# TODO: maybe this'd work better if you did by note type instead of deck? (or maybe both)

# TODO: Make this app use a QMainWindow by creating a new QApplication instance

# TODO: include functionaly for user to push only CERTAIN CARDS based on the names of the cards (Diffucult)

# TODO: convert the vocab lists into sets to avoid rescheduling the same card twice

# TODO: Add functionality for user to decide whether or not to add tags to the notes
# TODO: test for other delimiters

#  ===================== TO_DO_LIST ===================== #


class TextEditor(QDialog):
    def __init__(self, parent):
        """
        Initialize the UI
        :param parent:      global mw from aqt
        """

        # __init__ (self, QWidget parent = None, Qt.WindowFlags flags = 0)
        super(TextEditor, self).__init__(parent)

        self.matched_vocab                          = []
        self.list_of_vocabs                         = []
        self.unmatched_vocab                        = []
        self.matchned_but_not_rescheduled           = []

        # associated with a drop-down widget where the drop-down displays all decks and subdecks
        self.selected_deck                          = ''        # TODO: to be filled in by a signal
        self.field_tomatch                          = ''        # TODO: to be filled in by a signal
        self.selected_model                         = ''        # TODO: to be filled in by a signal
        self.number_of_cards_to_resched_per_note    = 1
        self.number_of_notes_in_deck                = 0
        self.enable_add_note_tag                    = True      # TODO: RadioButtons
        self.delimiter                              = '\n'
        self.encoding                               = 'UTF-8'
        # self.delimiter = '\r\n'
        # self.encoding = 'UTF-8-SIG'

        # setWindowTitle is probably a super method from QtGui
        self.setWindowTitle('Push Existing Vocab add-on')

        self._init_buttons()
        self._init_signals()
        self._init_ui()

    def _init_buttons(self):
        self.import_btn = QPushButton('Import CSV')
        self.show_contents = QPushButton('Show Contents')
        self.anki_based_reschedule_button = QPushButton('Anki-Based Resched')

        self.open_logfile_button = QPushButton('Open Log')
        self.clear_list = QPushButton('Clear List')

        # ===================== COMBOX BOXES ===================== #
        self._models_combo = QComboBox()
        self._models_combo.addItems(['Japanese-1b811 example_sentences', 'Placeholder 1'])

        self._fields_combo = QComboBox()
        self._fields_combo.addItems(['Expression_Original_Unedited', 'Placeholder 1'])

        self._cards_to_resch_combo = QComboBox()
        self._cards_to_resch_combo.addItems(['1', '2', '3', '4', '5', '6', '7', '8', '9', 'All'])

        self._delimiter_combo = QComboBox()
        self._delimiter_combo.addItems([r'\n',
                                        r'\t',
                                        'One Whitespace',
                                        '", "(Comma then space)',
                                        '","(Comma without space)',
                                        r'";"(Semicolon without space)',
                                        r'"; "(Semicolon with space)']
                                       )

        self._num_imported_cards_lcd = QLCDNumber()
        self._num_notes_in_deck_lcd = QLCDNumber()
        self._num_cards_succ_resch_lcd = QLCDNumber()
        self._num_cards_found_learning_due_lcd = QLCDNumber()
        self._num_cards_no_matches_lcd = QLCDNumber()

    def _init_signals(self):
        self.import_btn.clicked.connect(lambda: self.import_csv(self.delimiter, self.encoding))
        self.show_contents.clicked.connect(self.show_contents_signal)
        self.anki_based_reschedule_button.clicked.connect(self.anki_based_reschedule)

        self.open_logfile_button.clicked.connect(self.open_log_file)
        self.clear_list.clicked.connect(self.reset_list)

    def _init_ui(self):
        # ===================== SEPARATOR ===================== #
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator.setLineWidth(0.1)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separator2.setLineWidth(0.1)

        # ===================== COMBOBOX LAYOUTS ===================== #
        combo_ver_layout_1 = QVBoxLayout()
        combo_ver_lay1_label = QLabel('Models (Note Types)')
        combo_ver_layout_1.addWidget(combo_ver_lay1_label)
        combo_ver_layout_1.addWidget(self._models_combo)

        combo_ver_layout_2 = QVBoxLayout()
        combo_ver_lay2_label = QLabel('Field to Match')
        combo_ver_layout_2.addWidget(combo_ver_lay2_label)
        combo_ver_layout_2.addWidget(self._fields_combo)

        combo_ver_layout_3 = QVBoxLayout()
        combo_ver_lay3_label = QLabel('Num of Cards in Note to Push')
        combo_ver_layout_3.addWidget(combo_ver_lay3_label)
        combo_ver_layout_3.addWidget(self._cards_to_resch_combo)

        combo_ver_layout_4 = QVBoxLayout()
        combo_ver_lay4_label = QLabel('Delimiter')
        combo_ver_layout_4.addWidget(combo_ver_lay4_label)
        combo_ver_layout_4.addWidget(self._delimiter_combo)

        combo_layout = QHBoxLayout()
        combo_layout.addLayout(combo_ver_layout_1)
        combo_layout.addLayout(combo_ver_layout_2)
        combo_layout.addLayout(combo_ver_layout_3)
        combo_layout.addLayout(combo_ver_layout_4)

        # ===================== LCD BOXES ===================== #
        lcd_ver_layout_1 = QVBoxLayout()
        ver_layout_1_label = QLabel('Imported')
        lcd_ver_layout_1.addWidget(ver_layout_1_label)
        lcd_ver_layout_1.addWidget(self._num_imported_cards_lcd)

        lcd_ver_layout_2 = QVBoxLayout()
        ver_layout_2_label = QLabel('Notes in Model')
        lcd_ver_layout_2.addWidget(ver_layout_2_label)
        lcd_ver_layout_2.addWidget(self._num_notes_in_deck_lcd)

        lcd_ver_layout_3 = QVBoxLayout()
        ver_layout_3_label = QLabel('Rescheduled')
        lcd_ver_layout_3.addWidget(ver_layout_3_label)
        lcd_ver_layout_3.addWidget(self._num_cards_succ_resch_lcd)

        lcd_ver_layout_4 = QVBoxLayout()
        ver_layout_4_label = QLabel('Already Learning/Due')
        lcd_ver_layout_4.addWidget(ver_layout_4_label)
        lcd_ver_layout_4.addWidget(self._num_cards_found_learning_due_lcd)

        lcd_ver_layout_5 = QVBoxLayout()
        ver_layout_5_label = QLabel('No Match')
        lcd_ver_layout_5.addWidget(ver_layout_5_label)
        lcd_ver_layout_5.addWidget(self._num_cards_no_matches_lcd)

        lcd_layout = QHBoxLayout()
        lcd_layout.addLayout(lcd_ver_layout_1)
        lcd_layout.addLayout(lcd_ver_layout_2)
        lcd_layout.addLayout(lcd_ver_layout_3)
        lcd_layout.addLayout(lcd_ver_layout_4)
        lcd_layout.addLayout(lcd_ver_layout_5)

        v_layout = QVBoxLayout()
        v_layout.addLayout(combo_layout)
        v_layout.addWidget(separator)
        v_layout.addLayout(lcd_layout)

        h_layout = QHBoxLayout()

        # buttons lined horizontally to be added later to v_layout
        h_layout.addWidget(self.import_btn)
        h_layout.addWidget(self.show_contents)
        h_layout.addWidget(self.anki_based_reschedule_button)

        h_layout.addWidget(self.open_logfile_button)
        h_layout.addWidget(self.clear_list)

        v_layout.addWidget(separator2)
        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)
        self.setFocus()
        self.show()

    def import_csv(self, delimiter, encoding):
        """
        Import a DSV File with special provisions based on encoding
        Do note the difference between 'utf-8-sig' (with BOM) and 'utf-8'

        :param delimiter:   '\n' by default
        :param encoding:    'utf-8' by default
        :return:
        """

        filename = QFileDialog.getOpenFileName(self,
                                               'Open CSV',
                                               os.getenv('HOME'),
                                               'TXT(*.csv *.txt)'
                                               )

        if filename:
            self.reset_list()
            del self.list_of_vocabs[:]

            # EAFP Approach as opposed to LBYL
            try:
                if sys.version_info[0] == 2:
                    import codecs
                    with codecs.open(filename, 'r', encoding=encoding) as file:
                        self.__read_files(file, delimiter)

                elif sys.version_info[0] == 3:
                    with open(filename, 'r', encoding=encoding) as file:
                        self.__read_files(file, delimiter)

            except OSError as e:
                showInfo('Could not process the file because {}'.format(str(e)))

        if filename and self.list_of_vocabs:
            self.reset_lcd_display()
            showInfo('Successfully Imported {} lines from CSV'.format(len(self.list_of_vocabs)))
            self._num_imported_cards_lcd.display(len(self.list_of_vocabs))
        elif not filename and self.list_of_vocabs:
            showInfo('Nothing Imported\nThe contents of your previous import are retained')
        else:
            showInfo('Nothing Imported')

    def __read_files(self, file, delimiter):
        """
        It's annoying that I have to define a new method
        Just because it won't recognize self inside the nested function

        :param file:
        :param delimiter:
        :return:
        """
        contents = file.read()
        csvreader = contents.split(delimiter)

        for line in csvreader:
            self.list_of_vocabs.append(line.strip('\r'))

        # for line in file:
        #     self.list_of_vocabs.append(line)

    def show_contents_signal(self):
        # FiXME: Should show the entire table, not one by one
        list_of_vocabs = self.list_of_vocabs

        if not list_of_vocabs:
            showInfo('The list is empty')

        try:
            showInfo(_from_utf8(*list_of_vocabs))
        except:
            for vocab in list_of_vocabs:
                showInfo(_from_utf8(vocab))
            # raise

    def reset_list(self):
        """
        Primarily used as an event in response to the button
        Used in other methods as well (import csv and resched)
        to ensure that the lists they need are empty
        :return:
        """
        del self.matched_vocab[:]
        del self.unmatched_vocab[:]
        del self.matchned_but_not_rescheduled[:]
        sender = self.sender()

        if sender.text() == 'Clear List':
            del self.list_of_vocabs[:]
            showInfo('Succesfully reset the list of cards\n'
                     'Please import a text file to fill the list again')
            self.reset_lcd_display()

    def reset_lcd_display(self):
        self._num_imported_cards_lcd.display(0)
        self._num_notes_in_deck_lcd.display(0)
        self._num_cards_succ_resch_lcd.display(0)
        self._num_cards_found_learning_due_lcd.display(0)
        self._num_cards_no_matches_lcd.display(0)

    def show_rescheduled(self):
        if self.matched_vocab:
            for matched in self.matched_vocab:
                showInfo(_from_utf8(matched))

        else:
            showInfo('None')

    def show_not_rescheduled(self):
        if self.matchned_but_not_rescheduled:
            for matched_but_not_res in self.matchned_but_not_rescheduled:
                showInfo(_from_utf8(matched_but_not_res))

        else:
            showInfo('None')

    def show_not_matched(self):
        if self.unmatched_vocab:
            for unmatched in self.unmatched_vocab:
                showInfo(_from_utf8(unmatched))

        else:
            showInfo('None')

    @staticmethod
    def open_log_file():
        if sys.version_info[0] == 3:
            from webbrowser import open
            open(NEW_PATH)

        elif sys.version_info[0] == 2:
            os.startfile(NEW_PATH)

    # NOTE: this seems to be slower than my original function
    # TODO: I might recode this to use executemany instead, I doubt that'll speed things up though
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
        self.reset_list()

        mid = mw.col.models.byName(self.selected_model)['id']       # model ID
        nids = mw.col.findNotes('mid:' + str(mid))                  # returns a list of noteIds

        logger.info('=================================================================\n'
                    'Version {}\n'.format(__version__) +
                    'Imported from CSV: \t' +
                    ', '.join(vocab.encode(self.encoding) for vocab in self.list_of_vocabs)
                    )

        if not self.list_of_vocabs:
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
                     'Please try a new note type'.format(self.selected_model)
                     )
            return

        self.number_of_notes_in_deck = len(list_of_deck_vocabs_20k)

        for vocab in self.list_of_vocabs:
            if vocab.strip() in list_of_deck_vocabs_20k:
                nid = dict_of_note_first_fields[vocab.strip()]
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

                        mw.col.sched.unsuspendCards([card_id])
                        mw.col.sched.sortCards([card_id], start=self.number_of_replacements, step=1)

                        logger.info('Rescheduled card: {} with cardID: \t{}'
                                    .format(vocab.encode(self.encoding), card_id))

                        if self.enable_add_note_tag:
                            n = card.note()
                            n.addTag(TAG_TO_ADD)
                            # "If fields or tags have changed, write changes to disk."
                            n.flush()

                    elif card.type != 0:
                        self.matchned_but_not_rescheduled.append(vocab)
                        logger.info('Card matched but is already learning/due: \t{}, \tcardID: {}'
                                    .format(vocab.encode(self.encoding), card_id)
                                    )

                if self.number_of_replacements == len(self.list_of_vocabs) + 1:
                    break

            else:
                self.unmatched_vocab.append(vocab)
                logger.info('No match found: {}'.format(vocab.encode(self.encoding)))

        mw.reset()
        showInfo('Successfully Rescheduled {} cards\n'
                 'Did not reschedule {} cards because they were either learning or due cards\n'
                 'Unable to find {} cards'.format(self.number_of_replacements,
                                                  len(self.matchned_but_not_rescheduled),
                                                  len(self.unmatched_vocab)
                                                  )
                 )
        self._num_notes_in_deck_lcd.display(self.number_of_notes_in_deck)
        self._num_cards_succ_resch_lcd.display(self.number_of_replacements)
        self._num_cards_found_learning_due_lcd.display(len(self.matchned_but_not_rescheduled))
        self._num_cards_no_matches_lcd.display(len(self.unmatched_vocab))


def init_window():
    mw.texteditor = TextEditor(mw)

run_action = QAction('Push Existing Vocabulary', mw)
run_action.setShortcut(QKeySequence(HOTKEY))
run_action.triggered.connect(init_window)

mw.form.menuTools.addAction(run_action)

# TODO: vvv What's that?
# https://www.python.org/dev/peps/pep-0350/
