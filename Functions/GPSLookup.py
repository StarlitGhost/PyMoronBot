'''
Created on Oct 09, 2013

@author: Tyranic-Moron
'''

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *

import WebUtils
from Data.api_keys import load_key

import re, json, urllib

class Instantiate(Function):
    
    Help = "gps(lookup) <address> - Uses Microsoft's Bing Maps geocoding API to lookup GPS coordinates for the given address. Must be used over PM"

    def __init__(self):
        self.api_key = load_key(u'Bing Maps')

    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^gps(lookup)?$', message.Command, re.IGNORECASE)
        if not match:
            return

        if message.User.Name != message.ReplyTo:
            return IRCResponse(ResponseType.Say, "GPS Lookup must be done via PM", message.ReplyTo)
        
        if len(message.ParameterList) > 0:
            if self.api_key is None:
                return IRCResponse(ResponseType.Say, "[Bing Maps API key not found]", message.ReplyTo)

            url = "http://dev.virtualearth.net/REST/v1/Locations?q={0}&key={1}".format(urllib.quote_plus(message.Parameters), self.api_key)

            j = WebUtils.SendToServer(url)
            result = json.loads(j)

            if result['resourceSets'][0]['estimatedTotal'] == 0:
                print result
                return IRCResponse(ResponseType.Say, "Couldn't find GPS coords for '{0}', sorry!".format(message.Parameters), message.ReplyTo)

            coords = result['resourceSets'][0]['resources'][0]['point']['coordinates']

            return IRCResponse(ResponseType.Say,
                               "GPS coords for '{0}' are: {1},{2}".format(message.Parameters, coords[0], coords[1]),
                               message.ReplyTo)

        else:
            return IRCResponse(ResponseType.Say,
                               "You didn't give an address to look up",
                               message.ReplyTo)
