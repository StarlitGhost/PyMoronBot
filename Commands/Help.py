from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import GlobalVars

import re

class Command(CommandInterface):
    triggers = ['help','command','commands']
    help = 'help/command(s) (<module>) - returns a list of loaded command modules, or the help text of a particular module if one is specified'
    
    def execute(self, message):
        if len(message.ParameterList) > 0:
            if message.ParameterList[0].lower() in GlobalVars.commandCaseMapping:
                func = GlobalVars.commands[GlobalVars.commandCaseMapping[message.ParameterList[0].lower()]]
                if isinstance(func.help, basestring):
                    return IRCResponse(ResponseType.Say, func.help, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, func.help(message), message.ReplyTo)
            else:
                return IRCResponse(ResponseType.Say, '"%s" not found, try "%s" without parameters to see a list of loaded module names' % (message.ParameterList[0], message.Command), message.ReplyTo)
        else:
            funcs = ', '.join(sorted(GlobalVars.commands.iterkeys(), key=lambda s: s.lower()))
            return [IRCResponse(ResponseType.Say, "Command modules loaded are (use 'help <module>' to get help for that module):", message.ReplyTo),
                    IRCResponse(ResponseType.Say, funcs, message.ReplyTo)]

