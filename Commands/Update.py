# -*- coding: utf-8 -*-
"""
Created on Dec 07, 2013

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars

import re

import subprocess


class Update(CommandInterface):
    triggers = ['update']
    help = "update - pulls the latest code from GitHub"

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins can update me', message.ReplyTo)

        subprocess.call(['git', 'fetch'])

        output = subprocess.check_output(['git', 'whatchanged', '..origin/master'])
        changes = re.findall('\n\n\s{4}(.+?)\n\n', output)
        
        if len(changes) == 0:
            return IRCResponse(ResponseType.Say, 'The bot is already up to date', message.ReplyTo)

        changes = list(reversed(changes))
        response = 'New Commits: ' + ' | '.join(changes)

        subprocess.call(['git', 'pull'])
        
        return IRCResponse(ResponseType.Say,
                           response,
                           message.ReplyTo)
