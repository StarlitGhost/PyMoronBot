import sys, platform, os, traceback
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from IRCResponse import IRCResponse, ResponseType
from IRCMessage import IRCMessage
from FunctionHandler import AutoLoadFunctions
import GlobalVars

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

class MoronBot(irc.IRCClient):

    nickname = 'PyMoronBot'
    GlobalVars.CurrentNick = nickname
    
    realname = 'PyMoronBot'
    username = 'PyMoronBot'
    
    fingerReply = 'GET YOUR FINGER OUT OF THERE'
    
    versionName = 'PyMoronBot'
    versionNum = '0.0.1'
    versionEnv = platform.platform()
    
    sourceURL = 'https://github.com/MatthewCox/MoronBot/'
    
    responses = []

    def signedOn(self):
        for channel in self.factory.channels:
            self.join(channel)
    
    def privmsg(self, user, channel, msg):
        print "%s <%s> %s" % (channel, user.split('!')[0], msg)
        message = IRCMessage('PRIVMSG', user, channel, msg)
        self.handleMessage(message)

    def action(self, user, channel, msg):
        print "%s *%s %s*" % (channel, user.split('!')[0], msg)
        message = IRCMessage('ACTION', user, channel, msg)
        self.handleMessage(message)

    def sendResponse(self, response):
        if (response == None):
            return False
        
        response.Response = response.Response.decode('utf-8').encode('utf-8')
        
        if (response.Type == ResponseType.Say):
            self.msg(response.Target, response.Response)
        elif (response.Type == ResponseType.Do):
            self.describe(response.Target, response.Response)
        elif (response.Type == ResponseType.Notice):
            self.notice(response.Target, response.Response)
        elif (response.Type == ResponseType.Raw):
            self.sendLine(response.Response)

    def handleMessage(self, message):
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
        
class MoronBotFactory(protocol.ClientFactory):

    protocol = MoronBot
    
    def __init__(self, channel):
        self.channels = channels

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed: ", reason
        reactor.stop()

if __name__ == '__main__':
    AutoLoadFunctions()
    channels = ['#unmoderated', '#help', '#survivors']
    moronbot = MoronBotFactory(channels)
    reactor.connectTCP('irc.desertbus.org', 6667, moronbot)
    reactor.run()
