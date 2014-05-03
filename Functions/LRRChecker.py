from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import Data.LRRChecker as DataStore
import WebUtils

import re, datetime
import xml.etree.ElementTree as ET
import dateutil.parser as dparser

class Instantiate(Function):

    Help = "Automatic function, scans LRR video RSS feeds and reports new items in the channel."

    def GetResponse(self, message):
        responses = []
        for feedName, feedDeets in DataStore.LRRChecker.iteritems():
            if feedDeets['lastCheck'] > datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                continue
            
            DataStore.LRRChecker[feedName]['lastCheck'] = datetime.datetime.utcnow()
            
            feedPage = WebUtils.FetchURL(feedDeets['url'])
            
            if feedPage is None:
                #TODO: log an error here that the feed likely no longer exists!
                continue
            
            root = ET.fromstring(feedPage.Page)
            item = root.find('channel/item')
            
            if item is None:
                #TODO: log an error here that the feed likely no longer exists!
                continue

            title = DataStore.LRRChecker[feedName]['lastTitle'] = item.find('title').text
            link = DataStore.LRRChecker[feedName]['lastLink'] = WebUtils.ShortenGoogl(item.find('link').text)
            newestDate = dparser.parse(item.find('pubDate').text, fuzzy=True, ignoretz=True)
            
            if newestDate > feedDeets['lastUpdate']:
                DataStore.LRRChecker[feedName]['lastUpdate'] = newestDate
                
                if feedDeets['suppress']:
                    DataStore.LRRChecker[feedName]['suppress'] = False
                else:
                    response = 'New {0}! Title: {1} | {2}'.format(feedName, title, link)
                    responses.append(IRCResponse(ResponseType.Say, response, '#desertbus'))
            
        return responses

