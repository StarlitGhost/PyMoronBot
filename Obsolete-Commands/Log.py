import datetime
import subprocess

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from Utils import StringUtils
import dateutil.parser as dparser


class Command(CommandInterface):
    triggers = ['log']
    help = "log (<-n>/<date>) - gives you a link to today's log, the log from -n days ago, " \
           "or the log for the specified date"

    def execute(self, message=IRCMessage, bot=MoronBot):

        date = datetime.datetime.utcnow()
        if len(message.ParameterList) == 1:
            if StringUtils.isNumber(message.ParameterList[0]):
                date += datetime.timedelta(days=int(message.ParameterList[0]))
            else:
                try:
                    date = dparser.parse(message.ParameterList[0], fuzzy=True, dayfirst=True)
                except ValueError:
                    pass

        proc = subprocess.Popen(['/usr/bin/php',
                                 '/home/ubuntu/moronbot/getloghash.php',
                                 message.ReplyTo + "-" + date.strftime('%Y%m%d')],
                                stdout=subprocess.PIPE)
        hash = proc.stdout.read()
        if hash == "Not found":
            output = "I don't have that log."
        else:
            output = "Log for " + date.strftime('%Y/%m/%d') + ": http://www.moronic-works.co.uk/logs/?l=" + hash
            return IRCResponse(ResponseType.Say, output, message.ReplyTo)
