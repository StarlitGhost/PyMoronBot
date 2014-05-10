from enumType import enum

ResponseType = enum('Say', 'Do', 'Notice', 'Raw')


class IRCResponse(object):
    def __init__(self, messageType, response, target, extraVars=None):
        if extraVars is None:
            extraVars = {}
        self.Type = messageType
        try:
            self.Response = unicode(response, 'utf-8')
        except TypeError:  # Already utf-8?
            self.Response = response
        self.Target = target

        self.ExtraVars = extraVars
