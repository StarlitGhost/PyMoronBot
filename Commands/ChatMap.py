# -*- coding: utf-8 -*-
"""
Created on Apr 26, 2013

@author: Tyranic-Moron, Emily
"""

import json

from storm.locals import *

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Utils import StringUtils


class ChatMap(CommandInterface):
    chatMapDB = None

    triggers = ['chatmap', 'map']

    def onLoad(self):
        try:
            with open('Data/ChatMapDB.json', 'r') as f:
                self.chatMapDB = json.load(f)
        except IOError:
            pass

    def add(self, message):
        """add lat,lon - adds a nick to the chat map, or updates if already added"""

        coords = ''.join(message.ParameterList[1:])
        if not ',' in coords:
            return 'lat,lon coords must be comma separated'
        (lat, lon) = coords.split(',')
        if not StringUtils.isNumber(lat) or not StringUtils.isNumber(lon):
            return 'latitude or longitude are not numeric'

        (lat, lon) = float(lat), float(lon)

        if not -90.0 < lat < 90.0:
            return 'latitude is outside valid range (-90 -> 90)'
        if not -180.0 < lon < 180.0:
            return 'longitude is outside valid range (-180 -> 180)'

        db = create_database("mysql://{0}:{1}@{2}:{3}/{4}".format(self.chatMapDB['User'],
                                                                  self.chatMapDB['Password'],
                                                                  self.chatMapDB['Host'],
                                                                  3306,
                                                                  self.chatMapDB['DB']))
        store = Store(db)

        result = store.execute("SELECT nick, latitude, longitude FROM " + self.chatMapDB['Table'] + " WHERE nick=%s",
                               [message.User.Name])

        response = 'There has been a fatal error updating your GPS coordinates. Please contact Emily to let her know.'

        if result.rowcount == 1:
            result = store.execute("UPDATE " + self.chatMapDB['Table'] + " SET latitude=%s, longitude=%s WHERE nick=%s",
                                   [lat, lon, message.User.Name])
            if result:
                response = 'Your chatmap position has been updated with the new GPS coordinates!'

        elif result.rowcount == 0:
            result = store.execute(
                "INSERT INTO " + self.chatMapDB['Table'] + " (nick, latitude, longitude) VALUES(%s, %s, %s)",
                [message.User.Name, lat, lon])
            if result:
                response = 'You are now on the chatmap at the specified GPS coordinates! ' \
                           'Be sure to do an addYear to add the year you first started as a Survivor!'

        store.close()

        return response

    def addYear(self, message):
        """addYear - updates desert bus year for the user, (first surviving year)"""

        year = ''.join(message.ParameterList[1:])
        if not StringUtils.isNumber(year):
            return 'the desert bus year should only be numeric (1-8)'

        year = int(year)

        if year >= 2010:
            year -= 2006
        if not 4 <= year <= 8:
            return 'the desert bus year should only be for valid years (4 -> 8)'

        db = create_database("mysql://{0}:{1}@{2}:{3}/{4}".format(self.chatMapDB['User'],
                                                                  self.chatMapDB['Password'],
                                                                  self.chatMapDB['Host'],
                                                                  3306,
                                                                  self.chatMapDB['DB']))
        store = Store(db)

        result = store.execute("SELECT nick, dbyear FROM " + self.chatMapDB['Table'] + " WHERE nick=%s",
                               [message.User.Name])

        response = 'There has been a fatal error updating your Desert Bus Year. Please contact Emily to let her know.'

        if result.rowcount == 1:
            result = store.execute("UPDATE " + self.chatMapDB['Table'] + " SET dbyear=%s WHERE nick=%s",
                                   [year, message.User.Name])
            if result:
                response = 'Your desert bus year has been updated with your information!'

        elif result.rowcount == 0:
            response = 'You do not currently have a chatmap record, please use add lat,lon first.'

        store.close()

        return response

    def delete(self, message):
        """del - deletes a nick from the chat map"""

        db = create_database("mysql://{0}:{1}@{2}:{3}/{4}".format(self.chatMapDB['User'],
                                                                  self.chatMapDB['Password'],
                                                                  self.chatMapDB['Host'],
                                                                  3306,
                                                                  self.chatMapDB['DB']))
        store = Store(db)

        result = store.execute("SELECT nick, latitude, longitude FROM " + self.chatMapDB['Table'] + " WHERE nick=%s",
                               [message.User.Name])

        if result.rowcount == 1:
            result = store.execute("DELETE FROM " + self.chatMapDB['Table'] + " WHERE nick=%s", [message.User.Name])

            if result:
                response = 'Your chatmap record has been deleted!'
            else:
                response = "Something weird happened and I didn't delete your chatmap record. " \
                           "Someone tell my owner!"

        elif result.rowcount == 0:
            response = 'You do not currently have a chatmap record, and therefore cannot be deleted.'

        else:
            response = 'It seems like I just deleted a bunch of chatmap records with the same name! ' \
                       'Someone tell my owner!'

        store.close()

        return response

    subCommands = {'add': add, 'del': delete, 'addyear': addYear}

    def help(self, message):
        subCommand = None
        if len(message.ParameterList) > 1:
            subCommand = message.ParameterList[1].lower()
        if subCommand is not None:
            if subCommand in self.subCommands:
                return 'chatmap {0}'.format(self.subCommands[subCommand].__doc__)
            else:
                return self.unrecognizedSubcommand(subCommand)
        else:
            return "{1}chatmap ({0}) - where are the people of #DesertBus? " \
                   "Links to a Chat Map using the Google Maps API. " \
                   "Use '{1}help chatmap <subcommand>' for subcommand help. " \
                   "You can use '{1}gpslookup <address>' via PM to find your lat,lon coords".format(
                '/'.join(self.subCommands.keys()), self.bot.commandChar)

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 0:
            subCommand = message.ParameterList[0].lower()
            if subCommand not in self.subCommands:
                return IRCResponse(ResponseType.Say, self.unrecognizedSubcommand(subCommand), message.ReplyTo)

            if self.chatMapDB is None:
                return IRCResponse(ResponseType.Say, '[Chatmap database details not found]', message.ReplyTo)

            response = self.subCommands[subCommand](self, message)

            return IRCResponse(ResponseType.Say, response, message.ReplyTo)

        else:
            return IRCResponse(ResponseType.Say,
                               'The Wonderful World of #desertbus People! http://www.tsukiakariusagi.net/chatmap.php',
                               message.ReplyTo)

    def unrecognizedSubcommand(self, subCommand):
        return 'unrecognized subcommand \'{0}\', ' \
               'available subcommands for chatmap are: {1}'.format(subCommand, ', '.join(self.subCommands.keys()))
