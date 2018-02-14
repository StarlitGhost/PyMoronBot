# -*- coding: utf-8 -*-
from enum import Enum
from builtins import str


class ResponseType(Enum):
    Say = 1
    Do = 2
    Notice = 3
    Raw = 4


class IRCResponse(object):
    Type = ResponseType.Say
    Response = ''
    Target = ''

    def __init__(self, messageType, response, target, extraVars=None, metadata=None):
        """
        @type messageType: ResponseType
        @type response: unicode
        @type target: unicode
        @type extraVars: dict
        @type metadata: dict
        """
        if extraVars is None:
            extraVars = {}
        if metadata is None:
            metadata = {}
        self.Type = messageType
        try:
            self.Response = str(response, 'utf-8')
        except TypeError:  # Already utf-8?
            self.Response = response
        try:
            self.Target = str(target, 'utf-8')
        except TypeError:  # Already utf-8?
            self.Target = target

        # remove CTCP chars
        if not self.Type == ResponseType.Raw:
            self.Response = self.Response.replace('\x01', '')

        self.ExtraVars = extraVars
        self.Metadata = metadata
