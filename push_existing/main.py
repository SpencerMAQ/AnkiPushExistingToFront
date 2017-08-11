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

from .utils import setup_logger
from .utils import calculate_time
from .utils import open_log_file
from .utils import trace_calls

if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
    from functools import lru_cache

try:
    from PyQt4 import QtCore
    _from_utf8 = QtCore.QString.fromUtf8
except (AttributeError, ImportError):
    def _from_utf8(s):
        return s

__version__ = '0.0'
# Aug 1 2017

HOTKEY = 'Shift+P'
TAG_TO_ADD = 'Rescheduled_by_Push_Existing_Vocab'


# ===================== DO NOT EDIT BEYOND THIS LINE ===================== #
UNMATCHED_FORMAT = logging.Formatter('%(message)s')

addon_mgr_instance = AddonManager(mw)
ADD_ON_PATH = addon_mgr_instance.addonsFolder()
PUSH_EXISTING_PATH = ADD_ON_PATH + r'\push_existing'

if not os.path.exists(PUSH_EXISTING_PATH):
    os.makedirs(PUSH_EXISTING_PATH)
NEW_PATH = os.path.join(ADD_ON_PATH, 'push_existing')

CONFIG_PATH = os.path.join(NEW_PATH, 'push_existing_config.json')   # doesn't work on json?? but works for log
LOG_PATH = os.path.join(NEW_PATH, 'push_existing.log')
UNMATCHED_LOG_PATH = os.path.join(NEW_PATH, 'unmatched_vocab.log')

main_logger = setup_logger('main_logger', LOG_PATH)
unmatched_logger = setup_logger('unmatched_logger', UNMATCHED_LOG_PATH, _format=UNMATCHED_FORMAT)

del addon_mgr_instance

DELIMITER_DICT = {'New Line':                       '\n',
                  'Tab':                            '\t',
                  'One Whitespace':                 ' ',
                  '", "(Comma then space)':         ', ',
                  '","(Comma without space)':       ',',
                  '";"(Semicolon without space)':   ';',
                  '"; "(Semicolon with space)':     '; '
                  }


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

# TODO: Make this app use a QMainWindow by creating a new QApplication instance (IMPORTANT!)

# TODO: include functionality for user to push only CERTAIN CARDS based on the NAMES of the cards (Difficult)
# TODO: convert the vocab lists into sets to avoid rescheduling the same card twice
# TODO: use generators instead of list comprehensions where possible
# TODO: Only Show non-empty models

# TODO: Separate functions for updating LCD values and delim, radio, encoding based on their actual values
# TODO: (IMPORTANT) Use dictionary get method instead of index lookup to avoid key errors
# TODO: (IMPORTANT) Not working for Shift JIS
# TODO: (IMPORTANT) Show a table of the imported vocab instead of individually
# TODO: (IMPORTANT) Test for schedule-buried and user buried cards
# TODO: FFS Choose a better name for you add-on (Push Cards that Match a Field)

# TODO: split this module into different modules (separate for preferences, similar to yomi)

#  ===================== TO_DO_LIST ===================== #



class PushCards(QDialog):
    def __init__(self, parent):
        """Initialize the UI

        Args:
            parent:     mw
        """
        super(PushCards, self).__init__(parent)

        self.matched_vocab                          = []
        self.list_of_vocabs_from_csv                = []
        self.unmatched_vocab                        = []
        self.matched_but_not_rescheduled            = []

        # ===================== COMBOBOX BOXES ===================== #
        self.selected_deck                          = ''
        self.selected_model                         = ''
        self.field_to_match                         = ''
        self.number_of_cards_to_resched_per_note    = 1
        self.delimiter                              = '\n'
        self.preferred_csv_directory                = ''

        self.enable_add_note_tag                    = True
        self.encoding                               = 'UTF-8'
        self.number_of_notes_in_deck                = 0

        # setWindowTitle is probably a super method from QtGui
        self.setWindowTitle('Push Existing Vocab Add-On')

        self._init_buttons()
        self._init_json()
        self._init_signals()
        self._init_ui()


    @trace_calls
    def _init_json(self):
        """
        Initialize settings if a JSON file exists

        Nested if statements are inside the with context
        Each of which calls _models_combo_changed, then _fields_combo_changed
        to update the contents of the ComboBoxes and change the currentIndex
        based on the contents of the JSON file

        The Delimiter stored inside the JSON file is not the actual delimiter but is the key
        The actual delimiter is found through lookup on the global dict DELIMITER_DICT
        The actual delimiter is used by self.delimiter
        Only the key is displayed however, not the actual delimiter (for ease of use)
        """
        if os.path.isfile(NEW_PATH + r'\push_existing.json'):
            with open(NEW_PATH + r'\push_existing.json', 'r') as fh:
                conf = json.load(fh)

            self.selected_model = conf.get('default_model')
            self._models_combo.setCurrentIndex(self._models_combo.findText(self.selected_model))

            if self.selected_model:
                self._on_models_combo_index_changed()
                self.field_to_match = conf.get('default_field_to_match')
                self._fields_combo.setCurrentIndex(self._fields_combo.findText(self.field_to_match))

                if self.field_to_match:
                    self._on_fields_combo_index_changed()
                    self.number_of_cards_to_resched_per_note = conf.get('default_num_of_cards', 1)
                    self._cards_to_resch_combo.setCurrentIndex(self._cards_to_resch_combo
                                                               .findText(str(self.
                                                                             number_of_cards_to_resched_per_note)
                                                                         )
                                                               )

            __delimiter_ = conf.get('default_delimiter', 'New Line')
            if __delimiter_:
                self.delimiter = DELIMITER_DICT[__delimiter_]
                self._delimiter_combo.setCurrentIndex(self._delimiter_combo.findText(__delimiter_))

            self.enable_add_note_tag = conf.get('enable_add_tag', True)
            if self.enable_add_note_tag:
                self._yes_tagging_radio.toggle()
            else:
                self._no_tagging_radio.toggle()

            self.encoding = conf.get('default_encoding', 'UTF-8')
            self._encoding_combo.setCurrentIndex(self._encoding_combo.findText(self.encoding))

            self.preferred_csv_directory = conf.get('preferred_csv_loc')
        else:
            self.enable_add_note_tag = True
            self._yes_tagging_radio.toggle()


    def _init_buttons(self):
        """QtGui/QtWidget elements"""
        self.import_btn                     = QPushButton('Import CSV')
        self.show_contents                  = QPushButton('Show Contents')
        self.anki_based_reschedule_button   = QPushButton('Anki-Based Resched')

        self.open_unmatched_log_button      = QPushButton('Open Unmatched CSV')
        self.open_logfile_button            = QPushButton('Open Report Log')
        self.clear_list                     = QPushButton('Clear List')

        # ===================== COMBOBOX BOXES and RADIO ===================== #
        self._models_combo = QComboBox()

        self._models_combo.addItems([model for model in sorted(mw.col.models.allNames())])
        self._models_combo.setCurrentIndex(0)
        self.selected_model = self._models_combo.currentText()

        self._fields_combo = QComboBox()
        # self._fields_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self._fields_combo.setMinimumWidth(236)
        self.field_to_match = self._fields_combo.currentText()

        self._cards_to_resch_combo = QComboBox()

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
                                       'Shift-JIS']
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
        self.show_contents.clicked.connect(lambda: self.on_show_contents_clicked())
        self.anki_based_reschedule_button.clicked.connect(lambda: self.anki_based_reschedule())

        self.open_unmatched_log_button.clicked.connect(lambda: open_log_file(path=UNMATCHED_LOG_PATH))
        self.open_logfile_button.clicked.connect(lambda: open_log_file(path=LOG_PATH))
        self.clear_list.clicked.connect(lambda: self.reset_list())

        # ===================== COMBOBOX BOXES ===================== #
        self._models_combo.currentIndexChanged.connect(
            lambda: self._on_models_combo_index_changed(sender=self._models_combo))
        self._fields_combo.currentIndexChanged.connect(lambda: self._on_fields_combo_index_changed())
        self._cards_to_resch_combo.currentIndexChanged.connect(lambda: self._on_cards_to_resch_combo_index_changed())
        self._delimiter_combo.currentIndexChanged.connect(lambda: self._on_delimiter_combo_index_changed())
        self._encoding_combo.currentIndexChanged.connect(lambda: self._on_encoding_combo_index_changed())
        self._yes_tagging_radio.toggled.connect(lambda: self._enable_disable_tagging())


    def _init_ui(self):
        """Initialize Layout"""
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
        combo_ver_lay2_label = QLabel('Field to Match (Choose Model First)')
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
        ver_layout_1_label = QLabel('Imported from CSV')
        lcd_ver_layout_1.addWidget(ver_layout_1_label)
        lcd_ver_layout_1.addWidget(self._num_imported_cards_lcd)

        lcd_ver_layout_2 = QVBoxLayout()
        ver_layout_2_label = QLabel('Notes in Model')
        lcd_ver_layout_2.addWidget(ver_layout_2_label)
        lcd_ver_layout_2.addWidget(self._num_notes_in_deck_lcd)

        lcd_ver_layout_3 = QVBoxLayout()
        ver_layout_3_label = QLabel('Unsuspended + Rescheduled')
        lcd_ver_layout_3.addWidget(ver_layout_3_label)
        lcd_ver_layout_3.addWidget(self._num_cards_succ_resch_lcd)

        lcd_ver_layout_4 = QVBoxLayout()
        ver_layout_4_label = QLabel('Already Learning/Due')
        lcd_ver_layout_4.addWidget(ver_layout_4_label)
        lcd_ver_layout_4.addWidget(self._num_cards_found_learning_due_lcd)

        lcd_ver_layout_5 = QVBoxLayout()
        ver_layout_5_label = QLabel('No Matches Found')
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
        h_layout.addWidget(self.import_btn)
        h_layout.addWidget(self.show_contents)
        h_layout.addWidget(self.anki_based_reschedule_button)

        h_layout.addWidget(self.open_unmatched_log_button)
        h_layout.addWidget(self.open_logfile_button)
        h_layout.addWidget(self.clear_list)

        v_layout.addWidget(separator2)
        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)
        # self.setFixedSize(self.size())
        self.setFixedHeight(199)
        self.setFocus()
        self.show()


    @trace_calls
    def _on_models_combo_index_changed(self, sender=None):
        """Clears the fields QComboBox everytime the Index is changed (currentIndexChanged),
        This clear is necessary so that the 'fields' ComboBox isn't adding fields indefinitely
        everytime the 'models' ComboBox index changes

        It then fills the 'fields' ComboBox based on the selected model: self._models_combo.currentText()

        Aside from being called everytime the Model ComboBox index changes
        This function is also used inside __init_json to populate the Models ComboBox
        on initialization if the JSON file exists

        Args:
            sender:         None by default, self._models_combo as sent from signal (lambda)
        """
        self._fields_combo.clear()
        self.selected_model = self._models_combo.currentText()

        # NOTE: (IMP!) use index protocol for json objects, dot notation otherwise (DB)
        __mid = mw.col.models.byName(self.selected_model)['id']     # model ID
        __nids = mw.col.findNotes('mid:' + str(__mid))              # returns a list of noteIds

        try:
            # stored as attribute in order to be used by _fields combo changed to update No. of cards combobox
            self.__sample_nid = __nids[0]
        except IndexError:
            # when nids is an empty list
            if sender == self._models_combo:
                # only shown when the user himself changes the index of _models_combo
                showInfo('No Notes found for that Model\n Please select another one')
            return

        __note = mw.col.getNote(self.__sample_nid)
        self._fields_combo.addItems([field for field in sorted(__note.keys())])


    @trace_calls
    def _on_fields_combo_index_changed(self):
        """
        Clears the _cards_to_resch_combo ComboBox everytime it is called
        This clear is to ensure that its contents are only populated
        depending on the corresponding field to it

        The function then proceeds to get a list of card IDs
        based on the attribute self.__sample_nid obtained from self._models_combo_changed

        The card IDs are stored in a variable __cids
        A list comprehension is then made depending on the length of that list
        if len(list) = 1, the comboBox would be populate by only one option: 1
        if len(list) = 2, two options: 1, 2 and so on

        The default value however (and the display) is set to the first index, value: 1
        i.e. unless the user explicitly tells it not to
        at which point, the function _cards_to_resch_combo_changed is called
        """
        self._cards_to_resch_combo.clear()
        self.field_to_match = self._fields_combo.currentText()

        __cids = mw.col.findCards('nid:' + str(self.__sample_nid))
        self._cards_to_resch_combo.addItems([str(num+1) for num in range(len(__cids))])
        self._cards_to_resch_combo.setCurrentIndex(0)
        self.number_of_cards_to_resched_per_note = 1


    @trace_calls
    def _on_delimiter_combo_index_changed(self):
        """
        Looks up the actual delimiter from the global DELIMITER_DICT
        based on the currentText of self._delimiter_combo
        """
        self.delimiter = DELIMITER_DICT[self._delimiter_combo.currentText()]


    @trace_calls
    def _on_encoding_combo_index_changed(self):
        self.encoding = self._encoding_combo.currentText()


    @trace_calls
    def _on_cards_to_resch_combo_index_changed(self):
        self.number_of_cards_to_resched_per_note = self._cards_to_resch_combo.currentText()


    @trace_calls
    def _enable_disable_tagging(self):
        if self._yes_tagging_radio.isChecked():
            self.enable_add_note_tag = True
        else:
            self.enable_add_note_tag = False


    @trace_calls
    def import_csv(self, delimiter, encoding):
        """Import a DSV File with special provisions based on encoding
        Do note the difference between 'utf-8-sig' (with BOM) and 'utf-8'

        Args:
            delimiter:      New Line by default (sent by signal)
            encoding:       UTF-8 by default (sent by signal)
        """

        filename = QFileDialog.getOpenFileName(self,
                                               'Open CSV',
                                               self.preferred_csv_directory if self.preferred_csv_directory
                                               else os.getenv('HOME'),
                                               'TXT(*.csv *.txt)'
                                               )

        if filename:
            self.reset_list()
            del self.list_of_vocabs_from_csv[:]
            self.preferred_csv_directory = os.path.abspath(filename)

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

        if filename and self.list_of_vocabs_from_csv:
            self.reset_lcd_display()
            showInfo('Successfully Imported {} lines from CSV'.format(len(self.list_of_vocabs_from_csv)))
            self._num_imported_cards_lcd.display(len(self.list_of_vocabs_from_csv))
        elif not filename and self.list_of_vocabs_from_csv:
            showInfo('Nothing Imported\nThe contents of your previous import are retained')
        else:
            showInfo('Nothing Imported')


    def __read_files(self, _file, delimiter):
        """It's annoying that I have to define a new method
        Just because it won't recognize self inside the nested function

        Args:
            _file:          sent by import_csv
            delimiter:      sent by import_csv
        """
        contents = _file.read()       # could use readlines but I'm not sure that the vocabs are separated by newlines
        csvreader = contents.split(delimiter)

        for line in csvreader:
            self.list_of_vocabs_from_csv.append(line.strip('\r'))

            # for line in file:
            #     self.list_of_vocabs.append(line)

    @trace_calls
    def on_show_contents_clicked(self):
        # FiXME: Should show the entire table, not one by one
        list_of_vocabs = self.list_of_vocabs_from_csv

        if not list_of_vocabs:
            showInfo('The list is empty')

        try:
            showInfo(_from_utf8(*list_of_vocabs))
        except Exception as e:
            for i, vocab in enumerate(list_of_vocabs):
                showInfo(_from_utf8(vocab))
                if i == 2:
                    # Show only a few of the contents for verification
                    break
                # raise


    @trace_calls
    def reset_list(self):
        """
        Primarily used as an event in response to the button
        Used in other methods as well (import csv and resched)
        to ensure that the lists they need are empty
        """
        del self.matched_vocab[:]
        del self.unmatched_vocab[:]
        del self.matched_but_not_rescheduled[:]
        sender = self.sender()

        if sender.text() == 'Clear List':
            del self.list_of_vocabs_from_csv[:]
            showInfo('Successfully reset the list of cards\n'
                     'Please import a text file to fill the list again')
            self.reset_lcd_display()


    @trace_calls
    def reset_lcd_display(self):
        self._num_imported_cards_lcd.display(0)
        self._num_notes_in_deck_lcd.display(0)
        self._num_cards_succ_resch_lcd.display(0)
        self._num_cards_found_learning_due_lcd.display(0)
        self._num_cards_no_matches_lcd.display(0)


    # NOTE: this seems to be slower than my original function
    @trace_calls
    @calculate_time
    def anki_based_reschedule(self):
        """
        Main function of the program
        Checks every Note > Field if it is inside the
        list of mined words and sets the due date to zero accdngly
        Version 3: same as version 2 except this one uses built-in Anki modules
        """

        __number_of_replacements = 0
        self.reset_list()        # if sender is not a signal, only reset the container for others except vocab

        try:
            mid = mw.col.models.byName(self.selected_model)['id']       # model ID
        except TypeError:
            showInfo('Please Choose a Note Type First')
            return

        if not self.field_to_match:
            showInfo('Please Select a Field to Match first')
            return

        if not self.list_of_vocabs_from_csv:
            showInfo('The List is empty\n'
                     'Please Import a File before clicking this button')
            return

        nids = mw.col.findNotes('mid:' + str(mid))                      # returns a list of noteIds
        dict_of_note_first_fields = {
            mw.col.getNote(note_id)[self.field_to_match].strip().strip('<span>').strip('</span>'): note_id
            for note_id in nids
            }

        list_of_deck_vocabs_20k = dict_of_note_first_fields.keys()

        if not list_of_deck_vocabs_20k:
            showInfo('The model {} contains no notes\n'
                     'Please try a new note type'.format(self.selected_model)
                     )
            return

        # For LCD Display
        self.number_of_notes_in_deck = len(list_of_deck_vocabs_20k)

        # Place in try except for UnicodeEncodeError because self.selected_model can sometimes be unicode
        try:
            main_logger.info('=================================================================\n'
                             'Version {}\n'.format(__version__) +
                             'Imported from CSV: \t' +
                             ', '.join(vocab.encode('UTF-8') for vocab in self.list_of_vocabs_from_csv) +
                             '\t From Model: {}\t with encoding: {}'
                             .format(self.selected_model, self.encoding)
                             )
        except UnicodeEncodeError:
            main_logger.info('=================================================================\n'
                             'Version {}\n'.format(__version__) +
                             'Imported from CSV: \t' +
                             ', '.join(vocab.encode('UTF-8') for vocab in self.list_of_vocabs_from_csv) +
                             '\t From Model: {}\t with encoding: {}'
                             .format(self.selected_model.encode('UTF-8'), self.encoding)
                             )

        for vocab in self.list_of_vocabs_from_csv:
            if vocab.strip() in list_of_deck_vocabs_20k:
                nid = dict_of_note_first_fields[vocab.strip()]
                cids = mw.col.findCards('nid:' + str(nid))

                # num of cards to resched per note (default = 1), ensures only the cards specified are rescheduled
                number_of_cards_to_resched_ctr = 0
                for card_id in cids:
                    number_of_cards_to_resched_ctr += 1

                    # ensures only the cards specified are rescheduled
                    if number_of_cards_to_resched_ctr >= int(self.number_of_cards_to_resched_per_note) + 1:
                        break

                    card = mw.col.getCard(card_id)

                    if card.type == 0 or card.queue == -1 or card.queue == -2 or card.queue == -3:
                        self.matched_vocab.append(vocab)
                        __number_of_replacements += 1

                        mw.col.sched.unsuspendCards([card_id])
                        # set the due to be next to the previous due, avoiding cards having the same due(exc if siblngs)
                        mw.col.sched.sortCards([card_id], start=__number_of_replacements, step=1)   # resched

                        main_logger.info('Rescheduled card: {} with cardID: \t{}'
                                         .format(vocab.encode('UTF-8'), card_id))

                        if self.enable_add_note_tag:
                            n = card.note()
                            n.addTag(TAG_TO_ADD)
                            # "If fields or tags have changed, write changes to disk."
                            n.flush()

                    elif card.type != 0:
                        self.matched_but_not_rescheduled.append(vocab)
                        main_logger.info('Card matched but is already learning/due: \t{}, \tcardID: {}'
                                         .format(vocab.encode('UTF-8'), card_id))

                # Just to ensure that it doesn't reschedule more than the vocab count, also reduces load on comp
                if __number_of_replacements == len(self.list_of_vocabs_from_csv) + 1:
                    break

            else:
                self.unmatched_vocab.append(vocab)
                main_logger.info('No match found: {}'.format(vocab.encode('UTF-8')))

        '''
        Appends unmatched vocabs to a log file which the user can then use to
        create cards through on other software such as Rikai or Yomi
        This block works even if the file contains nothing
        Only adds unique items
        '''
        if self.unmatched_vocab:
            with open(UNMATCHED_LOG_PATH, mode='r') as __file:
                # The log file is UTF-8 by default, so I need to do i.decode(self.encoding)
                lines_from_file = [i.decode("UTF-8").encode('UTF-8').strip()
                                   for i in __file.readlines()
                                   ]

                for i in self.unmatched_vocab:
                    if i.encode('UTF-8').strip() not in lines_from_file:
                        unmatched_logger.info('{}'.format(i.encode('UTF-8')))

        mw.reset()
        showInfo('Successfully Rescheduled {} cards\n'
                 'Did not reschedule {} cards because they were either learning or due cards\n'
                 'Unable to find {} cards'.format(__number_of_replacements,
                                                  len(self.matched_but_not_rescheduled),
                                                  len(self.unmatched_vocab)
                                                  )
                 )
        self._num_notes_in_deck_lcd.display(self.number_of_notes_in_deck)
        self._num_cards_succ_resch_lcd.display(__number_of_replacements)
        self._num_cards_found_learning_due_lcd.display(len(self.matched_but_not_rescheduled))
        self._num_cards_no_matches_lcd.display(len(self.unmatched_vocab))


    @trace_calls
    def closeEvent(self, QCloseEvent):
        """Creates a JSON file if it doesn't exist
        Otherwise, saves the QComboBox and QRadioButton settings

        Due to difficulties in lookup when dealing with delimiters such as \n or \t
        the __delimiter stored inside the JSON file is based
        on a reverse lookup an a global dictionary DELIMITER_DICT

        On initialization, __init_json looks for the actual delimiter based on the key
        which was based on reverse lookup

        Skips the Yes/No Prompt if the settings are the same as the JSON file

        Args:
            QCloseEvent:        I have no idea what this is
        """
        # https://stackoverflow.com/questions/2568673/inverse-dictionary-lookup-in-python
        __delimiter = next(key for key, value in DELIMITER_DICT.items() if value == self.delimiter) \
            if self.delimiter else ''

        conf = {'default_model':            self.selected_model,
                'default_field_to_match':   self.field_to_match,
                'default_num_of_cards':     self.number_of_cards_to_resched_per_note,
                'default_delimiter':        __delimiter,
                'enable_add_tag':           self.enable_add_note_tag,
                'default_encoding':         self.encoding,
                'preferred_csv_loc':        self.preferred_csv_directory
                }

        '''Skip prompt if the settings are the same, but check first if it exists to avoid IOError'''
        if os.path.isfile(NEW_PATH + r'\push_existing.json'):
            with open(NEW_PATH + r'\push_existing.json', mode='r') as __hf:
                __fnoc = json.load(__hf)
                if all([__fnoc[key] == conf[key] for key, value in conf.items()]):
                    return

        # https://stackoverflow.com/questions/14834494/pyqt-clicking-x-doesnt-trigger-closeevent
        reply = QMessageBox.question(self, 'Save Settings',
                                     'Would you like to save your config settings?\n'
                                     'Click \'No\' to retain your previous settings',
                                     QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            with open(NEW_PATH + r'\push_existing.json', mode='w') as fh:
                json.dump(conf,
                          fh,
                          indent=4,
                          separators=(',', ': ')
                          )


    def __repr__(self):
        return 'PushCards(matched vocab = {},' \
               'list_of_vocabs_from_csv = {},' \
               'unmatched_vocab = {},' \
               'matched_but_not_rescheduled = {},' \
               'selected_deck = {},' \
               'selected_model = {}, ' \
               'field_to_match = {},' \
               'number_of_cards_to_resched_per_note = {},' \
               'delimiter = {},' \
               'preferred_csv_directory = {},' \
               'enable_add_note_tag = {},' \
               'encoding = {},' \
               'number_of_notes_in_deck = {})'.format(self.matched_vocab,
                                                      self.list_of_vocabs_from_csv,
                                                      self.unmatched_vocab,
                                                      self.matched_but_not_rescheduled,
                                                      self.selected_deck,
                                                      self.selected_model,
                                                      self.field_to_match,
                                                      self.number_of_cards_to_resched_per_note,
                                                      self.delimiter,
                                                      self.preferred_csv_directory,
                                                      self.enable_add_note_tag,
                                                      self.encoding,
                                                      self.number_of_notes_in_deck
                                                      )


    def __str__(self):
        return 'Just check the .json file'



def init_window():
    mw.push_cards = PushCards(mw)

run_action = QAction('Push Existing Vocabulary', mw)
run_action.setShortcut(QKeySequence(HOTKEY))
run_action.triggered.connect(init_window)

mw.form.menuTools.addAction(run_action)
