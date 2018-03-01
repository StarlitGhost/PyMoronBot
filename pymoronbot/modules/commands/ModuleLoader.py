# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand, admin
from zope.interface import implementer

from pymoronbot.modulehandler import ModuleHandler
from pymoronbot.response import IRCResponse, ResponseType

import sys
import traceback

from six import iteritems


@implementer(IPlugin, IModule)
class ModuleLoader(BotCommand):
    def triggers(self):
        return ['load', 'reload', 'unload']

    def help(self, arg):
        return "load/reload/unload <module> - handles loading/reloading/unloading of modules."

    @admin
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say,
                               "You didn't specify a module name! Usage: {0}".format(self.help),
                               message.ReplyTo)

        command = {'load': self.load, 'reload': self.reload, 'unload': self.unload}[message.Command.lower()]

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
    def load(moduleNames, moduleHandler):
        """
        @type moduleNames: list[str]
        @type moduleHandler: ModuleHandler
        @return: (list[str], list[str], list[str])
        """

        moduleNameCaseMap = {m.lower(): m for m in moduleNames}

        successes = []
        failures = []
        exceptions = []

        for moduleName in moduleNameCaseMap.keys():
            try:
                success = moduleHandler.loadModule(moduleName)
                if success:
                    successes.append(moduleNameCaseMap[moduleName])
                else:
                    failures.append(moduleNameCaseMap[moduleName])
            except Exception as x:
                xName = x.__class__.__name__
                exceptions.append(u"{} ({})".format(moduleNameCaseMap[moduleName], xName))
                print(xName, x.args)
                traceback.print_tb(sys.exc_info()[2])

        return successes, failures, exceptions

    @staticmethod
    def reload(moduleNames, moduleHandler):
        """
        @type moduleNames: list[str]
        @type moduleHandler: ModuleHandler
        @return: (list[str], list[str], list[str])
        """
        moduleNameCaseMap = {m.lower(): m for m in moduleNames}

        successes = []
        failures = []
        exceptions = []

        if len(moduleNames) == 1 and 'all' in moduleNameCaseMap:
            for name, _ in iteritems(moduleHandler.modules):
                if name == 'ModuleLoader':
                    continue

                moduleHandler.reloadModule(name)

            return ['all commands'], [], []

        for moduleName in moduleNameCaseMap:

            if moduleName == 'moduleloader':
                failures.append("ModuleLoader (I can't reload myself)")
            
            else:
                try:
                    success = moduleHandler.reloadModule(moduleName)
                    if success:
                        successes.append(moduleHandler.caseMap[moduleName])
                    else:
                        failures.append(moduleNameCaseMap[moduleName])

                except Exception as x:
                    xName = x.__class__.__name__
                    exceptions.append(u"{} ({})".format(moduleNameCaseMap[moduleName], xName))
                    print(xName, x.args)
                    traceback.print_tb(sys.exc_info()[2])

        return successes, failures, exceptions

    @staticmethod
    def unload(moduleNames, moduleHandler):
        """
        @type moduleNames: list[str]
        @type moduleHandler: ModuleHandler
        @return: (list[str], list[str], list[str])
        """

        moduleNameCaseMap = {m.lower(): m for m in moduleNames}

        successes = []
        failures = []
        exceptions = []
        
        for moduleName in moduleNameCaseMap.keys():
            try:
                success = moduleHandler.unloadModule(moduleName)
                if success:
                    successes.append(moduleNameCaseMap[moduleName])
                else:
                    failures.append(moduleNameCaseMap[moduleName])
            except Exception as x:
                xName = x.__class__.__name__
                exceptions.append(u"{} ({})".format(moduleNameCaseMap[moduleName], xName))
                print(xName, x.args)
                traceback.print_tb(sys.exc_info()[2])

        return successes, failures, exceptions


moduleloader = ModuleLoader()
