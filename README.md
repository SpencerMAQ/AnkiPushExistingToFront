# AnkiPushExistingToFront  

![AnkiPush](http://i.imgur.com/SSzm1mn.png)

An Anki add-on that reschedules `(due=0)` cards that match CSV lines.
I wrote this add-on as an exercise and because I couldn't find any plugin with this functionality in mind. 
My intention is to use this plugin to push existing cards from my deck (which contains more than 20k cards) based on a newline-separated
list of vocabs I've mined from different sources.

## How to Use  
1. Clone/Download the repository from [here](https://github.com/SpencerMAQ/AnkiPushExistingToFront/archive/master.zip)
2. Copy `Push_Existing_Vocab.py` and `push_existing` into `~\Documents\Anki\addons\`
3. You can customize some of the code inside `push_existing\main.py` [here](/push_existing/main.py) 

Basically, the only part that's user-friendly to edit is this part of the code:    　
```py
HOTKEY = 'Shift+P'  
TAG_TO_ADD = 'Rescheduled_by_Push_Existing_Vocab'
```   
4. You can manually set the settings of the plugin inside `push_existing\push_existing.json`  

## Suggestions, Bugs, Requests　
Simply Open an issue and I'll see if I can do it.   

## [License](LICENSE)

---

# 日本語(カードを正面に押す)
このadd-onは、ＣＳＶファイルから特定のCSVラインに一致するカードのスケジュールを変更します。

## 使い方  
1. [ここ](https://github.com/SpencerMAQ/AnkiPushExistingToFront/tree/master)から、レポをクローンしてください。
2. `Push_Existing_Vocab.py` と `push_existing` を　`~\Documents\Anki\addons\`　へコピーして。
3. `push_existing\main.py` から、いくつかのコードをカスタマイズことができる。  

簡単に編集してコードはこれだけです：    
```py
HOTKEY = 'Shift+P'  
TAG_TO_ADD = 'Rescheduled_by_Push_Existing_Vocab'
```
4. `push_existing\push_existing.json` から、自分で設定を変更することができます。


## 提案、バグ、要求  
ただ問題を開けて。それをすることができるかどうか試してみて。  

