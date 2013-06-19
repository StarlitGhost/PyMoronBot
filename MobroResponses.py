from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from GlobalVars import *

import re

import datetime

class MobroResponse:
    lastTriggered = datetime.datetime.min

    def __init__(self, name, response, regex, responseType = ResponseType.Say, enabled = True, seconds = 300, regexMustAllMatch = True):
        self.name = name
        self.response = response
        self.regex = regex
        self.enabled = enabled
        self.seconds = seconds
        self.mustAllMatch = regexMustAllMatch
        self.responseType = responseType

    #overwrite this with your own match(message) function if a response calls for different logic
    def match(self,message):
        if isinstance(self.regex,str):
            self.regex = [self.regex]
        for regex in self.regex:
            if re.search(regex, message, re.IGNORECASE):
                if not self.mustAllMatch:
                    return True
            elif self.mustAllMatch:
                return False
        return self.mustAllMatch

    def eligible(self,message):
        return self.enabled and (datetime.datetime.utcnow() - self.lastTriggered).seconds >= self.seconds and self.match(message)

    def chat(self,saywords,chatMessage):
        return IRCResponse(self.responseType,saywords,chatMessage.ReplyTo)

    def toggle(self,chatMessage):
        self.enabled = not self.enabled
        return self.chat("Response '%s' %s" % (self.name, {True:"Enabled",False:"Disabled"}[self.enabled]), chatMessage)

    #overwrite this with your own talkwords(IRCMessage) function if a response calls for it
    def talkwords(self, chatMessage):
        if isinstance(self.response,str):
            self.response = [self.response]
        responses = []
        for response in self.response:
            responses.append(self.chat(response, chatMessage))
        return responses

    def trigger(self,chatMessage):
        if self.eligible(chatMessage.MessageString):
            self.lastTriggered = datetime.datetime.utcnow()
            return self.talkwords(chatMessage)


class MobroResponseDict:
    dict = {}

    def add(self,mbr):
        self.dict[mbr.name] = mbr

    def toggle(self,name,chatMessage):
        if name in self.dict:
            return self.dict[name].toggle(chatMessage)
        return
