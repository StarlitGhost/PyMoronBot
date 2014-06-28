# -*- coding: utf-8 -*-
import importlib
import sys
import traceback
import operator
import os
from glob import glob

from twisted.internet import threads

from IRCResponse import IRCResponse, ResponseType


class ModuleHandler(object):

    def __init__(self, bot):
        """
        @type bot: MoronBot
        """
        self.bot = bot

        self.commands = {}
        self.commandCaseMapping = {}

        self.mappedTriggers = {}

        self.postProcesses = {}
        self.postProcessCaseMapping = {}

    def loadCommand(self, name):
        return self._load(name, 'Commands', self.commands, self.commandCaseMapping)

    def loadPostProcess(self, name):
        return self._load(name, 'PostProcesses', self.postProcesses, self.postProcessCaseMapping)

    def unloadCommand(self, name):
        return self._unload(name, 'Commands', self.commands, self.commandCaseMapping)

    def unloadPostProcess(self, name):
        return self._unload(name, 'PostProcesses', self.postProcesses, self.postProcessCaseMapping)

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
                    self.bot.msg(response.Target, response.Response.encode('utf-8'))
                elif response.Type == ResponseType.Do:
                    self.bot.describe(response.Target, response.Response.encode('utf-8'))
                elif response.Type == ResponseType.Notice:
                    self.bot.notice(response.Target, response.Response.encode('utf-8'))
                elif response.Type == ResponseType.Raw:
                    self.bot.sendLine(response.Response.encode('utf-8'))
            except Exception:
                # ^ dirty, but I don't want any commands to kill the bot, especially if I'm working on it live
                print "Python Execution Error sending responses '{0}': {1}".format(responses, str(sys.exc_info()))
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
                print "Python Execution Error in '{0}': {1}".format(post.__class__.__name__, str(sys.exc_info()))
                traceback.print_tb(sys.exc_info()[2])

        return newResponse

    def handleMessage(self, message):
        for command in sorted(self.commands.values(), key=operator.attrgetter('priority')):
            try:
                if command.shouldExecute(message):
                    if not command.runInThread:
                        response = command.execute(message)
                        self.sendResponse(response)
                    else:
                        d = threads.deferToThread(command.execute, message)
                        d.addCallback(self.sendResponse)
            except Exception:
                # ^ dirty, but I don't want any commands to kill the bot, especially if I'm working on it live
                print "Python Execution Error in '{0}': {1}".format(command.__class__.__name__, str(sys.exc_info()))
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

        module = importlib.import_module(category + '.' + catListCaseMap[name])

        reload(module)

        class_ = getattr(module, catListCaseMap[name])

        if alreadyExisted:
            print '-- {0} reloaded'.format(module.__name__)
        else:
            print '-- {0} loaded'.format(module.__name__)

        constructedModule = class_(self.bot)

        categoryDict.update({catListCaseMap[name]: constructedModule})
        categoryCaseMap.update({name: catListCaseMap[name]})

        # map triggers to commands so we can call them via dict lookup
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
            del sys.modules['{0}.{1}'.format(category, properName)]
            for f in glob('{0}/{1}.pyc'.format(category, properName)):
                os.remove(f)
        else:
            return False

        return True

    def loadAll(self):
        for command in self.getDirList('Commands'):
            try:
                self.loadCommand(command)
            except Exception, x:
                print x.args

        for post in self.getDirList('PostProcesses'):
            try:
                self.loadPostProcess(post)
            except Exception, x:
                print x.args

    @classmethod
    def getDirList(cls, category):
        root = os.path.join('.', category)

        for item in os.listdir(root):
            if not os.path.isfile(os.path.join(root, item)):
                continue
            if not item.endswith('.py'):
                continue
            if item.startswith('__init__'):
                continue

            yield item[:-3]
