# -*- coding: utf-8 -*-

# This file is part of the Push Existing Vocab add-on for Anki
# Copyright: SpencerMAQ (Michael Spencer Quinto) <spencer.michael.q@gmail.com> 2017
# License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html

from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo
from aqt.addons import AddonManager
import os
import sys
import json
import logging

if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
    from functools import lru_cache

try:
    from PyQt4 import QtCore
    _from_utf8 = QtCore.QString.fromUtf8
except (AttributeError, ImportError):
    def _from_utf8(s):
        return s

__version__ = '0.0'
# July 30 2017

HOTKEY = 'Shift+P'
TAG_TO_ADD = 'Rescheduled_by_Push_Existing_Vocab'


# ===================== DO NOT EDIT BEYOND THIS LINE ===================== #
LOG_FORMAT = '%(levelname)s \t| %(asctime)s: \t%(message)s'

addon_mgr_instance = AddonManager(mw)
ADD_ON_PATH = addon_mgr_instance.addonsFolder()
PUSH_EXISTING_PATH = ADD_ON_PATH + r'\push_existing'

if not os.path.exists(PUSH_EXISTING_PATH):
    os.makedirs(PUSH_EXISTING_PATH)
NEW_PATH = os.path.join(ADD_ON_PATH, 'push_existing')
# CONFIG_PATH = os.path.join(NEW_PATH, 'push_existing_config.json')
LOG_PATH = os.path.join(NEW_PATH, 'push_existing.log')

# DEBUG 10 INFO 20 WARNING 30 ERROR 40 CRITICAL 50
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger()

del addon_mgr_instance

# ===================== TEMPORARY STUFF ===================== #
if False:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from anki.storage import Collection

    class Temporary:
        def __init__(self):
            self.col = Collection('', log=True)

    mw = Temporary()

#  ===================== TO_DO_LIST ===================== #
# NOTE : TODO: I would have chosen to do it by decks but there seems to be a problem with the API when using decks
# TODO: maybe this'd work better if you did by note type instead of deck? (or maybe both)
# FIXME: Encoding Problems (only for logging when using UTF-8 With BOM) i.e. UTF-8-SIG
# TODO: Make this app use a QMainWindow by creating a new QApplication instance

# TODO: include functionaly for user to push only CERTAIN CARDS based on the names of the cards (Diffucult)

# TODO: convert the vocab lists into sets to avoid rescheduling the same card twice

# TODO: (IMPORTANT) Json for last saved preferences
# TODO: (IMPORTANT) Show a table of the imported vocab instead of individually

#  ===================== TO_DO_LIST ===================== #


class TextEditor(QDialog):
    def __init__(self, parent):
        """
        Initialize the UI
        :param parent:      global mw from aqt
        """
        # TODO:
        '''
        TESTS:
        Models:                     Passing (Perfect) TODO: Only Show non-empty models
        Field to Match:             Works in response to models
        Num cards to resch:         NONE
        Delim:                      Passing
        Encoding:                   Passing? (Works, garbage logging for SIG)

        Radio (tag):                Passing
        JSON                        Problem for 3 comboboxes
        '''
        super(TextEditor, self).__init__(parent)

        self.matched_vocab                          = []
        self.list_of_vocabs                         = []
        self.unmatched_vocab                        = []
        self.matchned_but_not_rescheduled           = []

        # ===================== COMBOX BOXES ===================== #
        self.selected_deck                          = ''        # TODO: to be filled in by a signal
        self.selected_model                         = ''        # TODO: to be filled in by a signal
        self.field_tomatch                          = ''        # TODO: to be filled in by a signal
        self.number_of_cards_to_resched_per_note    = 1
        self.delimiter                              = '\n'
        # self.delimiter = '\r\n'

        self.enable_add_note_tag                    = True
        self.encoding                               = 'UTF-8'
        self.number_of_notes_in_deck                = 0

        # setWindowTitle is probably a super method from QtGui
        self.setWindowTitle('Push Existing Vocab add-on')

        self._init_buttons()
        self.__init_json()
        self._init_signals()
        self._init_ui()

    def __init_json(self):
        if os.path.isfile(NEW_PATH + r'\push_existing.json'):
            with open(NEW_PATH + r'\push_existing.json', 'r') as fh:
                conf = json.load(fh)

            self.selected_model = conf['default_model']
            self._models_combo.setCurrentIndex(self._models_combo.findText(self.selected_model))

            self._models_combo_changed()
            self.field_tomatch = conf['default_field_to_match']
            self._fields_combo.setCurrentIndex(self._fields_combo.findText(self.field_tomatch))

            self.number_of_cards_to_resched_per_note = conf['default_num_of_cards']
            self._cards_to_resch_combo.setCurrentIndex(self._cards_to_resch_combo
                                                       .findData(self.number_of_cards_to_resched_per_note))

            self.delimiter = conf['default_delimiter']
            self._delimiter_combo.setCurrentIndex(self._delimiter_combo.findText(self.delimiter))

            self.enable_add_note_tag = conf['enable_add_tag']
            if self.enable_add_note_tag:
                self._yes_tagging_radio.toggle()
                # self._no_tagging_radio.setChecked(False)
            else:
                self._no_tagging_radio.toggle()
                # self._yes_tagging_radio.setChecked(False)

            self.encoding = conf['default_encoding']
            self._encoding_combo.setCurrentIndex(self._encoding_combo.findText(self.encoding))

    def _init_buttons(self):
        self.import_btn = QPushButton('Import CSV')
        self.show_contents = QPushButton('Show Contents')
        self.anki_based_reschedule_button = QPushButton('Anki-Based Resched')

        self.open_logfile_button = QPushButton('Open Log')
        self.clear_list = QPushButton('Clear List')

        # ===================== COMBOX BOXES and RADIO ===================== #
        self._models_combo = QComboBox()

        self._models_combo.addItems([model for model in sorted(mw.col.models.allNames())])
        self._models_combo.setCurrentIndex(0)
        self.selected_model = self._models_combo.currentText()

        self._fields_combo = QComboBox()
        # FIXME: Should be automatically filled
        # self._fields_combo.addItems(['Expression_Original_Unedited'])
        # self._fields_combo.setCurrentIndex(0)
        self.field_tomatch = self._fields_combo.currentText()

        self._cards_to_resch_combo = QComboBox()
        self._cards_to_resch_combo.addItems(['1', '2', '3', '4', '5', '6', '7', '8', '9', 'All'])
        self._cards_to_resch_combo.setCurrentIndex(0)
        self.number_of_cards_to_resched_per_note = int(self._cards_to_resch_combo.currentText())

        self._delimiter_combo = QComboBox()
        self._delimiter_combo.addItems(['New Line',
                                        'Tab',
                                        'One Whitespace',
                                        '", "(Comma then space)',
                                        '","(Comma without space)',
                                        '";"(Semicolon without space)',
                                        '"; "(Semicolon with space)']
                                       )
        self._delimiter_combo.setCurrentIndex(0)

        self._encoding_combo = QComboBox()
        self._encoding_combo.addItems(['UTF-8',
                                       'UTF-8-SIG',
                                       'Shift JIS']
                                      )
        self._encoding_combo.setCurrentIndex(0)

        self._yes_tagging_radio = QRadioButton('Yes')
        self._no_tagging_radio = QRadioButton('No')

        # ===================== LCD BOXES ===================== #
        self._num_imported_cards_lcd = QLCDNumber()
        self._num_imported_cards_lcd.setFixedHeight(43)
        self._num_notes_in_deck_lcd = QLCDNumber()
        self._num_notes_in_deck_lcd.setFixedHeight(43)
        self._num_cards_succ_resch_lcd = QLCDNumber()
        self._num_cards_succ_resch_lcd.setFixedHeight(43)
        self._num_cards_found_learning_due_lcd = QLCDNumber()
        self._num_cards_found_learning_due_lcd.setFixedHeight(43)
        self._num_cards_no_matches_lcd = QLCDNumber()
        self._num_cards_no_matches_lcd.setFixedHeight(43)

    def _init_signals(self):
        self.import_btn.clicked.connect(lambda: self.import_csv(self.delimiter, self.encoding))
        self.show_contents.clicked.connect(self.show_contents_signal)
        self.anki_based_reschedule_button.clicked.connect(self.anki_based_reschedule)

        self.open_logfile_button.clicked.connect(self.open_log_file)
        self.clear_list.clicked.connect(self.reset_list)

        # ===================== COMBOX BOXES ===================== #
        self._models_combo.currentIndexChanged.connect(self._models_combo_changed)
        self._fields_combo.currentIndexChanged.connect(self._selected_in_combo)
        # self._cards_to_resch_combo.currentIndexChanged.connect(self._selected_in_combo)
        self._delimiter_combo.currentIndexChanged.connect(self._selected_in_combo)
        self._encoding_combo.currentIndexChanged.connect(self._selected_in_combo)

        self._yes_tagging_radio.toggled.connect(self._enable_disable_tagging)

    def _init_ui(self):
        # ===================== SEPARATORS ===================== #
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

        combo_ver_layout_5 = QVBoxLayout()
        combo_ver_lay5_label = QLabel('Encoding')
        combo_ver_layout_5.addWidget(combo_ver_lay5_label)
        combo_ver_layout_5.addWidget(self._encoding_combo)

        combo_ver_layout_6_radio = QVBoxLayout()
        enable_tagging_label = QLabel('Enable Tagging')
        combo_ver_layout_6_radio.addWidget(enable_tagging_label)

        yes_no_hbox_layout = QHBoxLayout()
        yes_no_hbox_layout.addWidget(self._yes_tagging_radio)
        yes_no_hbox_layout.addWidget(self._no_tagging_radio)
        combo_ver_layout_6_radio.addLayout(yes_no_hbox_layout)

        combo_layout = QHBoxLayout()
        combo_layout.addLayout(combo_ver_layout_1)
        combo_layout.addLayout(combo_ver_layout_2)
        combo_layout.addLayout(combo_ver_layout_3)
        combo_layout.addLayout(combo_ver_layout_4)
        combo_layout.addLayout(combo_ver_layout_5)
        combo_layout.addLayout(combo_ver_layout_6_radio)


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
        # self.setFixedSize(self.size())
        self.setFixedHeight(199)
        self.setFocus()
        self.show()

    def _models_combo_changed(self):
        self._fields_combo.clear()
        self.selected_model = self._models_combo.currentText()

        # NOTE: (IMP!) use index protocol for json objects, dot notation otherwise (DB)
        mid = mw.col.models.byName(self.selected_model)['id']  # model ID
        # showInfo(str(mid))
        nids = mw.col.findNotes('mid:' + str(mid))             # returns a list of noteIds
        try:
            sample_nid = nids[0]
        except IndexError:
            # when nids is an empty list
            showInfo('No Notes found for that Model\n Please select another one')
            return

        __note = mw.col.getNote(sample_nid)
        # showInfo(str(__note.keys()[0]))
        self._fields_combo.addItems([field for field in sorted(__note.keys())])

    def _selected_in_combo(self):
        # FIXME: separate function for each combobox
        self.field_tomatch = self._fields_combo.currentText()
        # self.number_of_cards_to_resched_per_note = int(self._cards_to_resch_combo.currentText())
        # FIXME: should depend on INDEX

        delimiter_dict = {'New Line': '\n',
                          'Tab': '\t',
                          'One Whitespace': ' ',
                          '", "(Comma then space)': ', ',
                          '","(Comma without space)': ',',
                          '";"(Semicolon without space)': ';',
                          '"; "(Semicolon with space)': '; '
                          }
        self.delimiter = delimiter_dict[self._delimiter_combo.currentText()]

        self.encoding = self._encoding_combo.currentText()

    def _enable_disable_tagging(self):
        if self._yes_tagging_radio.isChecked():
            self.enable_add_note_tag = True
        else:
            self.enable_add_note_tag = False

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
            open(LOG_PATH)

        elif sys.version_info[0] == 2:
            os.startfile(LOG_PATH)

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
        # self.field_tomatch = 'Expression_Original_Unedited'
        # self.selected_model = 'Japanese-1b811 example_sentences'

        self.number_of_replacements = 0
        self.reset_list()

        try:
            mid = mw.col.models.byName(self.selected_model)['id']       # model ID
        except TypeError:
            showInfo('Please Choose a Note Type First')
            return

        if not self.field_tomatch:
            showInfo('Please Select a Field to Match first')
            return

        nids = mw.col.findNotes('mid:' + str(mid))                  # returns a list of noteIds

        logger.info('=================================================================\n'
                    'Version {}\n'.format(__version__) +
                    'Imported from CSV: \t' +
                    ', '.join(vocab.encode(self.encoding) for vocab in self.list_of_vocabs)
                    # ', '.join(vocab for vocab in self.list_of_vocabs)
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

    def closeEvent(self, QCloseEvent):
        # https: // stackoverflow.com / questions / 14834494 / pyqt - clicking - x - doesnt - trigger - closeevent
        # FIXME: Create a Yes or No Prompt, # Yes = override json, # No = preserve json

        reply = QMessageBox.question(self, 'Prompt', 'Would you like to save your settings?',
                                     QMessageBox.Yes, QMessageBox.No)

        conf = {'default_model':            self.selected_model,
                'default_field_to_match':   self.field_tomatch,
                'default_num_of_cards':     self.number_of_cards_to_resched_per_note,
                'default_delimiter':        self.delimiter,
                'enable_add_tag':           self.enable_add_note_tag,
                'default_encoding':         self.encoding
                }

        if reply == QMessageBox.Yes:
            with open(NEW_PATH + r'\push_existing.json', mode='w') as fh:
                json.dump(conf,
                          fh,
                          indent=4,
                          separators=(',', ': ')
                          )


def init_window():
    mw.texteditor = TextEditor(mw)

run_action = QAction('Push Existing Vocabulary', mw)
run_action.setShortcut(QKeySequence(HOTKEY))
run_action.triggered.connect(init_window)

mw.form.menuTools.addAction(run_action)
