"""
Created on May 04, 2014

@author: Tyranic-Moron
"""

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType

from twisted.words.protocols.irc import assembleFormattedText, attributes as A


class Command(CommandInterface):
    triggers = ['rainbow']
    help = 'rainbow <text> - outputs the specified text with rainbow colours'

    colours = [assembleFormattedText(A.fg.lightRed['']),
               #assembleFormattedText(A.fg.orange['']),
               assembleFormattedText(A.fg.yellow['']),
               assembleFormattedText(A.fg.lightGreen['']),
               assembleFormattedText(A.fg.lightCyan['']),
               assembleFormattedText(A.fg.lightBlue['']),
               assembleFormattedText(A.fg.lightMagenta['']),
               ]

    def execute(self, message=IRCMessage):
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, "You didn't give me any text to rainbow!", message.ReplyTo)

        outputMessage = ''

        for i, c in enumerate(message.Parameters):
            outputMessage += self.colours[i % len(self.colours)] + c

        outputMessage += assembleFormattedText(A.normal[''])

        return IRCResponse(ResponseType.Say, outputMessage, message.ReplyTo)
