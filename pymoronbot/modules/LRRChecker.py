# -*- coding: utf-8 -*-
import datetime
import xml.etree.ElementTree as ET
from six import iteritems

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.modules.commandinterface import BotCommand

import pymoronbot.utils.LRRChecker as DataStore
from pymoronbot.utils import web

import dateutil.parser as dparser


class LRRChecker(BotCommand):
    help = "Automatic function, scans LRR video RSS feeds and reports new items in the channel."
    runInThread = True

    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        """
        return True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        responses = []
        for feedName, feedDeets in iteritems(DataStore.LRRChecker):
            if feedDeets['lastCheck'] > datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                continue
            
            DataStore.LRRChecker[feedName]['lastCheck'] = datetime.datetime.utcnow()
            
            feedPage = web.fetchURL(feedDeets['url'])
            
            if feedPage is None:
                #TODO: log an error here that the feed likely no longer exists!
                continue
            
            root = ET.fromstring(feedPage.body)
            item = root.find('channel/item')
            
            if item is None:
                #TODO: log an error here that the feed likely no longer exists!
                continue

            title = DataStore.LRRChecker[feedName]['lastTitle'] = item.find('title').text
            link = DataStore.LRRChecker[feedName]['lastLink'] = web.shortenGoogl(item.find('link').text)
            newestDate = dparser.parse(item.find('pubDate').text, fuzzy=True, ignoretz=True)
            
            if newestDate > feedDeets['lastUpdate']:
                DataStore.LRRChecker[feedName]['lastUpdate'] = newestDate
                
                if feedDeets['suppress']:
                    DataStore.LRRChecker[feedName]['suppress'] = False
                else:
                    response = 'New {0}! Title: {1} | {2}'.format(feedName, title, link)
                    responses.append(IRCResponse(ResponseType.Say, response, '#desertbus'))
            
        return responses
