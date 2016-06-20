PyMoronBot [![Stories in Ready](https://badge.waffle.io/MatthewCox/PyMoronBot.png?label=ready&title=Ready)](https://waffle.io/MatthewCox/PyMoronBot)
==========

A modular IRC bot with extensive aliasing capabilities, written in Python.

Initially a language port/rewrite of [MoronBot](https://github.com/MatthewCox/MoronBot/) (C#), but now somewhat diverged.

Features
--------
* [Alias](Commands/Alias.py) any of the following to create new commands on-the-fly, and then alias *those* aliases to create even more
* Use [Slurp](Commands/Slurp.py) and [JQ](Commands/JQ.py) to extract data from HTML/XML or JSON
* Use [Sub](Commands/Sub.py) or [Chain](Commands/Chain.py) to link multiple modules together
  * and use [Var](Commands/Var.py) to store data for use within the same command (eg, a URL you want to slurp multiple times)
* [Follows URLs](Commands/URLFollow.py) posted in chat to see where they lead (following all redirects), responding with the page title and final hostname
  * with specialised follows to get extra relevant information from Imgur, KickStarter, Steam, Twitch, Twitter, and YouTube links
* Recognizes [sed-like](Commands/Sed.py) patterns in chat and replaces the most recent match in the last 20 messages
* Also recognizes [`*correction`](Commands/AsterFix.py) style corrections and replaces the most likely candidate word in that user's previous message
* [AutoPasteEE](PostProcesses/AutoPasteEE.py) detects when single responses are longer than ~2 IRC messages, and submit them to paste.ee instead, replacing the response with a link
* Consistent help for any module via the [Help](Commands/Help.py) module
* And many more (take a look in [Commands](Commands) and [PostProcesses](PostProcesses))

All of these features can be individually enabled/disabled by loading or unloading the module that provides them

Installation Instructions
-------------------------
* Install Python 2.6+
* Clone the repo with `git clone https://github.com/MatthewCox/PyMoronBot.git`
* Create a virtualenv to run the bot in, and activate it
* Run `pip install -r requirements.txt` to install all the requirements
* Edit [GlobalVars.py](GlobalVars.py) to set admins, and some less important stuff (this will be changing to a proper config file at some point)

Running the Bot
---------------
Activate your virtualenv, and run `python moronbot.py -s server.address -c \#channel`

You can run `python moronbot.py -h` for help with the command line args
