# -*- coding: utf-8 -*-
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import subprocess


class Command(CommandInterface):
    triggers = ['lastseen', 'lastsaw']
    help = 'lastseen/lastsaw <nick> - finds a nick\'s last message'

    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        if len(message.MessageList) > 1 and message.Command == "lastseen":
            proc = subprocess.Popen(['/usr/bin/php',
                                     '/opt/moronbot/loggrep.php',
                                     message.ParameterList[0],
                                     message.ReplyTo],
                                    stdout=subprocess.PIPE)
            output = proc.stdout.read()
            return IRCResponse(ResponseType.Say, output, message.ReplyTo)
        if len(message.MessageList) > 1 and message.Command == "lastsaw":
            proc = subprocess.Popen(['/usr/bin/php',
                                     '/opt/moronbot/loggrep.php',
                                     message.ParameterList[0],
                                     message.ReplyTo,
                                     "sawed"],
                                    stdout=subprocess.PIPE)
            output = proc.stdout.read()
            return IRCResponse(ResponseType.Say, output, message.ReplyTo)
