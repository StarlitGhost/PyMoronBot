from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
import WebUtils

import re
import urllib
import json

class Command(CommandInterface):
    triggers = ['define','def']
    help = "define <word> - Fetches the dictionary definition of the given word from Google"
    
    def execute(self, message):
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, 'Define what?', message.ReplyTo)
        
        query = urllib.quote(message.Parameters.encode('utf8'))
        url = 'http://www.google.com/dictionary/json?callback=a&sl=en&tl=en&q={0}'.format(query)
        j = WebUtils.SendToServer(url)
        j = j[2:]
        j = j[:-10]
        j = j.decode('string_escape')
        j = re.sub(r'</?[^>]+?>', '', j)
        defs = json.loads(j)
        
        numDefs = 0
        defsToDisp = 3
        responses = [IRCResponse(ResponseType.Say, 'Definitions for {0}:'.format(message.Parameters), message.ReplyTo)]
        defToDispIf = None
        for wordType in defs['primaries']:
            for definition in wordType['entries']:
                if definition['type'] == 'meaning':
                    numDefs += 1
                    if numDefs <= defsToDisp:
                        responses.append(IRCResponse(ResponseType.Say, '{0}. {1}'.format(numDefs, definition['terms'][0]['text']), message.ReplyTo))
                    if numDefs == defsToDisp+1:
                        defToDispIf = IRCResponse(ResponseType.Say, '{0}. {1}'.format(numDefs, definition['terms'][0]['text']), message.ReplyTo)
        if numDefs > defsToDisp+1:
            responses.append(IRCResponse(ResponseType.Say, 'And {1} more here: www.google.com/#tbs=dfn:1&q={0}'.format(query, numDefs-defsToDisp), message.ReplyTo))
        elif numDefs == defsToDisp+1:
            responses.append(defToDispIf)
                    
        if numDefs == 0:
            return IRCResponse(ResponseType.Say, 'No definitions found for {0}'.format(message.Parameters), message.ReplyTo)
        
        return responses

