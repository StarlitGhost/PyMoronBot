# -*- coding: utf-8 -*-
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import re
import urllib
import urllib2

import htmlentitydefs


# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
def unescape(text):
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


class Wikipedia(CommandInterface):
    triggers = ['wiki', 'wikipedia']
    help = 'wiki(pedia) <search term> - returns the top result for a given search term from wikipedia'
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        article = message.Parameters
        article = urllib.quote(article)
        
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        
        try:
            page = opener.open('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=site:en.wikipedia.org%20' + article)
            data = page.read()
            page.close()
            
            title = re.search('"titleNoFormatting":"(?P<title>[^"]+)', data).group('title').decode('utf-8')
            title = title[:-35]
            content = re.search('"content":"(?P<content>[^"]+)', data).group('content').decode('unicode-escape')
            content = re.sub('<.*?>', '', content)
            content = re.sub('\s+', ' ', content)
            content = unescape(content)
            url = re.search('"url":"(?P<url>[^"]+)', data).group('url')
            replyText = '%s | %s | %s' % (title, content, url)
            
            return IRCResponse(ResponseType.Say, replyText, message.ReplyTo)
        except Exception, x:
            print str(x)
            return IRCResponse(ResponseType.Say, x.args, message.ReplyTo)
