# -*- coding: utf-8 -*-

"""
Anki Add-on: Push Existing Vocab
Copyright: (c) SpencerMAQ 2016-2017
License: GNU AGPL, version 3 or later; https://www.gnu.org/licenses/agpl-3.0.en.html
"""

# possibilities:
# suspended, due, new, learn, review, buried
# if the card exists and is already due, do not chat its due

# if the card exists and is suspended and due, create notification


## Generate General notification of the cards that were modified, what happened

import push_existing.main