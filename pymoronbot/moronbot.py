# -*- coding: utf-8 -*-
import os
import shelve
import platform
import datetime
import subprocess

from twisted.words.protocols import irc
from twisted.internet import reactor
from pymoronbot.message import IRCMessage, IRCChannel, IRCUser
from pymoronbot import modulehandler, serverinfo


class MoronBot(irc.IRCClient, object):
    def __init__(self, factory, config):
        """
        @type factory: MoronBotFactory
        @type config: Config
        """
        self.factory = factory
        self.config = config

        self.nickname = self.config.getWithDefault('nickname', 'PyMoronBot')

        self.commandChar = self.config.getWithDefault('commandChar', '!')

        self.realname = self.config.getWithDefault('realname', self.nickname)
        self.username = self.config.getWithDefault('username', self.nickname)

        self.channels = {}
        self.userModes = {}

        self.fingerReply = self.config.getWithDefault('finger', 'GET YOUR FINGER OUT OF THERE')

        self.versionName = self.nickname
        try:
            self.versionNum = subprocess.check_output(["git", "describe", "--always"]).decode('utf-8').strip()
        except FileNotFoundError:
            self.versionNum = u'1.0'
        self.versionEnv = platform.platform()

        self.sourceURL = self.config.getWithDefault('source', 'https://github.com/TyranicMoron/PyMoronBot/')

        self.server = self.config['server']

        self.rootDir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

        self.dataPath = os.path.join(self.rootDir, 'data', self.server)
        if not os.path.exists(self.dataPath):
            os.makedirs(self.dataPath)

        # set the logging path
        self.logPath = os.path.join(self.rootDir, 'logs')

        self.quitting = False
        reactor.addSystemEventTrigger('before', 'shutdown', self.cleanup)

        self.moduleHandler = modulehandler.ModuleHandler(self)
        self.moduleHandler.loadAll()
        
        # set start time after modules have loaded, some take a while
        self.startTime = datetime.datetime.utcnow()

    def cleanup(self):
        self.config.writeConfig()
        print('-#- Saved config and data')

    def quit(self, message=''):
        self.cleanup()
        super(MoronBot, self).quit(message)

    def signedOn(self):
        for channel in self.config['channels']:
            self.join(channel)

    def privmsg(self, user, channel, msg):
        chan = self.getChannel(channel)
        message = IRCMessage('PRIVMSG', user, chan, msg, self)
        self.handleMessage(message)

    def action(self, user, channel, msg):
        chan = self.getChannel(channel)
        message = IRCMessage('ACTION', user, chan, msg, self)
        self.handleMessage(message)

    def noticed(self, user, channel, msg):
        chan = self.getChannel(channel)
        message = IRCMessage('NOTICE', user, chan, msg, self)
        self.handleMessage(message)

    def irc_NICK(self, prefix, params):
        userArray = prefix.split('!')
        oldNick = userArray[0]
        newNick = params[0]

        for key in self.channels:
            channel = self.channels[key]
            for userKey in channel.Users:
                user = channel.Users[userKey]
                if userKey == oldNick:
                    channel.Users[newNick] = IRCUser('{0}!{1}@{2}'.format(newNick, user.User, user.Hostmask))
                    del channel.Users[oldNick]
                    if oldNick in channel.Ranks:
                        channel.Ranks[newNick] = channel.Ranks[oldNick]
                        del channel.Ranks[oldNick]
                    message = IRCMessage('NICK', prefix, channel, newNick, self)
                    self.handleMessage(message)

    def nickChanged(self, nick):
        self.nickname = nick

    def irc_JOIN(self, prefix, params):
        if params[0] in self.channels:
            channel = self.channels[params[0]]
        else:
            channel = IRCChannel(params[0])

        message = IRCMessage('JOIN', prefix, channel, u'', self)

        if message.User.Name == self.nickname:
            self.channels[message.ReplyTo] = channel
            self.sendLine('WHO ' + message.ReplyTo)
            self.sendLine('MODE ' + message.ReplyTo)
        else:
            channel.Users[message.User.Name] = message.User

        self.handleMessage(message)

    def irc_INVITE(self, prefix, params):
        if params[0] in self.channels:
            channel = self.channels[params[0]]
        else:
            channel = IRCChannel(params[0])
        message = IRCMessage('INVITE', prefix, channel, u'', self)

        self.join(channel.Name)

        self.handleMessage(message)

    def irc_PART(self, prefix, params):
        partMessage = u''
        if len(params) > 1:
            partMessage = u', message: ' + u' '.join(params[1:])
        channel = self.channels[params[0]]
        message = IRCMessage('PART', prefix, channel, partMessage, self)

        if message.User.Name == self.nickname:
            del self.channels[message.ReplyTo]
        else:
            del channel.Users[message.User.Name]
            if message.User.Name in channel.Ranks:
                del channel.Ranks[message.User.Name]

        self.handleMessage(message)

    def irc_KICK(self, prefix, params):
        kickMessage = u''
        if len(params) > 2:
            kickMessage = u', message: ' + u' '.join(params[2:])

        channel = self.channels[params[0]]
        message = IRCMessage('KICK', prefix, channel, kickMessage, self)
        message.Kickee = params[1]

        if message.Kickee == self.nickname:
            del self.channels[message.ReplyTo]
        else:
            del channel.Users[message.Kickee]
            if message.Kickee in channel.Ranks:
                del channel.Ranks[message.Kickee]

        self.handleMessage(message)

    def irc_QUIT(self, prefix, params):
        quitMessage = u''
        if len(params) > 0:
            quitMessage = u', message: ' + u' '.join(params[0:])

        for key in self.channels:
            channel = self.channels[key]
            message = IRCMessage('QUIT', prefix, channel, quitMessage, self)
            if message.User.Name in channel.Users:
                del channel.Users[message.User.Name]
                if message.User.Name in channel.Ranks:
                    del channel.Ranks[message.User.Name]
                self.handleMessage(message)

    def irc_RPL_WHOREPLY(self, _, params):
        user = IRCUser('{0}!{1}@{2}'.format(params[5], params[2], params[3]))
        channel = self.channels[params[1]]
        flags = params[6][2:] if '*' in params[6] else params[6][1:]

        statusModes = ''
        for flag in flags:
            statusModes = statusModes + serverinfo.StatusesReverse[flag]

        channel.Users[user.Name] = user
        channel.Ranks[user.Name] = statusModes

    def irc_RPL_CHANNELMODEIS(self, _, params):
        channel = self.channels[params[1]]
        modeString = params[2][1:]
        modeParams = params[3:]

        for mode in modeString:
            if mode in serverinfo.ChannelSetArgsModes or mode in serverinfo.ChannelSetUnsetArgsModes:
                # Mode takes an argument
                channel.Modes[mode] = modeParams[0]
                del modeParams[0]
            else:
                channel.Modes[mode] = None

    def irc_RPL_MYINFO(self, prefix, params):
        serverinfo.UserModes = params[3]

    def isupport(self, options):
        for item in options:
            if '=' in item:
                option = item.split('=')
                if option[0] == 'CHANTYPES':
                    serverinfo.ChannelTypes = option[1]
                elif option[0] == 'CHANMODES':
                    modes = option[1].split(',')
                    serverinfo.ChannelListModes = modes[0]
                    serverinfo.ChannelSetUnsetArgsModes = modes[1]
                    serverinfo.ChannelSetArgsModes = modes[2]
                    serverinfo.ChannelNormalModes = modes[3]
                elif option[0] == 'PREFIX':
                    prefixes = option[1]
                    statusChars = prefixes[:prefixes.find(')')]
                    statusSymbols = prefixes[prefixes.find(')'):]
                    serverinfo.StatusOrder = statusChars
                    for i in range(1, len(statusChars)):
                        serverinfo.Statuses[statusChars[i]] = statusSymbols[i]
                        serverinfo.StatusesReverse[statusSymbols[i]] = statusChars[i]

    def modeChanged(self, user, channel, set, modes, args):
        message = IRCMessage('MODE', user, self.getChannel(channel), u'', self)
        if not message.Channel:
            # Setting a usermode
            for mode, arg in zip(modes, args):
                if set:
                    self.userModes[mode] = arg
                else:
                    del self.userModes[mode]
        else:
            # Setting a chanmode
            for mode, arg in zip(modes, args):
                if mode in serverinfo.Statuses:
                    # Setting a status mode
                    if set:
                        if arg not in self.channels[channel].Ranks:
                            self.channels[channel].Ranks[arg] = mode
                        else:
                            self.channels[channel].Ranks[arg] = self.channels[channel].Ranks[arg] + mode
                    else:
                        self.channels[channel].Ranks[arg] = self.channels[channel].Rank[arg].replace(mode, '')
                else:
                    # Setting a normal chanmode
                    if set:
                        self.channels[channel].Modes[mode] = arg
                    else:
                        del self.channels[channel].Modes[mode]

        message.ModeArgs = [arg for arg in args if arg is not None]
        message.Modes = modes
        message.ModeOperator = '+' if set else '-'
        message.ReplyTo = message.ReplyTo if message.Channel else ''

        self.handleMessage(message)

    def getChannel(self, name):
        if name in self.channels:
            return self.channels[name]
        else:
            # This is a PM
            return None

    def topicUpdated(self, user, channel, newTopic):
        self.channels[channel].Topic = newTopic
        self.channels[channel].TopicSetBy = user

        message = IRCMessage('TOPIC', user, self.getChannel(channel), newTopic, self)

        self.handleMessage(message)

    def lineReceived(self, line):
        # decode bytes from transport to unicode, replacing invalid unicode with escapes before twisted gets to them
        if bytes != str and isinstance(line, bytes):
            line = line.decode('utf-8', errors='backslashreplace')

        super(MoronBot, self).lineReceived(line)

    def handleMessage(self, message):
        """
        @type message: IRCMessage
        """
        self.moduleHandler.handleMessage(message)

    def sendResponse(self, response):
        """
        @type response: IRCResponse
        """
        self.moduleHandler.sendResponse(response)
