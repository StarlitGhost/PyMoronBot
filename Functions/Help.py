from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import GlobalVars

import re

class Instantiate(Function):

    Help = 'command(s)/help/function(s) (<function>) - Returns a list of loaded functions, or the help text of a particular function if one is specified'
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^(commands?|help|functions?)$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        if len(message.ParameterList) > 0:
            lowerMap = dict(zip(map(lambda x:x.lower(),GlobalVars.functions.iterkeys()),GlobalVars.functions.iterkeys()))
            if (message.ParameterList[0].lower() in lowerMap):
                func = GlobalVars.functions[lowerMap[message.ParameterList[0].lower()]]
                if isinstance(func.Help, basestring):
                    return IRCResponse(ResponseType.Say, func.Help, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, func.Help(message), message.ReplyTo)
            else:
                return IRCResponse(ResponseType.Say, '"%s" not found, try "%s" without parameters to see a list of loaded function names' % (message.ParameterList[0], message.Command), message.ReplyTo)
        else:
            funcs = ', '.join(sorted(GlobalVars.functions.iterkeys(), key=lambda s: s.lower()))
            return [IRCResponse(ResponseType.Say, "Functions loaded are:", message.ReplyTo),
                    IRCResponse(ResponseType.Say, funcs, message.ReplyTo)]

