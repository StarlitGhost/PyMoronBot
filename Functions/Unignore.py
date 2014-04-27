'''
Created on Dec 01, 2013

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import GlobalVars
from Data import ignores

import re

class Instantiate(Function):
    Help = 'unignore <user> - remove the specified user from the ignore list'

    def __init__(self):
        if ignores.ignoreList is None:
            ignores.loadList()

    def __del__(self):
        if ignores.ignoreList is not None and 'Ignore' not in GlobalVars.functions:
            ignores.ignoreList = None

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^unignore$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say, 'Only my admins can edit the ignore list', message.ReplyTo)

        if len(message.ParameterList) > 0:
            for user in message.ParameterList:
                if user.lower() in ignores.ignoreList:
                    ignores.ignoreList.remove(user.lower())

            ignores.saveList()
                
            output = 'No longer ignoring user(s) {0}'.format(', '.join(message.ParameterList))

            return IRCResponse(ResponseType.Say, output, message.ReplyTo)

        else:
            return IRCResponse(ResponseType.Say, self.Help, message.ReplyTo)

