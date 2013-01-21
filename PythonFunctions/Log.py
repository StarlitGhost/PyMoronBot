from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re
import datetime
import subprocess

import dateutil.parser as dparser

class Instantiate(Function):
    Help = 'Gives you a log link'
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^log$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        date = datetime.datetime.utcnow();
        if len(message.ParameterList) == 1:
            if self.is_number(message.ParameterList[0]):
                date += datetime.timedelta(days = int(message.ParameterList[0]))
            else:
                try:
                    date = dparser.parse(message.ParameterList[0], fuzzy=True, dayfirst=True)
                except ValueError:
                    pass
                
        
        proc = subprocess.Popen(['/usr/bin/php','/home/ubuntu/moronbot/getloghash.php',message.ReplyTo+"-"+ date.strftime('%Y%m%d')], stdout=subprocess.PIPE)
        hash = proc.stdout.read()
        if hash == "Not found":
            output = "I don't have that log."
        else:
            output = "Log for " + date.strftime('%Y/%m/%d') + ": http://www.moronic-works.co.uk/logs/?l=" + hash
            return IRCResponse(ResponseType.Say, output, message.ReplyTo)
            
    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
