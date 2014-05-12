from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import datetime
import subprocess


class Command(CommandInterface):
    acceptedTypes = ['PRIVMSG', 'ACTION', 'JOIN']
    help = 'Gives Pika a bunch of logs'

    lastMessageDate = datetime.datetime.utcnow()
    lastJoinDate = datetime.datetime.utcnow()

    def shouldExecute(self, message=IRCMessage, bot=MoronBot):
        if message.Type not in self.acceptedTypes:
            return False
        if message.User.Name in ['Pikachaos', 'Raichaos', 'Pika']:
            return True
        return False

    def execute(self, message=IRCMessage, bot=MoronBot):
        now = datetime.datetime.utcnow()
        lastJoin = self.lastJoinDate

        if message.Type in ['PRIVMSG', 'ACTION']:
            self.lastMessageDate = now

        if message.Type != 'JOIN':
            return
        elif (now - lastJoin).total_seconds() < 960:
            self.lastJoinDate = now
            return
        else:
            self.lastJoinDate = now

        date = self.lastMessageDate

        replyTo = message.MessageList[2]

        output = []

        while date < now:
            proc = subprocess.Popen(['/usr/bin/php',
                                     '/home/ubuntu/moronbot/getloghash.php',
                                     replyTo + "-" + date.strftime('%Y%m%d')],
                                    stdout=subprocess.PIPE)
            hash = proc.stdout.read()
            if hash == "Not found":
                output.append(IRCResponse(ResponseType.Say,
                                          "D'aww, no logs for %s found. I guess I was dead for that date :(" % date.strftime('%Y/%m/%d'),
                                          replyTo))
            else:
                output.append(IRCResponse(ResponseType.Say,
                                          "Pika's awesome log funtimes for " + date.strftime('%Y/%m/%d') + "!: http://www.moronic-works.co.uk/logs/?l=" + hash,
                                          replyTo))
            date += datetime.timedelta(days=1)

        return output

