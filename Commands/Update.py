# -*- coding: utf-8 -*-
"""
Created on Dec 07, 2013

@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import subprocess
import os
import sys

class Update(CommandInterface):
    triggers = ['update', 'updatelibs']
    
    def help(self, message):
        """
        @type message: IRCMessage
        """
        helpDict = {
            u"update": u"update - pulls the latest code from GitHub",
            u"updatelibs": u"updatelibs - updates the libraries used by the bot (not implemented yet, does the same as update)"}
            
        command = message.ParameterList[0].lower()
        if command in helpDict:
            return helpDict[command]

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if not self.checkPermissions(message):
            return IRCResponse(ResponseType.Say, 'Only my admins can update me', message.ReplyTo)
        
        subprocess.check_call(['git', 'fetch'])

        output = subprocess.check_output(['git', 'log', '--no-merges',
                                          '--pretty=format:%s %b', '..origin/master'])
        changes = [s.strip().decode('utf-8', 'ignore') for s in output.splitlines()]

        if len(changes) == 0:
            return IRCResponse(ResponseType.Say, 'The bot is already up to date', message.ReplyTo)

        changes = list(reversed(changes))
        response = u'New commits: {}'.format(u' | '.join(changes))

        returnCode = subprocess.check_call(['git', 'merge', 'origin/master'])

        if returnCode != 0:
            return IRCResponse(ResponseType.Say,
                               'Merge after update failed, please merge manually',
                               message.ReplyTo)

        try:
            subprocess.check_call([os.path.join(os.path.dirname(sys.executable), 'pip'),
                                   'install', '-r', 'requirements.txt', '-U'])
        except OSError:
            print('pip not found, requirements not updated')
        
        return IRCResponse(ResponseType.Say,
                           response,
                           message.ReplyTo)
