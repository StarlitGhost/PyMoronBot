# -*- coding: utf-8 -*-
"""
Created on Dec 07, 2013

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand, admin
from zope.interface import implementer

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

import subprocess
import os
import sys


@implementer(IPlugin, IModule)
class Update(BotCommand):
    def triggers(self):
        return ['update', 'fullupdate']
    
    def help(self, query):
        """
        @type query: list[str]
        """
        helpDict = {
            u"update": u"update - pulls the latest code from GitHub",
            u"fullupdate": u"updatelibs - updates the libraries used by the bot (not implemented yet, does the same as update)"}
            
        command = query[0].lower()
        if command in helpDict:
            return helpDict[command]

    @admin
    def execute(self, message):
        """
        @type message: IRCMessage
        """
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

        if message.Command.lower() == 'fullupdate':
            try:
                subprocess.check_call([os.path.join(os.path.dirname(sys.executable), 'pip'),
                                       'install', '-r', 'requirements.txt'])
            except OSError:
                response += ' | pip not found, requirements not updated'
        
        return IRCResponse(ResponseType.Say,
                           response,
                           message.ReplyTo)


update = Update()
