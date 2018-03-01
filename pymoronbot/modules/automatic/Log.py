# -*- coding: utf-8 -*-
"""
Created on May 11, 2014

@author: Tyranic-Moron
"""

from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

import datetime
import codecs
import os

from pymoronbot.message import IRCMessage
from pymoronbot.response import ResponseType

logFuncs = {
    'PRIVMSG': lambda m: u'<{0}> {1}'.format(m.User.Name, m.MessageString),
    'ACTION': lambda m: u'*{0} {1}*'.format(m.User.Name, m.MessageString),
    'NOTICE': lambda m: u'[{0}] {1}'.format(m.User.Name, m.MessageString),
    'JOIN': lambda m: u' >> {0} ({1}@{2}) joined {3}'.format(m.User.Name, m.User.User, m.User.Hostmask, m.ReplyTo),
    'NICK': lambda m: u'{0} is now known as {1}'.format(m.User.Name, m.MessageString),
    'PART': lambda m: u' << {0} ({1}@{2}) left {3}{4}'.format(m.User.Name, m.User.User, m.User.Hostmask, m.ReplyTo, m.MessageString),
    'QUIT': lambda m: u' << {0} ({1}@{2}) quit{3}'.format(m.User.Name, m.User.User, m.User.Hostmask, m.MessageString),
    'KICK': lambda m: u'!<< {0} was kicked by {1}{2}'.format(m.Kickee, m.User.Name, m.MessageString),
    'TOPIC': lambda m: u'# {0} set the topic to: {1}'.format(m.User.Name, m.MessageString),
    'MODE': lambda m: u'# {0} sets mode: {1}{2} {3}'.format(m.User.Name, m.ModeOperator, m.Modes, ' '.join(m.ModeArgs)),
}

logSelfFuncs = {
    ResponseType.Say: lambda nick, r: u'<{0}> {1}'.format(nick, r.Response),
    ResponseType.Do: lambda nick, r: u'*{0} {1}*'.format(nick, r.Response),
    ResponseType.Notice: lambda nick, r: u'[{0}] {1}'.format(nick, r.Response),
}


def log(path, target, text):
    now = datetime.datetime.utcnow()
    time = now.strftime("[%H:%M]")
    data = u'{0} {1}'.format(time, text)
    print(target, data)

    fileName = "{0}{1}.txt".format(target, now.strftime("-%Y%m%d"))
    fileDirs = path
    if not os.path.exists(fileDirs):
        os.makedirs(fileDirs)
    filePath = os.path.join(fileDirs, fileName)

    with codecs.open(filePath, 'a+', 'utf-8') as f:
        f.write(data + '\n')


@implementer(IPlugin, IModule)
class Log(BotCommand):
    def actions(self):
        return super(Log, self).actions() + [('message-channel', 100, self.input),
                                             ('message-user', 100, self.input),
                                             ('action-channel', 100, self.input),
                                             ('action-user', 100, self.input),
                                             ('notice-channel', 100, self.input),
                                             ('notice-user', 100, self.input),
                                             ('channeljoin', 100, self.input),
                                             ('channelinvite', 100, self.input),
                                             ('channelpart', 100, self.input),
                                             ('channelkick', 100, self.input),
                                             ('userquit', 100, self.input),
                                             ('usernick', 100, self.input),
                                             ('modeschanged-channel', 100, self.input),
                                             ('modeschanged-user', 100, self.input),
                                             ('channeltopic', 100, self.input),
                                             ('response-message', -1, self.output),
                                             ('response-action', -1, self.output),
                                             ('response-notice', -1, self.output)]

    def triggers(self):
        return []#['log']

    def help(self, arg):
        return "Logs {} messages.".format("/".join(logFuncs.keys()))#"log (-n / yyyy-mm-dd) - " \
            #"without parameters, links to today's log. " \
            #"-n links to the log n days ago. " \
            #"yyyy-mm-dd links to the log for the specified date"

    def input(self, message):
        """
        @type message: IRCMessage
        """
        if message.Type in logFuncs:
            logString = logFuncs[message.Type](message)
            log(os.path.join(self.bot.logPath, self.bot.server), message.ReplyTo, logString)

    def output(self, response):
        """
        @type response: IRCResponse
        """
        if response.Type in logSelfFuncs:
            logString = logSelfFuncs[response.Type](self.bot.nickname, response)
            log(os.path.join(self.bot.logPath, self.bot.server),
                response.Target,
                logString)

        return response

    def execute(self, message):
        # log linking things
        pass


logger = Log()
