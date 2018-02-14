# -*- coding: utf-8 -*-
from twisted.internet import reactor, protocol

from pymoronbot.moronbot import MoronBot


class MoronBotFactory(protocol.ReconnectingClientFactory):
    def __init__(self, config):
        """
        @type config: Config
        """
        self.bot = MoronBot(self, config)
        self.protocol = self.bot

        self.server = config['server']
        self.port = config.getWithDefault('port', 6667)

        reactor.connectTCP(self.server, self.port, self)
        reactor.run()

    def startedConnecting(self, connector):
        print('-#- Started to connect.')

    def buildProtocol(self, addr):
        print('-#- Connected.')
        print('-#- Resetting reconnection delay')
        self.resetDelay()
        return self.bot

    def clientConnectionLost(self, connector, reason):
        if not self.bot.quitting:
            print('-!- Lost connection.  Reason:', reason)
            protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('-!- Connection failed. Reason:', reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)