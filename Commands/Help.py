from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars

import re

class Command(CommandInterface):
    triggers = ['help','command','commands']
    help = 'command(s)/help/function(s) (<function>) - returns a list of loaded commands, or the help text of a particular command if one is specified'
    
    def execute(self, message):
        if len(message.ParameterList) > 0:
            if message.ParameterList[0].lower() in GlobalVars.commandCaseMapping:
                func = GlobalVars.commands[GlobalVars.commandCaseMapping[message.ParameterList[0].lower()]]
                if isinstance(func.help, basestring):
                    return IRCResponse(ResponseType.Say, func.help, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, func.help(message), message.ReplyTo)
            else:
                return IRCResponse(ResponseType.Say, '"%s" not found, try "%s" without parameters to see a list of loaded function names' % (message.ParameterList[0], message.Command), message.ReplyTo)
        else:
            funcs = ', '.join(sorted(GlobalVars.commands.iterkeys(), key=lambda s: s.lower()))
            return [IRCResponse(ResponseType.Say, "Commands loaded are:", message.ReplyTo),
                    IRCResponse(ResponseType.Say, funcs, message.ReplyTo)]

