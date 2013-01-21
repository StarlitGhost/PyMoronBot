from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re
import datetime
import subprocess

class Instantiate(Function):
    Help = 'Gives Pika a bunch of logs'
    
    lastMessageDate = datetime.datetime.utcnow()
    
    def GetResponse(self, message):
        if message.User.Name != 'Pikachaos':
            return
        
        if message.Type == 'PRIVMSG':
            self.lastMessageDate = datetime.datetime.utcnow()
    
        if message.Type != 'JOIN':
            return
        
        now = datetime.datetime.utcnow()
        timeDiff = now - self.lastMessageDate
        
        date = self.lastMessageDate
        
        replyTo = message.MessageList[2][1:]
        
        output = []
        
        while date < now:
            proc = subprocess.Popen(['/usr/bin/php','/home/ubuntu/moronbot/getloghash.php',replyTo+"-"+ date.strftime('%Y%m%d')], stdout=subprocess.PIPE)
            hash = proc.stdout.read()
            if hash == "Not found":
                output.append(IRCResponse(ResponseType.Say, "No log for %s found." % date.strftime('%Y/%m/%d'), replyTo))
            else:
                output.append(IRCResponse(ResponseType.Say, "Log for " + date.strftime('%Y/%m/%d') + ": http://www.moronic-works.co.uk/logs/?l=" + hash, replyTo))
            date += datetime.timedelta(days = 1)
        
        return output
