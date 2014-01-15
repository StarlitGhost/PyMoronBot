from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import GlobalVars

import sys
from FunctionHandler import LoadFunction, UnloadFunction, AutoLoadFunctions

class Instantiate(Function):
    Help = "load <function>, unload <function> - handles loading/unloading/reloading of functions. Use 'all' with load to reload all active functions"

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        notAllowed = "Only my admins can use {0}".format(message.Command)

        if message.Command == "load":
            if message.User.Name not in GlobalVars.admins:
                return IRCResponse(ResponseType.Say, notAllowed, message.ReplyTo)

            if len(message.ParameterList) == 0:
                return IRCResponse(ResponseType.Say, "You didn't specify a function name! Usage: {0}".format(self.Help), message.ReplyTo)
            
            path = message.ParameterList[0]
            
            if path == 'FuncLoader':
                return IRCResponse(ResponseType.Say, "I can't reload myself, sorry!", message.ReplyTo)
            
            elif path == 'all':
                for name, func in GlobalVars.functions.iteritems():
                    if name != 'FuncLoader':
                        LoadFunction(name)
                        LoadFunction(name)
                return IRCResponse(ResponseType.Say, "All functions reloaded!", message.ReplyTo)
            
            else:
                try:
                    loadType = LoadFunction(path)
                    LoadFunction(path)
                    return IRCResponse(ResponseType.Say, "Function '%s' %soaded!" % (path, loadType), message.ReplyTo)
                except Exception:
                    return IRCResponse(ResponseType.Say, "Load Error: cannot find function '%s'" % path, message.ReplyTo)
        
        elif message.Command == "unload":
            if message.User.Name not in GlobalVars.admins:
                return IRCResponse(ResponseType.Say, notAllowed, message.ReplyTo)

            if len(message.ParameterList) == 0:
                return IRCResponse(ResponseType.Say, "You didn't specify a function name! Usage: {0}".format(self.Help), message.ReplyTo)
            
            path = message.ParameterList[0]
            
            try:
                success = UnloadFunction(path)
                if success:
                    return IRCResponse(ResponseType.Say, "Function '%s' unloaded!" % path, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, "Function '%s' not found" % path, message.ReplyTo)
            except Exception:
                return IRCResponse(ResponseType.Say, "Unload Error: function '%s' not loaded" % path, message.ReplyTo)
