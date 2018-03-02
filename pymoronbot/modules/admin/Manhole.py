# -*- coding: utf-8 -*-
"""
Created on Dec 07, 2014

@author: Tyranic-Moron
"""
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand, admin
from zope.interface import implementer

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from twisted.conch.manhole_tap import makeService
from twisted.internet.error import CannotListenError
import os


@implementer(IPlugin, IModule)
class Manhole(BotCommand):
    def triggers(self):
        return ['manhole']

    def help(self, query):
        return "A debug module that uses Twisted's Manhole to poke at the bot's innards"

    manhole = None
    port = 4040

    def onLoad(self):
        while self.manhole is None or not self.manhole.running:
            try:
                self.manhole = makeService({
                    "namespace": {"bot": self.bot},
                    "passwd": os.path.join("data", "manhole.passwd"),
                    "telnetPort": None,
                    "sshPort": "tcp:{}:interface=127.0.0.1".format(self.port),
                    "sshKeyDir": os.path.join("data"),
                    "sshKeyName": "manhole.sshkey",
                    "sshKeySize": 4096
                })
                self.manhole.startService()
            except CannotListenError:
                self.port += 1

    def onUnload(self):
        self.manhole.stopService()

    @admin
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        return IRCResponse(ResponseType.Notice, "Manhole port: {}".format(self.port), message.User.Name)


manhole = Manhole()
