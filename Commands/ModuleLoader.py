# -*- coding: utf-8 -*-
from CommandInterface import CommandInterface
from ModuleHandler import ModuleHandler
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars

import sys
import traceback

from six import iteritems


class ModuleLoader(CommandInterface):
    triggers = ['load', 'reload', 'unload',
                'loadp', 'reloadp', 'unloadp']
    help = "load/reload <command>, unload <command> - handles loading/unloading/reloading of commands. " \
           "Use 'all' with load/reload to reload all active commands"

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.User.Name not in GlobalVars.admins:
            return IRCResponse(ResponseType.Say,
                               "Only my admins can use {0}".format(message.Command),
                               message.ReplyTo)

        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "You didn't specify a command name! Usage: {0}".format(self.help),
                               message.ReplyTo)

        command = {'load': self.load, 'reload': self.load, 'unload': self.unload,
                   'loadp': self.loadp, 'reloadp': self.loadp, 'unloadp': self.unloadp,
        }[message.Command.lower()]

        successes, failures, exceptions = command(message.ParameterList, self.bot.moduleHandler)

        responses = []
        if len(successes) > 0:
            responses.append(IRCResponse(ResponseType.Say,
                                         "'{0}' {1}ed successfully".format(', '.join(successes),
                                                                           message.Command.lower()),
                                         message.ReplyTo))
        if len(failures) > 0:
            responses.append(IRCResponse(ResponseType.Say,
                                         "'{0}' failed to {1}, or (they) do not exist".format(', '.join(failures),
                                                                                              message.Command.lower()),
                                         message.ReplyTo))
        if len(exceptions) > 0:
            responses.append(IRCResponse(ResponseType.Say,
                                         "'{0}' threw an exception (printed to console)".format(', '.join(exceptions)),
                                         message.ReplyTo))

        return responses

    @staticmethod
    def load(commandNames, moduleHandler):
        """
        @type commandNames: list[str]
        @type moduleHandler: ModuleHandler
        @return: (list[str], list[str], list[str])
        """
        commandNameCaseMap = {c.lower(): c for c in commandNames}

        successes = []
        failures = []
        exceptions = []

        if len(commandNames) == 1 and 'all' in commandNameCaseMap:
            for name, _ in iteritems(moduleHandler.commands):
                if name == 'ModuleLoader':
                    continue

                moduleHandler.loadCommand(name)

            return ['all commands'], [], []

        for commandName in commandNameCaseMap.keys():

            if commandName == 'moduleloader':
                failures.append("ModuleLoader (I can't reload myself)")
            
            else:
                try:
                    success = moduleHandler.loadCommand(commandName)
                    if success:
                        successes.append(moduleHandler.commandCaseMapping[commandName])
                    else:
                        failures.append(commandNameCaseMap[commandName])

                except Exception as x:
                    xName = x.__class__.__name__
                    exceptions.append(u"{} ({})".format(commandNameCaseMap[commandName], xName))
                    print(xName, x.args)
                    traceback.print_tb(sys.exc_info()[2])

        return successes, failures, exceptions

    @staticmethod
    def loadp(postProcessNames, moduleHandler):
        """
        @type postProcessNames: list[str]
        @type moduleHandler: ModuleHandler
        @return: (list[str], list[str], list[str])
        """
        postProcessNameCaseMap = {p.lower(): p for p in postProcessNames}

        successes = []
        failures = []
        exceptions = []

        if len(postProcessNames) == 1 and 'all' in postProcessNameCaseMap:
            for name, _ in iteritems(moduleHandler.postProcesses):
                moduleHandler.loadPostProcess(name)

            return ['all post processes'], [], []

        for postProcessName in postProcessNameCaseMap.keys():
            try:
                success = moduleHandler.loadPostProcess(postProcessName)
                if success:
                    successes.append(moduleHandler.postProcessCaseMapping[postProcessName])
                else:
                    failures.append(postProcessNameCaseMap[postProcessName])

            except Exception as x:
                xName = x.__class__.__name__
                exceptions.append(u"{} ({})".format(postProcessNameCaseMap[postProcessName], xName))
                print(xName, x.args)
                traceback.print_tb(sys.exc_info()[2])

        return successes, failures, exceptions

    @staticmethod
    def unload(commandNames, moduleHandler):
        """
        @type commandNames: list[str]
        @type moduleHandler: ModuleHandler
        @return: (list[str], list[str], list[str])
        """

        commandNameCaseMap = {c.lower(): c for c in commandNames}

        successes = []
        failures = []
        exceptions = []
        
        for commandName in commandNameCaseMap.keys():
            try:
                success = moduleHandler.unloadCommand(commandName)
                if success:
                    successes.append(commandNameCaseMap[commandName])
                else:
                    failures.append(commandNameCaseMap[commandName])
            except Exception as x:
                xName = x.__class__.__name__
                exceptions.append(u"{} ({})".format(commandNameCaseMap[commandName], xName))
                print(xName, x.args)
                traceback.print_tb(sys.exc_info()[2])

        return successes, failures, exceptions

    @staticmethod
    def unloadp(postProcessNames, moduleHandler):
        """
        @type postProcessNames: list[str]
        @type moduleHandler: ModuleHandler
        @return: (list[str], list[str], list[str])
        """

        postProcessNameCaseMap = {p.lower(): p for p in postProcessNames}

        successes = []
        failures = []
        exceptions = []

        for postProcessName in postProcessNameCaseMap.keys():
            try:
                success = moduleHandler.unloadPostProcess(postProcessName)
                if success:
                    successes.append(postProcessNameCaseMap[postProcessName])
                else:
                    failures.append(postProcessNameCaseMap[postProcessName])
            except Exception as x:
                xName = x.__class__.__name__
                exceptions.append(u"{} ({})".format(postProcessNameCaseMap[postProcessName], xName))
                print(xName, x.args)
                traceback.print_tb(sys.exc_info()[2])

        return successes, failures, exceptions
