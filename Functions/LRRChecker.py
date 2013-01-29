from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import FunctionData
import WebUtils

import re, datetime
import xml.etree.ElementTree as ET
import dateutil.parser as dparser

class Instantiate(Function):
    Help = "Automatic function, scans LRR video RSS feeds and reports new items in the channel."
    
    def GetResponse(self, message):
        responses = []
        for feedName, feedDeets in FunctionData.LRRChecker.iteritems():
            if feedDeets['lastCheck'] > datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                continue
            
            FunctionData.LRRChecker[feedName]['lastCheck'] = datetime.datetime.utcnow()
            
            feedPage = WebUtils.FetchURL(feedDeets['url'])
            root = ET.fromstring(feedPage.Page)
            item = root.find('channel/item')
            
            title = FunctionData.LRRChecker[feedName]['lastTitle'] = item.find('title').text
            link = FunctionData.LRRChecker[feedName]['lastLink'] = WebUtils.ShortenGoogl(item.find('link').text)
            newestDate = dparser.parse(item.find('pubDate').text, fuzzy=True, ignoretz=True)
            
            if newestDate > feedDeets['lastUpdate']:
                FunctionData.LRRChecker[feedName]['lastUpdate'] = newestDate
                
                if feedDeets['suppress']:
                    FunctionData.LRRChecker[feedName]['suppress'] = False
                else:
                    response = 'New {0}! Title: {1} | Link: {2}'.format(feedName, title, link)
                    responses.append(IRCResponse(ResponseType.Say, response, '#desertbus'))
            
        return responses

