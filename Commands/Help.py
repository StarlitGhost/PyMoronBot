from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
import GlobalVars


class Command(CommandInterface):
    triggers = ['help', 'command', 'commands']
    help = 'help/command(s) (<module>) - returns a list of loaded command modules, ' \
           'or the help text of a particular module if one is specified'

    def execute(self, message=IRCMessage):
        if len(message.ParameterList) > 0:
            if message.ParameterList[0].lower() in GlobalVars.commandCaseMapping:
                func = GlobalVars.commands[GlobalVars.commandCaseMapping[message.ParameterList[0].lower()]]
                if isinstance(func.help, basestring):
                    return IRCResponse(ResponseType.Say, func.help, message.ReplyTo)
                else:
                    return IRCResponse(ResponseType.Say, func.help(message), message.ReplyTo)
            else:
                return IRCResponse(ResponseType.Say,
                                   '"{0}" not found, try "{1}" without parameters '
                                   'to see a list of loaded module names'.format(message.ParameterList[0],
                                                                                 message.Command),
                                   message.ReplyTo)
        else:
            funcs = ', '.join(sorted(GlobalVars.commands.iterkeys(), key=lambda s: s.lower()))
            return [IRCResponse(ResponseType.Say,
                                "Command modules loaded are (use 'help <module>' to get help for that module):",
                                message.ReplyTo),
                    IRCResponse(ResponseType.Say,
                                funcs,
                                message.ReplyTo)]
