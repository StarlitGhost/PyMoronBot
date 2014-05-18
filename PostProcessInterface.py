# -*- coding: utf-8 -*-
from moronbot import MoronBot
from IRCResponse import IRCResponse, ResponseType


class PostProcessInterface(object):
    acceptedTypes = [ResponseType.Say, ResponseType.Do, ResponseType.Notice]
    help = '<no help defined (yet)>'
    runInThread = False
    priority = 0

    def __init__(self, bot):
        """
        @type bot: MoronBot
        """
        self.bot = bot
        self.onLoad()

    def onLoad(self):
        pass

    def onUnload(self):
        pass

    def shouldExecute(self, response):
        """
        @type response: IRCResponse
        """
        if response.Type in self.acceptedTypes:
            return True

    def execute(self, response):
        """
        @type response: IRCResponse
        """
        return response
