# -*- coding: utf-8 -*-
from collections import OrderedDict
from html.entities import name2codepoint
from builtins import chr
from six import iteritems
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
# https://github.com/ElementalAlchemist/txircd/blob/99e86d53f1fa43e0916497edd08ee3f34f69c4b0/txircd/utils.py#L218
# \x02: bold
# \x1f: underline
# \x16: reverse
# \x1d: italic
# \x0f: normal
# \x03: color stop
# \x03FF: set foreground
# \x03FF,BB: set fore/background
format_chars = re.compile(r'[\x02\x1f\x16\x1d\x0f]|\x03([0-9]{1,2}(,[0-9]{1,2})?)?')
def stripFormatting(message):
    """
    Removes IRC formatting from the provided message.
    """
    return format_chars.sub('', message)


# mostly taken from dave_random's UnsafeBot (whose source is not generally accessible)
def deltaTimeToString(timeDelta, resolution='m'):
    """
    returns a string version of the given timedelta, with a resolution of minutes ('m') or seconds ('s')
    @type timeDelta: timedelta
    @type resolution: str
    """
    d = OrderedDict()
    d['days'] = timeDelta.days
    d['hours'], rem = divmod(timeDelta.seconds, 3600)
    if resolution == 'm' or resolution == 's':
        d['minutes'], seconds = divmod(rem, 60)
        if resolution == 's':
            d['seconds'] = seconds

    def lex(durationWord, duration):
        if duration == 1:
            return '{0} {1}'.format(duration, durationWord[:-1])
        else:
            return '{0} {1}'.format(duration, durationWord)

    deltaString = ' '.join([lex(word, number) for word, number in iteritems(d) if number > 0])
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
                    return chr(int(escapeText[3:-1], 16))
                else:
                    return chr(int(escapeText[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                escapeText = chr(name2codepoint[escapeText[1:-1]])
            except KeyError:
                pass
        return escapeText  # leave as is
    return re.sub('&#?\w+;', fixup, text)
