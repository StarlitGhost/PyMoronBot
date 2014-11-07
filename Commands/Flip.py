# -*- coding: utf-8 -*-
"""
Created on Nov 07, 2014
@author: Tyranic-Moron
"""

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

from string import maketrans

class Flip(CommandInterface):
    triggers = ['flip']
    help = 'flip <text> - flips the text given to it'

    def onLoad(self):
        table = {
            u'a': u'ɐ',    u'A': u'∀',
            u'b': u'q',    u'B': u'ᗺ',
            u'c': u'ɔ',    u'C': u'Ↄ',
            u'd': u'p',    u'D': u'◖',
            u'e': u'ǝ',    u'E': u'Ǝ',
            u'f': u'ɟ',    u'F': u'Ⅎ',
            u'g': u'ƃ',    u'G': u'⅁',
            u'h': u'ɥ',    u'H': u'H',
            u'i': u'ı',    u'I': u'I',
            u'j': u'ɾ',    u'J': u'ſ',
            u'k': u'ʞ',    u'K': u'⋊',
            u'l': u'ʃ',    u'L': u'⅂',
            u'm': u'ɯ',    u'M': u'W',
            u'n': u'u',    u'N': u'ᴎ',
            u'o': u'o',    u'O': u'O',
            u'p': u'd',    u'P': u'Ԁ',
            u'q': u'b',    u'Q': u'Ό',
            u'r': u'ɹ',    u'R': u'ᴚ',
            u's': u's',    u'S': u'S',
            u't': u'ʇ',    u'T': u'⊥',
            u'u': u'n',    u'U': u'∩',
            u'v': u'ʌ',    u'V': u'ᴧ',
            u'w': u'ʍ',    u'W': u'M',
            u'x': u'x',    u'X': u'X',
            u'y': u'ʎ',    u'Y': u'⅄',
            u'z': u'z',    u'Z': u'Z',
            u'0': u'0',
            u'1': u'⇂',
            u'2': u'ᘔ',
            u'3': u'Ɛ',
            u'4': u'ᔭ',
            u'5': u'5',
            u'6': u'9',
            u'7': u'Ɫ',
            u'8': u'8',
            u'9': u'6',
            u'.': u'˙',
            u',': u"'",
            u"'": u',',
            u'"': u'„',
            u'!': u'¡',
            u'?': u'¿',
            u'<': u'>',
            u'(': u')',
            u'[': u']',
            u'{': u'}',
            u'_': u'‾',
            u'^': u'∨',
            u';': u'؛'
        }
        # Create and append the inverse dictionary
        table.update({v: k for k,v in table.iteritems()})
        self.translation = {ord(k): v for k,v in table.iteritems()}

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

