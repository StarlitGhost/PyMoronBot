# -*- coding: utf-8 -*-
"""
Created on Nov 07, 2014
@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface


class Flip(CommandInterface):
    triggers = ['flip']
    help = 'flip <text> - flips the text given to it'

    def onLoad(self):
        table = {
            'a': 'ɐ',    'A': '∀',
            'b': 'q',    'B': '8',
            'c': 'ɔ',    'C': 'Ↄ',
            'd': 'p',    'D': '◖',
            'e': 'ǝ',    'E': 'Ǝ',
            'f': 'ɟ',    'F': 'Ⅎ',
            'g': 'ƃ',    'G': '⅁',
            'h': 'ɥ',    'H': 'H',
            'i': 'ı',    'I': 'I',
            'j': 'ɾ',    'J': 'ſ',
            'k': 'ʞ',    'K': '⋊',
            'l': 'ʃ',    'L': '⅂',
            'm': 'ɯ',    'M': 'W',
            'n': 'u',    'N': 'ᴎ',
            'o': 'o',    'O': 'O',
            'p': 'd',    'P': 'Ԁ',
            'q': 'b',    'Q': 'Ό',
            'r': 'ɹ',    'R': 'ᴚ',
            's': 's',    'S': 'S',
            't': 'ʇ',    'T': '⊥',
            'u': 'n',    'U': '∩',
            'v': 'ʌ',    'V': 'ᴧ',
            'w': 'ʍ',    'W': 'M',
            'x': 'x',    'X': 'X',
            'y': 'ʎ',    'Y': '⅄',
            'z': 'z',    'Z': 'Z',
            '0': '0',
            '1': '1',
            '2': '2',
            '3': 'Ɛ',
            '4': 'ᔭ',
            '5': '5',
            '6': '9',
            '7': 'Ɫ',
            '8': 'B',
            '9': '6',
            '.': '˙',
            ',': "'",
            "'": ',',
            '"': '„',
            '!': '¡',
            '?': '¿'
        }
        # Create and append the inverse dictionary
        table.update({v: k for k,v in table.iteritems()})
        self.translation = maketrans(''.join(table.keys()), ''.join(table.values()))

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 0:
            translated = message.Parameters.translate(self.translation)
            reversed = translated[::-1]
            return IRCResponse(ResponseType.Say, reversed, message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say, 'Flip what?', message.ReplyTo)

