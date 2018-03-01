# -*- coding: utf-8 -*-
from pymoronbot.modules.commandinterface import BotCommand
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from six import string_types


class Help(BotCommand):
    triggers = ['help', 'module', 'modules']
    help = 'help/module(s) (<module>) - returns a list of loaded modules, ' \
           'or the help text of a particular module if one is specified'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        moduleHandler = self.bot.moduleHandler

        if len(message.ParameterList) > 0:
            if message.ParameterList[0].lower() in moduleHandler.mappedTriggers:
                funcHelp = moduleHandler.mappedTriggers[message.ParameterList[0].lower()].help
                if isinstance(funcHelp, string_types):
                    return IRCResponse(ResponseType.Say, funcHelp, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, funcHelp(message), message.ReplyTo)

            elif message.ParameterList[0].lower() in moduleHandler.moduleCaseMapping:
                func = moduleHandler.modules[moduleHandler.moduleCaseMapping[message.ParameterList[0].lower()]]
                if isinstance(func.help, string_types):
                    return IRCResponse(ResponseType.Say, func.help, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, func.help(message), message.ReplyTo)

            else:
                return IRCResponse(ResponseType.Say,
                                   '"{0}" not found, try "{1}" without parameters '
                                   'to see a list of loaded module names'.format(message.ParameterList[0],
                                                                                 message.Command),
                                   message.ReplyTo)
        else:
            funcs = ', '.join(sorted(moduleHandler.modules, key=lambda s: s.lower()))
            return [IRCResponse(ResponseType.Say,
                                "Command modules loaded are (use 'help <module>' to get help for that module):",
                                message.ReplyTo),
                    IRCResponse(ResponseType.Say,
                                funcs,
                                message.ReplyTo)]
