"""
Created on May 11, 2014

@author: Tyranic-Moron
"""

import datetime
import codecs
import os

from moronbot import cmdArgs
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars


logFuncs = {'PRIVMSG': lambda m,t: log(u'<{0}> {1}'.format(m.User.Name, m.MessageString), t),
            'ACTION': lambda m,t: log(u'*{0} {1}*'.format(m.User.Name, m.MessageString), t),
            'NOTICE': lambda m,t: log(u'[{0}] {1}'.format(m.User.Name, m.MessageString), t),
            'JOIN': lambda m,t: log(u' >> {0} ({1}@{2}) joined {3}'.format(m.User.Name, m.User.User, m.User.Hostmask, m.ReplyTo), t)}


def log(text, target):
    now = datetime.datetime.utcnow()
    time = now.strftime("[%H:%M]")
    data = u'{0} {1}'.format(time, text)
    print target, data

    fileName = "{0}{1}.txt".format(target, now.strftime("-%Y%m%d"))
    fileDirs = os.path.join(GlobalVars.logPath, cmdArgs.server)
    if not os.path.exists(fileDirs):
        os.makedirs(fileDirs)
    filePath = os.path.join(fileDirs, fileName)

    with codecs.open(filePath, 'a+', 'utf-8') as f:
        f.write(data + '\n')


class Command(CommandInterface):
    triggers = ['log']
    help = "log (-n / yyyy-mm-dd) - " \
           "without parameters, links to today's log. " \
           "-n links to the log n days ago. " \
           "yyyy-mm-dd links to the log for the specified date"

    def shouldExecute(self, message=IRCMessage):
        return True

    def execute(self, message=IRCMessage):
        logFuncs[message.Type](message, message.ReplyTo)

        if message.Type == 'PRIVMSG' and message.Command in self.triggers:
            # log linking things
            pass