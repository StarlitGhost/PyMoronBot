# -*- coding: utf-8 -*-
from enum import Enum


class ResponseType(Enum):
    Say = 1
    Do = 2
    Notice = 3
    Raw = 4


class IRCResponse(object):
    Type = ResponseType.Say
    Response = ''
    Target = ''

    def __init__(self, messageType, response, target, extraVars=None):
        if extraVars is None:
            extraVars = {}
        self.Type = messageType
        try:
            self.Response = unicode(response, 'utf-8')
        except TypeError:  # Already utf-8?
            self.Response = response
        try:
            self.Target = unicode(target, 'utf-8')
        except TypeError:  # Already utf-8?
            self.Target = target

        self.ExtraVars = extraVars
