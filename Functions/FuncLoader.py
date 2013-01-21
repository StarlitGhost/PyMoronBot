from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import GlobalVars

import sys
from FunctionHandler import LoadFunction, UnloadFunction, AutoLoadFunctions

class Instantiate(Function):
    Help = "load <function>, unload <function> - handles loading/unloading/reloading of functions"

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
            
        if message.Command == "load":
            path = message.ParameterList[0]
            if path == 'FuncLoader':
                return IRCResponse(ResponseType.Say, "I can't reload myself, sorry!", message.ReplyTo)
            elif path == 'all':
                for name, func in GlobalVars.functions.iteritems():
                    if name != 'FuncLoader':
                        LoadFunction(name)
                return IRCResponse(ResponseType.Say, "All functions reloaded!", message.ReplyTo)
            else:
                try:
                    loadType = LoadFunction(path)
                    return IRCResponse(ResponseType.Say, "Function '%s' %soaded!" % (path, loadType), message.ReplyTo)
                except Exception:
                    return IRCResponse(ResponseType.Say, "Load Error: cannot find function '%s'" % path, message.ReplyTo)
        elif message.Command == "unload":
            path = message.ParameterList[0]
            try:
                success = UnloadFunction(path)
                if success:
                    return IRCResponse(ResponseType.Say, "Function '%s' unloaded!" % path, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, "Function '%s' not found" % path, message.ReplyTo)
            except Exception:
                return IRCResponse(ResponseType.Say, "Unload Error: function '%s' not loaded" % path, message.ReplyTo)
