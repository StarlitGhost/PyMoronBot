# -*- coding: utf-8 -*-
from imp import reload
from importlib import import_module
import sys
import traceback
import operator
import os
from glob import glob

from twisted.internet import threads

from pymoronbot.response import IRCResponse, ResponseType


class ModuleHandler(object):
    def __init__(self, bot):
        """
        @type bot: MoronBot
        """
        self.bot = bot

        self.modules = {}
        self.caseMap = {}
        self.mappedTriggers = {}

        self.modulesToLoad = self.bot.config.getWithDefault('modules', ['all'])

    def loadModule(self, name):
        name = name.lower()

        moduleCaseMap = {key.lower(): key for key in ModuleHandler.getDirList('modules')}

        if name not in moduleCaseMap:
            return False

        alreadyExisted = False

        # unload first if the module is already loaded, we're doing a reload
        if name in self.caseMap:
            self._unload(name)
            alreadyExisted = True

        module = import_module('pymoronbot.modules.' + moduleCaseMap[name])

        reload(module)

        class_ = getattr(module, moduleCaseMap[name])

        constructedModule = class_(self.bot)

        if alreadyExisted:
            print('-- {0} reloaded'.format(module.__name__))
        else:
            print('-- {0} loaded'.format(module.__name__))

        self.modules.update({moduleCaseMap[name]: constructedModule})
        self.caseMap.update({name: moduleCaseMap[name]})

        # map triggers to modules so we can call them via dict lookup
        if hasattr(constructedModule, 'triggers'):
            for trigger in constructedModule.triggers():
                self.mappedTriggers[trigger] = constructedModule

        return True

    def unloadModule(self, name):
        if name.lower() in self.caseMap.keys():
            properName = self.caseMap[name.lower()]

            # unmap module triggers
            if hasattr(self.modules[properName], 'triggers'):
                for trigger in self.modules[properName].triggers:
                    del self.mappedTriggers[trigger]

            self.modules[properName].onUnload()

            del self.modules[properName]
            del self.caseMap[name.lower()]
            del sys.modules['pymoronbot.modules.{}'.format(properName)]
            for f in glob('pymoronbot/modules/{}.pyc'.format(properName)):
                os.remove(f)
        else:
            return False

        return True

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
        modulesToLoad = []
        if 'all' in self.modulesToLoad:
            modulesToLoad.extend(ModuleHandler.getDirList('modules'))

        for module in self.modulesToLoad:
            if module == 'all':
                continue
            elif module.startswith('-'):
                modulesToLoad.remove(module[1:])
            else:
                modulesToLoad.append(module)

        for module in modulesToLoad:
            try:
                self.loadModule(module)
            except Exception as e:
                print(u'[{}]'.format(module), e)

    @classmethod
    def getDirList(cls, category):
        root = os.path.join('pymoronbot', category)

        for item in os.listdir(root):
            if not os.path.isfile(os.path.join(root, item)):
                continue
            if not item.endswith('.py'):
                continue
            if item.startswith('__init__'):
                continue

            yield item[:-3]

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