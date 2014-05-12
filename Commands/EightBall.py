"""
Created on Aug 14, 2013

@author: Tyranic-Moron
"""

import random

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from moronbot import MoronBot


class EightBall(CommandInterface):
    triggers = ['8ball']
    help = '8ball (question) - swirls a magic 8-ball to give you the answer to your questions'

    def execute(self, message=IRCMessage, bot=MoronBot):
        answers = ['It is certain',  # positive
                   'It is decidedly so',
                   'Without a doubt',
                   'Yes definitely',
                   'You may rely on it',
                   'As I see it yes',
                   'Most likely',
                   'Outlook good',
                   'Yes',
                   'Signs point to yes',

                   'Reply hazy try again',  # non-committal
                   'Ask again later',
                   'Better not tell you now',
                   'Cannot predict now',
                   'Concentrate and ask again',

                   "Don't count on it",  # negative
                   'My reply is no',
                   'My sources say no',
                   'Outlook not so good',
                   'Very doubtful']

        return IRCResponse(ResponseType.Say,
                           'The Magic 8-ball says... {0}'.format(random.choice(answers)),
                           message.ReplyTo)
