# -*- coding: utf-8 -*-
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.moduleinterface import ModuleInterface

tang = {'A': 'ALPHA',
        'B': 'BRAVO',
        'C': 'CHARLIE',
        'D': 'DELTA',
        'E': 'ECHO',
        'F': 'FOXTROT',
        'G': 'GOLF',
        'H': 'HOTEL',
        'I': 'INDIA',
        'J': 'JULIET',
        'K': 'KILO',
        'L': 'LIMA',
        'M': 'MIKE',
        'N': 'NOVEMBER',
        'O': 'OSCAR',
        'P': 'PAPA',
        'Q': 'QUEBEC',
        'R': 'ROMEO',
        'S': 'SIERRA',
        'T': 'TANGO',
        'U': 'UNIFORM',
        'V': 'VICTOR',
        'W': 'WHISKEY',
        'X': 'XRAY',
        'Y': 'YANKEE',
        'Z': 'ZULU',
        '1': 'ONE',
        '2': 'TWO',
        '3': 'THREE',
        '4': 'FOUR',
        '5': 'FIVE',
        '6': 'SIX',
        '7': 'SEVEN',
        '8': 'EIGHT',
        '9': 'NINER',
        '0': 'ZERO',
        '-': 'DASH'}


class Tango(ModuleInterface):
    triggers = ['tango']
    help = 'tango <words> - reproduces <words> with the NATO phonetic alphabet, because reasons.'

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:
            return

        response = ' '.join(tang[letter.upper()] if letter.upper() in tang else letter for letter in message.Parameters)
        return IRCResponse(ResponseType.Say,
                           response,
                           message.ReplyTo)
