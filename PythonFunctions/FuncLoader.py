from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import GlobalVars

import sys
from FunctionHandler import LoadFunction, UnloadFunction

class Instantiate(Function):
    Help = "Handles loading/unloading of python functions."

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
            
        if message.Command == "pyload":
            path = message.ParameterList[0]
            try:
                loadType = LoadFunction(path)
                return IRCResponse(ResponseType.Say, "Python Function '%s' %soaded!" % (path, loadType), message.ReplyTo)
            except Exception:
                return IRCResponse(ResponseType.Say, "Python Load Error: cannot find function '%s'" % path, message.ReplyTo)
        elif message.Command == "pyunload":
            path = message.ParameterList[0]
            try:
                success = UnloadFunction(path)
                if success:
                    return IRCResponse(ResponseType.Say, "Python Function '%s' unloaded!" % path, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, "Python Function '%s' not found" % path, message.ReplyTo)
            except Exception:
                return IRCResponse(ResponseType.Say, "Python Unload Error: function '%s' not loaded" % path, message.ReplyTo)
