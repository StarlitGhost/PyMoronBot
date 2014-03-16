from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re
import subprocess

class Instantiate(Function):
	Help = 'lastmention(ed)/lastsaid <text> - checks the log for the last time someone mentioned a given word or phrase'
	def GetResponse(self, message):
		if message.Type != 'PRIVMSG':
			return
			
		if (len(message.MessageList) > 1 and (message.Command == "lastmention" or message.Command == "lastmentioned")):
			proc = subprocess.Popen(['/usr/bin/php','/opt/moronbot/loggrep.php',"\""+message.Parameters.replace("\"","\\\"").replace("\n","\\\n")+"\"",message.ReplyTo,"mention"], stdout=subprocess.PIPE)
			output = proc.stdout.read()		
			return IRCResponse(ResponseType.Say,output, message.ReplyTo)
		if (len(message.MessageList) > 1 and message.Command == "lastsaid"):
			proc = subprocess.Popen(['/usr/bin/php','/opt/moronbot/loggrep.php',"\""+message.Parameters.replace("\"","\\\"").replace("\n","\\\n")+"\"",message.ReplyTo,"mentionnottoday"],stdout=subprocess.PIPE)
			output = proc.stdout.read()		
			return IRCResponse(ResponseType.Say,output, message.ReplyTo)
