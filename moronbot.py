#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import shelve
import sys
import platform
import datetime
import argparse

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from IRCMessage import IRCMessage, IRCChannel, IRCUser
from IRCResponse import IRCResponse
import ModuleHandler
import GlobalVars
import ServerInfo


parser = argparse.ArgumentParser(description='An IRC bot written in Python.')
parser.add_argument('-s', '--server', help='the IRC server to connect to (required)', type=str, required=True)
parser.add_argument('-p', '--port', help='the port on the server to connect to (default 6667)', type=int, default=6667)
parser.add_argument('-c', '--channels', help='channels to join after connecting (default none)', type=str, nargs='+', default=[])
parser.add_argument('-n', '--nick', help='the nick the bot should use (default PyMoronBot)', type=str, default='PyMoronBot')
cmdArgs = parser.parse_args()

restarting = False
startTime = datetime.datetime.utcnow()


class MoronBot(irc.IRCClient, object):

    def __init__(self):
        self.nickname = cmdArgs.nick
        self.commandChar = '.'

        self.realname = self.nickname
        self.username = self.nickname

        self.channels = {}
        self.userModes = {}

        self.fingerReply = GlobalVars.finger

        self.versionName = self.nickname
        self.versionNum = GlobalVars.version
        self.versionEnv = platform.platform()

        self.sourceURL = GlobalVars.source

        # dataStore has to be before moduleHandler
        dataStorePath = os.path.join('Data', cmdArgs.server)
        if not os.path.exists(dataStorePath):
            os.makedirs(dataStorePath)
        self.dataStore = shelve.open(os.path.join(dataStorePath, 'shelve.db'), protocol=2, writeback=True)

        self.moduleHandler = ModuleHandler.ModuleHandler(self)
        self.moduleHandler.loadAll()

    def quit(self, message=''):
        self.dataStore.close()
        irc.IRCClient.quit(self, message)

    def signedOn(self):
        for channel in cmdArgs.channels:
            self.join(channel)

        global startTime
        startTime = datetime.datetime.utcnow()

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
            statusModes = statusModes + ServerInfo.StatusesReverse[flag]

        channel.Users[user.Name] = user
        channel.Ranks[user.Name] = statusModes

    def irc_RPL_CHANNELMODEIS(self, _, params):
        channel = self.channels[params[1]]
        modeString = params[2][1:]
        modeParams = params[3:]

        for mode in modeString:
            if mode in ServerInfo.ChannelSetArgsModes or mode in ServerInfo.ChannelSetUnsetArgsModes:
                # Mode takes an argument
                channel.Modes[mode] = modeParams[0]
                del modeParams[0]
            else:
                channel.Modes[mode] = None

    def irc_RPL_MYINFO(self, prefix, params):
        ServerInfo.UserModes = params[3]

    def isupport(self, options):
        for item in options:
            if '=' in item:
                option = item.split('=')
                if option[0] == 'CHANTYPES':
                    ServerInfo.ChannelTypes = option[1]
                elif option[0] == 'CHANMODES':
                    modes = option[1].split(',')
                    ServerInfo.ChannelListModes = modes[0]
                    ServerInfo.ChannelSetUnsetArgsModes = modes[1]
                    ServerInfo.ChannelSetArgsModes = modes[2]
                    ServerInfo.ChannelNormalModes = modes[3]
                elif option[0] == 'PREFIX':
                    prefixes = option[1]
                    statusChars = prefixes[:prefixes.find(')')]
                    statusSymbols = prefixes[prefixes.find(')'):]
                    ServerInfo.StatusOrder = statusChars
                    for i in range(1, len(statusChars)):
                        ServerInfo.Statuses[statusChars[i]] = statusSymbols[i]
                        ServerInfo.StatusesReverse[statusSymbols[i]] = statusChars[i]

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
                if mode in ServerInfo.Statuses:
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
        # restart command, can't restart within 1 minute of starting (avoids chanhistory triggering another restart)
        if (message.Command == 'restart' and
                datetime.datetime.utcnow() > startTime + datetime.timedelta(seconds=10) and
                message.User.Name in GlobalVars.admins):
            global restarting
            restarting = True
            self.dataStore.close()
            self.quit(message='restarting')
            return

        self.moduleHandler.handleMessage(message)

    def sendResponse(self, response):
        """
        @type response: IRCResponse
        """
        self.moduleHandler.sendResponse(response)


class MoronBotFactory(protocol.ReconnectingClientFactory):

    def __init__(self):
        self.protocol = MoronBot

    def startedConnecting(self, connector):
        print('-#- Started to connect.')

    def buildProtocol(self, addr):
        print('-#- Connected.')
        print('-#- Resetting reconnection delay')
        self.resetDelay()
        return MoronBot()

    def clientConnectionLost(self, connector, reason):
        print('-!- Lost connection.  Reason:', reason)
        if restarting:
            python = sys.executable
            os.execl(python, python, *sys.argv)
            # nothing beyond here will be executed if the bot is restarting, as the process itself is replaced

        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('-!- Connection failed. Reason:', reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


if __name__ == '__main__':
    moronbot = MoronBotFactory()
    reactor.connectTCP(cmdArgs.server, cmdArgs.port, moronbot)
    reactor.run()
