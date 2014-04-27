import sys, platform, os, traceback, datetime, codecs, argparse
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from IRCResponse import IRCResponse, ResponseType
from IRCMessage import IRCMessage, IRCChannel, IRCUser
from FunctionHandler import AutoLoadFunctions
import GlobalVars, ServerInfo

parser = argparse.ArgumentParser(description='An IRC bot written in Python.')
parser.add_argument('-s', '--server', help='the IRC server to connect to (required)', type=str, required=True)
parser.add_argument('-p', '--port', help='the port on the server to connect to (default 6667)', type=int, default=6667)
parser.add_argument('-c', '--channels', help='channels to join after connecting (default none)', type=str, nargs='+', default=[])
parser.add_argument('-n', '--nick', help='the nick the bot should use (default PyMoronBot)', type=str, default='PyMoronBot')
cmdArgs = parser.parse_args()

restarting = False
startTime = datetime.datetime.utcnow()

class MoronBot(irc.IRCClient):

    GlobalVars.CurrentNick = cmdArgs.nick

    nickname = GlobalVars.CurrentNick
    
    realname = GlobalVars.CurrentNick
    username = GlobalVars.CurrentNick
    
    channels = {}
    userModes = {}

    fingerReply = GlobalVars.finger
    
    versionName = GlobalVars.CurrentNick
    versionNum = GlobalVars.version
    versionEnv = platform.platform()
    
    sourceURL = GlobalVars.source
    
    responses = []

    def signedOn(self):
        for channel in cmdArgs.channels:
            self.join(channel)

        global startTime
        startTime = datetime.datetime.utcnow()
    
    def privmsg(self, user, channel, msg):
        chan = self.getChannel(channel)
        message = IRCMessage('PRIVMSG', user, chan, msg)
        self.log(u'<{0}> {1}'.format(message.User.Name, message.MessageString), message.ReplyTo)
        self.handleMessage(message)

    def action(self, user, channel, msg):
        chan = self.getChannel(channel)
        message = IRCMessage('ACTION', user, chan, msg)
        self.log(u'*{0} {1}*'.format(message.User.Name, message.MessageString), message.ReplyTo)
        self.handleMessage(message)
    
    def noticed(self, user, channel, msg):
        chan = self.getChannel(channel)
        message = IRCMessage('NOTICE', user, chan, msg)
        self.log(u'[{0}] {1}'.format(message.User.Name, message.MessageString), message.ReplyTo)
        self.handleMessage(message)
    
    def irc_NICK(self, prefix, params):
        userArray = prefix.split('!')
        oldnick = userArray[0]
        newnick = params[0]

        for key in self.channels:
            channel = self.channels[key]
            for userKey in channel.Users:
                user = channel.Users[userKey]
                if userKey == oldnick:
                    channel.Users[newnick] = IRCUser('{0}!{1}@{2}'.format(newnick, user.User, user.Hostmask))
                    del channel.Users[oldnick]
                    self.log(u'{0} is now known as {1}'.format(oldnick, newnick), channel.Name)

    def nickChanged(self, nick):
        self.nickname = nick
        GlobalVars.CurrentNick = nick
    
    def irc_JOIN(self, prefix, params):
        if params[0] in self.channels:
            channel = self.channels[params[0]]
        else:
            channel = IRCChannel(params[0])

        message = IRCMessage('JOIN', prefix, channel, '')

        if message.User.Name == GlobalVars.CurrentNick:
            self.channels[message.ReplyTo] = channel
            self.sendLine('WHO ' + message.ReplyTo)
            self.sendLine('MODE ' + message.ReplyTo)
        else:
            channel.Users[message.User.Name] = message.User

        self.log(u' >> {0} ({1}@{2}) joined {3}'.format(message.User.Name, message.User.User, message.User.Hostmask, message.ReplyTo), message.ReplyTo)
    
    def irc_PART(self, prefix, params):
        partMessage = u''
        if len(params) > 1:
            partMessage = u', message: '+u' '.join(params[1:])
        channel = self.channels[params[0]]
        message = IRCMessage('PART', prefix, channel, partMessage)
        
        if message.User.Name == GlobalVars.CurrentNick:
            del self.channels[message.ReplyTo]
        else:
            del channel.Users[message.User.Name]

        self.log(u' << {0} ({1}@{2}) left {3}{4}'.format(message.User.Name, message.User.User, message.User.Hostmask, message.ReplyTo, partMessage), message.ReplyTo)

    def irc_KICK(self, prefix, params):
        kickMessage = u''
        if len(params) > 2:
            kickMessage = u', message: '+u' '.join(params[2:])
        
        channel = self.channels[params[0]]
        message = IRCMessage('KICK', prefix, channel, kickMessage)
        kickee = params[1]

        if kickee == GlobalVars.CurrentNick:
            del self.channels[message.ReplyTo]
        else:
            del channel.Users[kickee]

        self.log(u'!<< {0} was kicked by {1}{2}'.format(kickee, message.User.Name, kickMessage), message.ReplyTo)

    def irc_QUIT(self, prefix, params):
        quitMessage = u''
        if len(params) > 0:
            quitMessage = u', message: '+u' '.join(params[0:])

        message = IRCMessage('QUIT', prefix, None, quitMessage)
        
        for key in self.channels:
            channel = self.channels[key]
            if message.User.Name in channel.Users:
                del channel.Users[message.User.Name]
                self.log(u' << {0} ({1}@{2}) quit{3}'.format(message.User.Name, message.User.User, message.User.Hostmask, quitMessage), channel.Name)

    def irc_RPL_WHOREPLY(self, prefix, params):
        user = IRCUser('{0}!{1}@{2}'.format(params[5], params[2], params[3]))
        channel = self.channels[params[1]]
        flags = params[6][2:] if '*' in params[6] else params[6][1:]
        
        statusModes = ''
        for flag in flags:
            statusModes = statusModes + ServerInfo.StatusesReverse[flag]

        channel.Users[user.Name] = user
        channel.Ranks[user.Name] = statusModes

    def irc_RPL_CHANNELMODEIS(self, prefix, params):
        channel = self.channels[params[1]]
        modestring = params[2][1:]
        modeparams = params[3:]

        for mode in modestring:
            if mode in ServerInfo.ChannelSetArgsModes or mode in ServerInfo.ChannelSetUnsetArgsModes:
                # Mode takes an argument
                channel.Modes[mode] = modeparams[0]
                del modeparams[0]
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
                    statusChars = prefixes[1:prefixes.find(')')]
                    statusSymbols = prefixes[prefixes.find(')') + 1:]
                    ServerInfo.StatusOrder = statusChars
                    for i in range(1, len(statusChars)):
                        ServerInfo.Statuses[statusChars[i]] = statusSymbols[i]
                        ServerInfo.StatusesReverse[statusSymbols[i]] = statusChars[i]

    def modeChanged(self, user, channel, set, modes, args):
        message = IRCMessage('MODE', user, self.getChannel(channel), '')
        if not message.Channel:
            #Setting a usermode
            for mode, arg in zip(modes, args):
                if set:
                    self.userModes[mode] = arg
                else:
                    del self.userModes[mode]
        else:
            #Setting a chanmode
            for mode, arg in zip(modes, args):
                if mode in ServerInfo.Statuses:
                    #Setting a status mode
                    if set:
                        if arg not in self.channels[channel].Ranks:
                            self.channels[channel].Ranks[arg] = mode
                        else:
                            self.channels[channel].Ranks[arg] = self.channels[channel].Ranks[arg] + mode
                    else:
                        self.channels[channel].Ranks[arg] = self.channels[channel].Rank[arg].replace(mode,'')
                else:
                    #Setting a normal chanmode
                    if set:
                        self.channels[channel].Modes[mode] = arg
                    else:
                        del self.channels[channel].Modes[mode]

        logArgs = [arg for arg in args if arg is not None]
        operator = '+' if set else '-'
        target  = message.ReplyTo if message.Channel else ''
        
        self.log(u'# {0} sets mode: {1}{2} {3}'.format(message.User.Name, operator, modes, ' '.join(logArgs)), target)

    def getChannel(self, name):
        if name in self.channels:
            return self.channels[name]
        else:
            #This is a PM
            return None

    def topicUpdated(self, user, channel, newTopic):
        self.channels[channel].Topic = newTopic
        self.channels[channel].TopicSetBy = user

        self.log(u'# {0} set the topic to: {1}'.format(user, newTopic), channel)

    def sendResponse(self, response):
        if (response == None or response.Response == None):
            return False
        
        if (response.Type == ResponseType.Say):
            self.msg(response.Target, response.Response.encode('utf-8'))
            self.log(u'<{0}> {1}'.format(self.nickname, response.Response), response.Target)
        elif (response.Type == ResponseType.Do):
            self.describe(response.Target, response.Response.encode('utf-8'))
            self.log(u'*{0} {1}*'.format(self.nickname, response.Response), response.Target)
        elif (response.Type == ResponseType.Notice):
            self.notice(response.Target, response.Response.encode('utf-8'))
            self.log(u'[{0}] {1}'.format(self.nickname, response.Response), response.Target)
        elif (response.Type == ResponseType.Raw):
            self.sendLine(response.Response.encode('utf-8'))

    def handleMessage(self, message):
        self.responses = [] # in case earlier Function responses caused some weird errors

        # restart command, can't restart within 1 minute of starting (avoids chanhistory triggering another restart)
        if message.Command == 'restart' and datetime.datetime.utcnow() > startTime + datetime.timedelta(seconds=10) and message.User.Name in GlobalVars.admins:
            global restarting
            restarting = True
            self.quit(message = 'restarting')
            return

        for (name, func) in GlobalVars.functions.items():
            try:
                response = func.GetResponse(message)
                if response is None:
                    continue
                if hasattr(response, '__iter__'):
                    for r in response:
                        self.responses.append(r)
                else:
                    self.responses.append(response)
            except Exception:
                print "Python Execution Error in '%s': %s" % (name, str( sys.exc_info() ))
                traceback.print_tb(sys.exc_info()[2])
        
        for response in self.responses:
            self.sendResponse(response)

        self.responses = []
        
    def log(self, text, target):
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
        
class MoronBotFactory(protocol.ReconnectingClientFactory):

    protocol = MoronBot
    
    def startedConnecting(self, connector):
        print '-#- Started to connect.'
        
    def buildProtocol(self, addr):
        print '-#- Connected.'
        print '-#- Resetting reconnection delay'
        self.resetDelay()
        return MoronBot()
        
    def clientConnectionLost(self, connector, reason):
        print '-!- Lost connection.  Reason:', reason
        if restarting:
            python = sys.executable
            os.execl(python, python, *sys.argv)
            #nothing beyond here will be executed if the bot is restarting, as the process itself is replaced

        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print '-!- Connection failed. Reason:', reason
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

if __name__ == '__main__':
    AutoLoadFunctions()
    moronbot = MoronBotFactory()
    reactor.connectTCP(cmdArgs.server, cmdArgs.port, moronbot)
    reactor.run()
