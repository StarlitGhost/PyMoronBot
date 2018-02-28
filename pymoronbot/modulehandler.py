# -*- coding: utf-8 -*-
import importlib
import sys
import traceback

from twisted.plugin import getPlugins
from twisted.python.rebuild import rebuild
from twisted.internet import threads
from enum import Enum
from six import iteritems

from pymoronbot.moduleinterface import IModule
import pymoronbot.modules
from pymoronbot.message import TargetTypes
from pymoronbot.response import ResponseType


class ModuleHandler(object):
    def __init__(self, bot):
        """
        @type bot: MoronBot
        """
        self.bot = bot

        self.modules = {}
        self.caseMap = {}
        self.actions = {}
        self.mappedTriggers = {}

    def loadModule(self, name):
        for module in getPlugins(IModule, pymoronbot.modules):
            if module.__name__ and module.__name__.lower() == name.lower():
                rebuild(importlib.import_module(module.__module__))
                self._loadModuleData(module)

                return module.__name__

    def _loadModuleData(self, module):
        if not IModule.providedBy(module):
            raise ModuleLoaderError(module.__name__,
                                    "Module doesn't implement the module interface.",
                                    ModuleLoadType.LOAD)
        if module.__name__ in self.modules:
            raise ModuleLoaderError(module.__name__,
                                    "Module is already loaded.",
                                    ModuleLoadType.LOAD)

        module.hookBot(self.bot)

        actions = {}
        for action in module.actions():
            if action[0] not in actions:
                actions[action[0]] = [ (action[2], action[1]) ]
            else:
                actions[action[0]].append((action[2], action[1]))

        for action, actionList in iteritems(actions):
            if action not in self.actions:
                self.actions[action] = []
            for actionData in actionList:
                for index, handlerData in enumerate(self.actions[action]):
                    if handlerData[1] < actionData[1]:
                        self.actions[action].insert(index, actionData)
                        break
                else:
                    self.actions[action].append(actionData)

        # map triggers to modules so we can call them via dict lookup
        if hasattr(module, 'triggers'):
            for trigger in module.triggers():
                self.mappedTriggers[trigger] = module

        self.modules.update({module.__name__: module})
        self.caseMap.update({module.__name__.lower(): module.__name__})

        module.onLoad()

    def unloadModule(self, name):
        if name.lower() not in self.caseMap:
            raise ModuleLoaderError(name, "The module is not loaded.", ModuleLoadType.UNLOAD)

        name = self.caseMap[name.lower()]

        self.modules[name].onUnload()

        for action in self.modules[name]:
            self.actions[action[0]].remove((action[2], action[1]))

        # unmap module triggers
        if hasattr(self.modules[name], 'triggers'):
            for trigger in self.modules[name].triggers():
                del self.mappedTriggers[trigger]

        del self.modules[name]
        del self.caseMap[name.lower()]

        return name

    def reloadModule(self, name):
        self.unloadModule(name)
        return self.loadModule(name)

    def sendPRIVMSG(self, message, destination):
        self.bot.msg(destination, message)

    def handleMessage(self, message):
        isChannel = message.TargetType == TargetTypes.CHANNEL
        typeActionMap = {
            "PRIVMSG": lambda: "message-channel" if isChannel else "message-user",
            "ACTION": lambda: "action-channel" if isChannel else "action-user",
            "NOTICE": lambda: "notice-channel" if isChannel else "notice-user",
            "JOIN": lambda: "channeljoin",
            "INVITE": lambda: "channelinvite",
            "PART": lambda: "channelpart",
            "KICK": lambda: "channelkick",
            "QUIT": lambda: "userquit",
            "NICK": lambda: "usernick",
            "MODE": lambda: "modeschanged-channel" if isChannel else "modeschanged-user",
            "TOPIC": lambda: "channeltopic",
        }
        action = typeActionMap[message.Type]
        responses = self.runGatheringAction(action, message)
        self.sendResponses(responses)

    def sendResponses(self, responses):
        typeActionMap = {
            ResponseType.Say: lambda: "response-message",
            ResponseType.Do: lambda: "response-action",
            ResponseType.Notice: lambda: "response-notice",
            ResponseType.Raw: lambda: "response-",
        }
        for response in responses:
            if not response or not response.Response:
                continue

            action = typeActionMap[response.Type]()
            if response.Type == ResponseType.Raw:
                action += response.Response.split()[0].lower()
            self.runProcessingAction(action, response)

            try:
                if response.Type == ResponseType.Say:
                    self.bot.msg(response.Target, response.Response)
                elif response.Type == ResponseType.Do:
                    self.bot.describe(response.Target, response.Response)
                elif response.Type == ResponseType.Notice:
                    self.bot.notice(response.Target, response.Response)
                elif response.Type == ResponseType.Raw:
                    self.bot.sendLine(response.Response)
            except Exception:
                # ^ dirty, but I don't want any modules to kill the bot, especially if I'm working on it live
                print("Python Execution Error sending responses '{0}': {1}".format(responses, str(sys.exc_info())))
                traceback.print_tb(sys.exc_info()[2])

    def loadAll(self):
        modulesToLoad = self.bot.config.getWithDefault('modules', ['all'])
        if 'all' in modulesToLoad:
            modulesToLoad.extend([module.__name__ for module in getPlugins(IModule, pymoronbot.modules)])

        for module in modulesToLoad:
            if module == 'all':
                continue
            elif module.startswith('-'):
                modulesToLoad.remove(module[1:])
            else:
                modulesToLoad.append(module)

        for module in set(modulesToLoad):
            try:
                self.loadModule(module)
            except Exception as e:
                print(u'[{}]'.format(module), e)

    def runGenericAction(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            action[0](*params, **kw)

    def runProcessingAction(self, actionName, data, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            action[0](data, *params, **kw)
            if not data:
                return

    def runGatheringAction(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        responses = []
        for action in actionList:
            responses.append(action[0](*params, **kw))
        return responses

    def runActionUntilTrue(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            if action[0](*params, **kw):
                return True
        return False

    def runActionUntilFalse(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            if not action[0](*params, **kw):
                return True
        return False

    def runActionUntilValue(self, actionName, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        for action in actionList:
            value = action[0](*params, **kw)
            if value:
                return value
        return None


class ModuleLoadType(Enum):
    LOAD = 0
    UNLOAD = 1


class ModuleLoaderError(Exception):
    def __init__(self, module, message, loadType):
        self.module = module
        self.message = message
        self.loadType = loadType

    def __str__(self):
        if self.loadType == ModuleLoadType.LOAD:
            return "Module {} could not be loaded: {}".format(self.module, self.message)
        elif self.loadType == ModuleLoadType.UNLOAD:
            return "Module {} could not be unloaded: {}".format(self.module, self.message)
        elif self.loadType == ModuleLoadType.ENABLE:
            return "Module {} could not be enabled: {}".format(self.module, self.message)
        elif self.loadType == ModuleLoadType.DISABLE:
            return "Module {} could not be disabled: {}".format(self.module, self.message)
        return "Error: {}".format(self.message)
