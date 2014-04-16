import sys, platform, os, traceback, datetime, codecs, argparse
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from IRCResponse import IRCResponse, ResponseType
from IRCMessage import IRCMessage, IRCChannel, IRCUser
from ServerInfo import ServerInfo
from FunctionHandler import AutoLoadFunctions
import GlobalVars

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
    serverInfo = ServerInfo()

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
    
    def userRenamed(self, oldname, newname):
        self.log(u'{0} is now known as {1}'.format(oldname, newname), '')
    
    def nickChanged(self, nick):
        self.nickname = nick
        GlobalVars.CurrentNick = nick
    
    def irc_JOIN(self, prefix, params):
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
        channel = self.channels[message.ReplyTo]
        message = IRCMessage('PART', prefix, channel, partMessage)
        
        if message.User.Name == GlobalVars.CurrentNick:
            del self.channels[message.ReplyTo]
        else:
            del channel.Users[message.User.Name]

        self.log(u' << {0} ({1}@{2}) left {3}{4}'.format(message.User.Name, message.User.User, message.User.Hostmask, message.ReplyTo, partMessage), message.ReplyTo)

    def irc_RPL_WHOREPLY(self, prefix, params):
        user = IRCUser('{0}!{1}@{2}'.format(params[5], params[2], params[3]))
        channel = self.channels[params[1]]
        channel.Users[params[5]] = user

    def getChannel(self, name):
        if name in self.channels:
            return self.channels[name]
        else:
            #This is a PM
            return None

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
