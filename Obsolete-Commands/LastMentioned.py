# -*- coding: utf-8 -*-
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import subprocess


class Command(CommandInterface):
    triggers = ['lastsaid', 'lastmention', 'lastmentioned']
    help = 'lastmention(ed)/lastsaid <text> - checks the log for the last time someone mentioned a given word or phrase'

    def execute(self, message, bot):
        """
        @type message: IRCMessage
        @type bot: MoronBot
        """
        if len(message.MessageList) > 1 and (message.Command == "lastmention" or message.Command == "lastmentioned"):
            proc = subprocess.Popen(['/usr/bin/php',
                                     '/opt/moronbot/loggrep.php',
                                     "\"" + message.Parameters.replace("\"", "\\\"").replace("\n", "\\\n") + "\"",
                                     message.ReplyTo,
                                     "mention"],
                                    stdout=subprocess.PIPE)
            output = proc.stdout.read()
            return IRCResponse(ResponseType.Say, output, message.ReplyTo)
        if len(message.MessageList) > 1 and message.Command == "lastsaid":
            proc = subprocess.Popen(['/usr/bin/php',
                                     '/opt/moronbot/loggrep.php',
                                     "\"" + message.Parameters.replace("\"", "\\\"").replace("\n", "\\\n") + "\"",
                                     message.ReplyTo,
                                     "mentionnottoday"],
                                    stdout=subprocess.PIPE)
            output = proc.stdout.read()
            return IRCResponse(ResponseType.Say, output, message.ReplyTo)
