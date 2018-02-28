# -*- coding: utf-8 -*-
from importlib import import_module
import sys
import traceback
import operator
import os
from glob import glob

from twisted.plugin import getPlugins
from twisted.python.rebuild import rebuild
from twisted.internet import threads

from pymoronbot.moduleinterface import IModule
import pymoronbot.modules
from pymoronbot.response import IRCResponse, ResponseType


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
                actions[action[0]].append(([action[2], action[1]))

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

    def sendResponse(self, response):
        responses = []

        if hasattr(response, '__iter__'):
            for r in response:
                if r is None or r.Response is None or r.Response == '':
                    continue
                responses.append(r)
        elif response is not None and response.Response is not None and response.Response != '':
            responses.append(response)

        for response in responses:
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
    
    def _deferredError(self, failure):
        print(str(failure))

    def handleMessage(self, message):
        isChannel = message.TargetType == TargetTypes.CHANNEL
        typeActionMap = {
            "PRIVMSG": lambda: "message-channel" if isChannel else "message-user",
        }
        action = typeActionMap[message.Type]
        responses = self.runGatheringAction(action, message)
        self.sendResponses(responses)
        ###
        for module in sorted(self.modules.values(), key=operator.attrgetter('priority')):
            try:
                if module.shouldExecute(message):
                    if not module.runInThread:
                        response = module.execute(message)
                        self.sendResponse(response)
                    else:
                        d = threads.deferToThread(module.execute, message)
                        d.addCallback(self.sendResponse)
                        d.addErrback(self._deferredError)
            except Exception:
                # ^ dirty, but I don't want any modules to kill the bot, especially if I'm working on it live
                print("Python Execution Error in '{0}': {1}".format(module.__class__.__name__, str(sys.exc_info())))
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

    def runGatheringProcessingAction(self, actionName, data, *params, **kw):
        actionList = []
        if actionName in self.actions:
            actionList = self.actions[actionName]
        responses = []
        for action in actionList:
            responses.append(action[0](data, *params, **kw))
            if not data:
                return responses
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
