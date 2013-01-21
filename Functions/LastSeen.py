from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re
import subprocess

class Instantiate(Function):
	Help = 'Finds a nick\'s last message'
	def GetResponse(self, message):
		if message.Type != 'PRIVMSG':
			return
			
		if (len(message.MessageList) > 1 and message.Command == "lastseen"):
			proc = subprocess.Popen(['/usr/bin/php','/opt/moronbot/loggrep.php',message.ParameterList[0],message.ReplyTo], stdout=subprocess.PIPE)
			output = proc.stdout.read()		
			return IRCResponse(ResponseType.Say,output, message.ReplyTo)
		if (len(message.MessageList) > 1 and message.Command == "lastsaw"):
			proc = subprocess.Popen(['/usr/bin/php','/opt/moronbot/loggrep.php',message.ParameterList[0],message.ReplyTo,"sawed"], stdout=subprocess.PIPE)
			output = proc.stdout.read()		
			return IRCResponse(ResponseType.Say,output, message.ReplyTo)
