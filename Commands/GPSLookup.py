# -*- coding: utf-8 -*-
"""
Created on Oct 09, 2013

@author: Tyranic-Moron
"""

import json
import urllib

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType

from Data.api_keys import load_key
from Utils import WebUtils


class GPSLookup(CommandInterface):
    triggers = ['gps', 'gpslookup']
    help = "gps(lookup) <address> - Uses Microsoft's Bing Maps geocoding API to " \
           "lookup GPS coordinates for the given address. Must be used over PM"

    def onLoad(self):
        self.api_key = load_key(u'Bing Maps')

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.User.Name != message.ReplyTo:
            return IRCResponse(ResponseType.Say, "GPS Lookup must be done via PM", message.ReplyTo)
        
        if len(message.ParameterList) > 0:
            if self.api_key is None:
                return IRCResponse(ResponseType.Say, "[Bing Maps API key not found]", message.ReplyTo)

            url = "http://dev.virtualearth.net/REST/v1/Locations?q={0}&key={1}".format(urllib.quote_plus(message.Parameters), self.api_key)

            page = WebUtils.fetchURL(url)
            result = json.loads(page.body)

            if result['resourceSets'][0]['estimatedTotal'] == 0:
                print result
                return IRCResponse(ResponseType.Say,
                                   "Couldn't find GPS coords for '{0}', sorry!".format(message.Parameters),
                                   message.ReplyTo)

            coords = result['resourceSets'][0]['resources'][0]['point']['coordinates']

            return IRCResponse(ResponseType.Say,
                               "GPS coords for '{0}' are: {1},{2}".format(message.Parameters, coords[0], coords[1]),
                               message.ReplyTo)

        else:
            return IRCResponse(ResponseType.Say,
                               "You didn't give an address to look up",
                               message.ReplyTo)
