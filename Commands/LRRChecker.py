import datetime
import xml.etree.ElementTree as ET

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from moronbot import MoronBot

import Data.LRRChecker as DataStore
from Utils import WebUtils

import dateutil.parser as dparser


class LRRChecker(CommandInterface):
    help = "Automatic function, scans LRR video RSS feeds and reports new items in the channel."
    runInThread = True

    def shouldExecute(self, message=IRCMessage, bot=MoronBot):
        return True

    def execute(self, message=IRCMessage, bot=MoronBot):
        responses = []
        for feedName, feedDeets in DataStore.LRRChecker.iteritems():
            if feedDeets['lastCheck'] > datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                continue
            
            DataStore.LRRChecker[feedName]['lastCheck'] = datetime.datetime.utcnow()
            
            feedPage = WebUtils.fetchURL(feedDeets['url'])
            
            if feedPage is None:
                #TODO: log an error here that the feed likely no longer exists!
                continue
            
            root = ET.fromstring(feedPage.Page)
            item = root.find('channel/item')
            
            if item is None:
                #TODO: log an error here that the feed likely no longer exists!
                continue

            title = DataStore.LRRChecker[feedName]['lastTitle'] = item.find('title').text
            link = DataStore.LRRChecker[feedName]['lastLink'] = WebUtils.shortenGoogl(item.find('link').text)
            newestDate = dparser.parse(item.find('pubDate').text, fuzzy=True, ignoretz=True)
            
            if newestDate > feedDeets['lastUpdate']:
                DataStore.LRRChecker[feedName]['lastUpdate'] = newestDate
                
                if feedDeets['suppress']:
                    DataStore.LRRChecker[feedName]['suppress'] = False
                else:
                    response = 'New {0}! Title: {1} | {2}'.format(feedName, title, link)
                    responses.append(IRCResponse(ResponseType.Say, response, '#desertbus'))
            
        return responses
