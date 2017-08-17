# AnkiPushExistingToFront

An Anki add-on that reschedules `(due=0)` cards that match CSV lines.
I wrote this add-on as an exercise and because I couldn't find any plugin with this functionality in mind. 
My intention is to use this plugin to push existing cards from my deck (which contains more than 20k cards) based on a newline-separated
list of vocabs I've mined from different sources.

# How to Use
1. Clone/Download the repository from [here](https://github.com/SpencerMAQ/AnkiPushExistingToFront/tree/master)
2. Copy `Push_Existing_Vocab.py` and `push_existing` into `~\Documents\Anki\addons\`
3. You can customize some of the code inside `push_existing\main.py`
Basically, the only part that's user-friendly to edit is this part of the code:  

    HOTKEY = 'Shift+P'  
    TAG_TO_ADD = 'Rescheduled_by_Push_Existing_Vocab'
    
4. You can manually set the settings of the plugin inside `push_existing\push_existing.json`

# Suggestions, Bugs, Requests
Simply Open an issue and I'll see if I can do it.
