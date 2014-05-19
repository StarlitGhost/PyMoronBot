# -*- coding: utf-8 -*-
from collections import OrderedDict
import htmlentitydefs
import re
from twisted.words.protocols.irc import assembleFormattedText, attributes as A


graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])


def isNumber(s):
    """returns True if string s can be cast to a number, False otherwise"""
    try:
        float(s)
        return True
    except ValueError:
        return False


# From this SO answer: http://stackoverflow.com/a/6043797/331047
def splitUTF8(s, n):
    """Split UTF-8 s into chunks of maximum byte length n"""
    while len(s) > n:
        k = n
        while (ord(s[k]) & 0xc0) == 0x80:
            k -= 1
        yield s[:k]
        s = s[k:]
    yield s


# Taken from txircd
# https://github.com/ElementalAlchemist/txircd/blob/889b19cdfedd8f1bb2aa6f23e9a745bdf7330b81/txircd/modules/stripcolor.py#L4
def stripColours(msg):
    """Strip colours (and other formatting) from the given string"""
    while chr(3) in msg:
        color_pos = msg.index(chr(3))
        strip_length = 1
        color_f = 0
        color_b = 0
        comma = False
        for i in range(color_pos + 1, len(msg) if len(msg) < color_pos + 6 else color_pos + 6):
            if msg[i] == ",":
                if comma or color_f == 0:
                    break
                else:
                    comma = True
            elif msg[i].isdigit():
                if color_b == 2 or (not comma and color_f == 2):
                    break
                elif comma:
                    color_b += 1
                else:
                    color_f += 1
            else:
                break
            strip_length += 1
        msg = msg[:color_pos] + msg[color_pos + strip_length:]
    # bold, italic, underline, plain, reverse
    msg = msg.replace(chr(2), "").replace(chr(29), "").replace(chr(31), "").replace(chr(15), "").replace(chr(22), "")
    return msg


# mostly taken from dave_random's UnsafeBot (whose source is not generally accessible)
def deltaTimeToString(timeDelta):
    """
    @type timeDelta: timedelta
    """
    d = OrderedDict()
    d['days'] = timeDelta.days
    d['hours'], rem = divmod(timeDelta.seconds, 3600)
    d['minutes'], _ = divmod(rem, 60)  # replace _ with d['seconds'] to get seconds

    def lex(durationWord, duration):
        if duration == 1:
            return '{0} {1}'.format(duration, durationWord[:-1])
        else:
            return '{0} {1}'.format(duration, durationWord)

    deltaString = ' '.join([lex(word, number) for word, number in d.iteritems() if number > 0])
    return deltaString if len(deltaString) > 0 else 'seconds'


# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
def unescapeXHTML(text):
    def fixup(m):
        escapeText = m.group(0)
        if escapeText[:2] == '&#':
            # character reference
            try:
                if escapeText[:3] == '&#x':
                    return unichr(int(escapeText[3:-1], 16))
                else:
                    return unichr(int(escapeText[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                escapeText = unichr(htmlentitydefs.name2codepoint[escapeText[1:-1]])
            except KeyError:
                pass
        return escapeText  # leave as is
    return re.sub('&#?\w+;', fixup, text)
