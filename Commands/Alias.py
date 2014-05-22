# -*- coding: utf-8 -*-
"""
Created on May 21, 2014

@author: HubbeKing, Tyranic-Moron
"""

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars


class Alias(CommandInterface):
    triggers = ['alias']
    help = 'alias <alias> <command> <params> - aliases <alias> to the specified command and parameters\n' \
           'you can specify where parameters given to the alias should be inserted with $1, $2, $n. ' \
           'The whole parameter string is $0. $sender and $channel can also be used.'
    aliases = {}       
           
    def onLoad(self):
        pass
        #Here you can load in aliases from your chosen storage. Just make sure to save them in newAlias aswell.
           
    def newAlias(self, alias, command):
        self.aliases[alias] = command
        
    def aliasedMessage(self, message):
        if message.Command in self.aliases.keys():
            alias = self.aliases[message.Command]
            newMsg = message.MessageString.replace(message.Command, " ".join(alias), 1)
            if "$sender" in newMsg:
                newMsg = newMsg.replace("$sender", message.User.Name)
            if "$channel" in newMsg:
                newMsg = newMsg.replace("$channel", message.Channel)
            newMsg = newMsg.replace(message.Parameters, "")
            if "$0" in newMsg:
                newMsg = newMsg.replace("$0", " ".join(message.ParameterList))
            if len(message.ParameterList) >= 1:
                for i, param in enumerate(message.ParameterList):
                    if newMsg.find("${}+".format(i+1)) != -1:
                        newMsg = newMsg.replace("${}+".format(i+1), " ".join(message.ParameterList[i:]))
                    else:
                        newMsg = newMsg.replace("${}".format(i+1), param)
            return IRCMessage(message.Type, message.User.String, message.Channel, newMsg)

    def shouldExecute(self, message):
        return True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Command in self.triggers:
            if message.User.Name not in GlobalVars.admins:
                return IRCResponse(ResponseType.Say, "Only my admins may create new aliases!", message.ReplyTo)
    
            if len(message.ParameterList) <= 1:
                return IRCResponse(ResponseType.Say, "Alias what?", message.ReplyTo)
    
            triggerFound = False
            for (name, command) in self.bot.moduleHandler.commands.items():
                if message.ParameterList[0] in command.triggers:
                    return IRCResponse(ResponseType.Say,
                                       "'{}' is already a command!".format(message.ParameterList[0]),
                                       message.ReplyTo)
                if message.ParameterList[1] in command.triggers:
                    triggerFound = True
    
            if not triggerFound:
                return IRCResponse(ResponseType.Say,
                                   "'{}' is not a valid command!".format(message.ParameterList[1]),
                                   message.ReplyTo)
            if message.ParameterList[0] in self.bot.moduleHandler.commandAliases:
                return IRCResponse(ResponseType.Say,
                                   "'{}' is already an alias!".format(message.ParameterList[0]),
                                   message.ReplyTo)
    
            newAlias = []
            for word in message.ParameterList[1:]:
                newAlias.append(word.lower())
            self.newAlias(message.ParameterList[0], newAlias)
    
            return IRCResponse(ResponseType.Say,
                               "Created a new alias '{}' for '{}'.".format(message.ParameterList[0],
                                                                           " ".join(message.ParameterList[1:])),
                               message.ReplyTo)
                               
        elif message.Command in self.aliases.keys():
            self.bot.moduleHandler.handleMessage(self.aliasedMessage(message))
