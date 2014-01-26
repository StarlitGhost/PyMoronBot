import sys, platform, os, traceback, datetime, codecs, argparse
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from IRCResponse import IRCResponse, ResponseType
from IRCMessage import IRCMessage
from FunctionHandler import AutoLoadFunctions
import GlobalVars

parser = argparse.ArgumentParser(description='An IRC bot written in Python.')
parser.add_argument('-s', '--server', help='the IRC server to connect to (required)', type=str, required=True)
parser.add_argument('-p', '--port', help='the port on the server to connect to (default 6667)', type=int, default=6667)
parser.add_argument('-c', '--channels', help='channels to join after connecting (default none)', type=str, nargs='+', default=[])
cmdArgs = parser.parse_args()

restarting = False
startTime = datetime.datetime.utcnow()

class MoronBot(irc.IRCClient):

    nickname = GlobalVars.CurrentNick
    
    realname = GlobalVars.CurrentNick
    username = GlobalVars.CurrentNick
    
    fingerReply = GlobalVars.finger
    
    versionName = GlobalVars.CurrentNick
    versionNum = GlobalVars.version
    versionEnv = platform.platform()
    
    sourceURL = GlobalVars.source
    
    responses = []

    def signedOn(self):
        for channel in cmdArgs.channels:
            self.join(channel)
    
    def privmsg(self, user, channel, msg):
        message = IRCMessage('PRIVMSG', user, channel, msg)
        self.log(u'<{0}> {1}'.format(message.User.Name, message.MessageString), message.ReplyTo)
        self.handleMessage(message)

    def action(self, user, channel, msg):
        message = IRCMessage('ACTION', user, channel, msg)
        self.log(u'*{0} {1}*'.format(message.User.Name, message.MessageString), message.ReplyTo)
        self.handleMessage(message)
    
    def noticed(self, user, channel, msg):
        message = IRCMessage('NOTICE', user, channel, msg)
        self.log(u'[{0}] {1}'.format(message.User.Name, message.MessageString), message.ReplyTo)
        self.handleMessage(message)
    
    def userRenamed(self, oldname, newname):
        self.log(u'{0} is now known as {1}'.format(oldname, newname), '')
    
    def nickChanged(self, nick):
        self.nickname = nick
        GlobalVars.CurrentNick = nick
    
    def irc_JOIN(self, prefix, params):
        message = IRCMessage('JOIN', prefix, params[0], '')
        self.log(u' >> {0} ({1}@{2}) joined {3}'.format(message.User.Name, message.User.User, message.User.Hostmask, message.ReplyTo), message.ReplyTo)
    
    def irc_PART(self, prefix, params):
        partMessage = u''
        if len(params) > 1:
            partMessage = u', message: '+u' '.join(params[1:])
        message = IRCMessage('PART', prefix, params[0], partMessage)
        self.log(u' << {0} ({1}@{2}) left {3}{4}'.format(message.User.Name, message.User.User, message.User.Hostmask, message.ReplyTo, partMessage), message.ReplyTo)

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
        if message.Command == 'restart' and datetime.datetime.utcnow() > startTime + datetime.timedelta(minutes=1):
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
