'''
Created on Apr 26, 2013

@author: Tyranic-Moron, Emily
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import re, json

from storm.locals import *

import StringUtils

class Instantiate(Function):

    ChatMapDB = None

    def __init__(self):
        try:
            with open('Data/ChatMapDB.json', 'r') as f:
                self.ChatMapDB = json.load(f)
        except IOError:
            pass

    def add(self, message):
        """add lat,lon - adds a nick to the chat map, or updates if already added"""

        coords = ''.join(message.ParameterList[1:])
        if not ',' in coords:
            return 'lat,lon coords must be comma separated'
        (lat,lon) = coords.split(',')
        if not StringUtils.is_number(lat) or not StringUtils.is_number(lon):
            return 'latitude or longitude are not numeric'

        (lat,lon) = float(lat),float(lon)

        if not -90.0 < lat < 90.0:
            return 'latitude is outside valid range (-90 -> 90)'
        if not -180.0 < lon < 180.0:
            return 'longitude is outside valid range (-180 -> 180)'

        db = create_database("mysql://{0}:{1}@{2}:{3}/{4}".format(self.ChatMapDB['User'],
                                                                  self.ChatMapDB['Password'],
                                                                  self.ChatMapDB['Host'],
                                                                  3306,
                                                                  self.ChatMapDB['DB']))
        store = Store(db)

        result = store.execute("SELECT nick, latitude, longitude FROM " + self.ChatMapDB['Table'] + " WHERE nick=%s", [message.User.Name])

        response = 'There has been a fatal error updating your GPS coordinates. Please contact Emily to let her know.'

        if result.rowcount == 1:
            result = store.execute("UPDATE " + self.ChatMapDB['Table'] + " SET latitude=%s, longitude=%s WHERE nick=%s", [lat, lon, message.User.Name])
            if result:
                response = 'Your chatmap position has been updated with the new GPS coordinates!'

        elif result.rowcount == 0:
            result = store.execute("INSERT INTO " + self.ChatMapDB['Table'] + " (nick, latitude, longitude) VALUES(%s, %s, %s)", [message.User.Name, lat, lon])
            if result:
                response = 'You are now on the chatmap at the specified GPS coordinates!  Be sure to do an addYear to add the year you first started as a Survivor!'

        store.close()

        return response

    def addYear(self, message):
        """addYear - updates desert bus year for the user, (first surviving year)"""

        year = ''.join(message.ParameterList[1:])
        if not StringUtils.is_number(year):
            return 'the desert bus year should only be numeric (1-7)'

        year = int(year)

        if not -1 < year < 8:
            return 'the desert bus year should only be for valid years (1 -> 7)'

        db = create_database("mysql://{0}:{1}@{2}:{3}/{4}".format(self.ChatMapDB['User'],
                                                                  self.ChatMapDB['Password'],
                                                                  self.ChatMapDB['Host'],
                                                                  3306,
                                                                  self.ChatMapDB['DB']))
        store = Store(db)

        result = store.execute("SELECT nick, dbyear FROM " + self.ChatMapDB['Table'] + " WHERE nick=%s", [message.User.Name])

        response = 'There has been a fatal error updating your Desert Bus Year. Please contact Emily to let her know.'

        if result.rowcount == 1:
            result = store.execute("UPDATE " + self.ChatMapDB['Table'] + " SET dbyear=%s, WHERE nick=%s", [year, message.User.Name])
            if result:
                response = 'Your desert bus year has been updated with your information!'

        store.close()

        return response

    def delete(self, message):
        """del - deletes a nick from the chat map"""

        db = create_database("mysql://{0}:{1}@{2}:{3}/{4}".format(self.ChatMapDB['User'],
                                                                  self.ChatMapDB['Password'],
                                                                  self.ChatMapDB['Host'],
                                                                  3306,
                                                                  self.ChatMapDB['DB']))
        store = Store(db)

        result = store.execute("SELECT nick, latitude, longitude FROM " + self.ChatMapDB['Table'] + " WHERE nick=%s", [message.User.Name])

        if result.rowcount == 1:
            result = store.execute("DELETE FROM " + self.ChatMapDB['Table'] + " WHERE nick=%s", [message.User.Name])

            if result:
                response = 'Your chatmap record has been deleted!'

        elif result.rowcount == 0:
            return 'You do not currently have a chatmap record, and therefore cannot be deleted.'

        store.close()

        return response

    subCommands = {'add': add, 'del': delete, 'addYear': addYear}

    def Help(self, message):
        subCommand = None
        if len(message.ParameterList) > 1:
            subCommand = message.ParameterList[1]
        if subCommand is not None:
            if subCommand in self.subCommands:
                return 'chatmap {0}'.format(self.subCommands[subCommand].__doc__)
            else:
                return self.UnrecognizedSubcommand(subCommand)
        else:
            return 'chatmap ({0}) - where are the people of #DesertBus? Links to a Chat Map using the Google Maps API'.format('/'.join(self.subCommands.keys()))

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^(chat)?map$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        subCommand = None
        if len(message.ParameterList) > 0:
            subCommand = message.ParameterList[0]
            if subCommand not in self.subCommands:
                return IRCResponse(ResponseType.Say, self.UnrecognizedSubcommand(subCommand), message.ReplyTo)
            
            response = self.subCommands[message.ParameterList[0]](self, message)

            return IRCResponse(ResponseType.Say, response, message.ReplyTo)

        else:
            return IRCResponse(ResponseType.Say,
                               'The Wonderful World of #desertbus People! http://www.tsukiakariusagi.net/chatmap.php',
                               message.ReplyTo)

    def UnrecognizedSubcommand(self, subCommand):
        return 'unrecognized subcommand \'{0}\', available subcommands for chatmap are: {1}'.format(subCommand, ', '.join(self.subCommands.keys()))
