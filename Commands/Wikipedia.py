# -*- coding: utf-8 -*-
import json
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

import re
import urllib
from Utils import StringUtils, WebUtils


class Wikipedia(CommandInterface):
    triggers = ['wiki', 'wikipedia']
    help = 'wiki(pedia) <search term> - returns the top result for a given search term from wikipedia'
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        try:
            query = 'site:en.wikipedia.org {0}'.format(message.Parameters)
            results = WebUtils.googleSearch(query)

            firstResult = results['responseData']['results'][0]
            
            title = firstResult['titleNoFormatting']
            content = firstResult['content']
            content = re.sub(r'<.*?>', '', content)  # strip html tags
            content = re.sub(r'\s+', ' ', content)  # replace multiple spaces with single ones (includes newlines?)
            content = StringUtils.unescapeXHTML(content)
            url = firstResult['url']
            replyText = u'{1}{0}{2}{0}{3}'.format(StringUtils.graySplitter, title, content, url)
            
            return IRCResponse(ResponseType.Say, replyText, message.ReplyTo)
        except Exception, x:
            print str(x)
            return IRCResponse(ResponseType.Say, x.args, message.ReplyTo)
