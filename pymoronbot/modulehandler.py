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
        self.moduleCaseMapping = {}

        self.mappedTriggers = {}

        self.postProcesses = {}
        self.postProcessCaseMapping = {}

        self.modulesToLoad = bot.config.getWithDefault('modules', ['all'])
        self.postProcessesToLoad = bot.config.getWithDefault('postprocesses', ['all'])

    def loadModule(self, name):
        return self._load(name, 'modules', self.modules, self.moduleCaseMapping)

    def loadPostProcess(self, name):
        return self._load(name, 'postprocesses', self.postProcesses, self.postProcessCaseMapping)

    def unloadModule(self, name):
        return self._unload(name, 'modules', self.modules, self.moduleCaseMapping)

    def unloadPostProcess(self, name):
        return self._unload(name, 'postprocesses', self.postProcesses, self.postProcessCaseMapping)

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
                response = self.postProcess(response)

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

    def postProcess(self, response):
        """
        @type response: IRCResponse
        """
        newResponse = response
        for post in sorted(self.postProcesses.values(), key=operator.attrgetter('priority'), reverse=True):
            try:
                if post.shouldExecute(newResponse):
                    newResponse = post.execute(newResponse)
            except Exception:
                # ^ dirty, but I don't want any responses to kill the bot, especially if I'm working on it live
                print("Python Execution Error in '{0}': {1}".format(post.__class__.__name__, str(sys.exc_info())))
                traceback.print_tb(sys.exc_info()[2])

        return newResponse
    
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

    def _load(self, name, category, categoryDict, categoryCaseMap):
        name = name.lower()

        catListCaseMap = {key.lower(): key for key in ModuleHandler.getDirList(category)}

        if name not in catListCaseMap:
            return False

        alreadyExisted = False

        # unload first if the module is already loaded, we're doing a reload
        if name in categoryCaseMap:
            self._unload(name, category, categoryDict, categoryCaseMap)
            alreadyExisted = True

        module = import_module('pymoronbot.' + category + '.' + catListCaseMap[name])

        reload(module)

        class_ = getattr(module, catListCaseMap[name])

        constructedModule = class_(self.bot)

        if alreadyExisted:
            print('-- {0} reloaded'.format(module.__name__))
        else:
            print('-- {0} loaded'.format(module.__name__))

        categoryDict.update({catListCaseMap[name]: constructedModule})
        categoryCaseMap.update({name: catListCaseMap[name]})

        # map triggers to modules so we can call them via dict lookup
        if hasattr(constructedModule, 'triggers'):
            for trigger in constructedModule.triggers:
                self.mappedTriggers[trigger] = constructedModule

        return True

    def _unload(self, name, category, categoryDict, categoryCaseMap):
        if name.lower() in categoryCaseMap.keys():
            properName = categoryCaseMap[name.lower()]

            # unmap module triggers
            if hasattr(categoryDict[properName], 'triggers'):
                for trigger in categoryDict[properName].triggers:
                    del self.mappedTriggers[trigger]

            categoryDict[properName].onUnload()

            del categoryDict[properName]
            del categoryCaseMap[name.lower()]
            del sys.modules['pymoronbot.{0}.{1}'.format(category, properName)]
            for f in glob('pymoronbot/{0}/{1}.pyc'.format(category, properName)):
                os.remove(f)
        else:
            return False

        return True

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

        postProcessesToLoad = []
        if 'all' in self.postProcessesToLoad:
            postProcessesToLoad.extend(ModuleHandler.getDirList('postprocesses'))

        for post in self.postProcessesToLoad:
            if post == 'all':
                continue
            elif post.startswith('-'):
                postProcessesToLoad.remove(post[1:])
            else:
                postProcessesToLoad.append(post)

        for post in postProcessesToLoad:
            try:
                self.loadPostProcess(post)
            except Exception as e:
                print(u'[{}]'.format(post), e)

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
