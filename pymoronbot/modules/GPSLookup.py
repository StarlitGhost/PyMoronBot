# -*- coding: utf-8 -*-
"""
Created on Oct 09, 2013

@author: Tyranic-Moron
"""

import json
import urllib

from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils.api_keys import load_key
from pymoronbot.utils import web


class GPSLookup(ModuleInterface):
    triggers = ['gps', 'gpslookup']
    help = "gps(lookup) <address> - Uses Microsoft's Bing Maps geocoding API to " \
           "lookup GPS coordinates for the given address"

    def onLoad(self):
        self.api_key = load_key(u'Bing Maps')

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) > 0:
            if self.api_key is None:
                return IRCResponse(ResponseType.Say, "[Bing Maps API key not found]", message.ReplyTo)

            url = "http://dev.virtualearth.net/REST/v1/Locations?q={0}&key={1}".format(urllib.quote_plus(message.Parameters), self.api_key)

            page = web.fetchURL(url)
            result = json.loads(page.body)

            if result['resourceSets'][0]['estimatedTotal'] == 0:
                print(result)
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
