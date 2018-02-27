# -*- coding: utf-8 -*-
"""
Created on May 11, 2014

@author: Tyranic-Moron
"""

import datetime
import codecs
import os

from pymoronbot.message import IRCMessage
from pymoronbot.modules.commandinterface import BotCommand

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
    'MODE': lambda m: u'# {0} sets mode: {1}{2} {3}'.format(m.User.Name, m.ModeOperator, m.Modes, ' '.join(m.ModeArgs))
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


class Log(BotCommand):
    triggers = []#['log']
    help = "Logs {} messages.".format("/".join(logFuncs.keys()))#"log (-n / yyyy-mm-dd) - " \
           #"without parameters, links to today's log. " \
           #"-n links to the log n days ago. " \
           #"yyyy-mm-dd links to the log for the specified date"

    priority = -1

    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        """
        return True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Type in logFuncs:
            logString = logFuncs[message.Type](message)
            log(os.path.join(self.bot.logPath, self.bot.server),
                message.ReplyTo,
                logString)

        if message.Type in self.acceptedTypes and message.Command in self.triggers:
            # log linking things
            super(Log, self).execute(message)
