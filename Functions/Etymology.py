from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import WebUtils

import re
from bs4 import BeautifulSoup

class Instantiate(Function):
    Help = "etym(ology) <word> - returns the etymology of the given word from etymonline.com"
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('etym(ology)?', message.Command, re.IGNORECASE)
        if not match:
            return
        
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, "You didn't give a word! Usage: {0}".format(self.Help), message.ReplyTo)
        
        word = message.Parameters
        
        webPage = WebUtils.FetchURL('http://www.etymonline.com/index.php?allowed_in_frame=0&search={0}'.format(word))
        root = BeautifulSoup(webPage.Page)
        etymTitle = root.find('dt')
        etymDef = root.find('dd')
        
        if not etymTitle or not etymDef:
            return IRCResponse(ResponseType.Say, "No etymology found for '{0}'".format(word), message.ReplyTo)

        response = "{0}: {1}".format(etymTitle.text.strip(), etymDef.text.strip())
        
        return IRCResponse(ResponseType.Say, response, message.ReplyTo)

