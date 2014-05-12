"""
Created on Feb 15, 2013

@author: Emily, Tyranic-Moron
"""

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from moronbot import MoronBot


class Torrent(CommandInterface):
    triggers = ['torrent']
    help = 'torrent - responds with a link to the DB torrents'

    def execute(self, message=IRCMessage, bot=MoronBot):
        return IRCResponse(ResponseType.Say,
                           #'DB6: http://fugiman.com/DesertBus6.torrent | DB5: http://fugiman.com/De5ertBus.torrent',
                           'Torrent Files: http://www.laserdino.com/db7.torrent http://static.fugiman.com/ | '
                           'Magnet Links: http://mgnet.me/.DB7 http://mgnet.me/.DB6 http://mgnet.me/.DB5',
                           message.ReplyTo)
