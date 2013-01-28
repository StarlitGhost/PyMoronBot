from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import WebUtils

import re, datetime
import xml.etree.ElementTree as ET
import dateutil.parser as dparser

class Instantiate(Function):
    Help = "Automatic function, scans LRR video RSS feeds and reports new items in the channel."
    
    #! move to a common function data store if at all possible
    feeds = {
        'Unskippable': {
            'url': 'http://www.escapistmagazine.com/rss/videos/list/82.xml',
            'lastUpdate': datetime.datetime.utcnow(),
            'lastTitle': '',
            'lastLink': '',
            'lastCheck': datetime.datetime.utcnow() - datetime.timedelta(minutes=10) },
        'LRR': {
            'url': 'http://www.escapistmagazine.com/rss/videos/list/123.xml',
            'lastUpdate': datetime.datetime.utcnow(),
            'lastTitle': '',
            'lastLink': '',
            'lastCheck': datetime.datetime.utcnow() - datetime.timedelta(minutes=10) },
        'Feed Dump': {
            'url': 'http://www.escapistmagazine.com/rss/videos/list/171.xml',
            'lastUpdate': datetime.datetime.utcnow(),
            'lastTitle': '',
            'lastLink': '',
            'lastCheck': datetime.datetime.utcnow() - datetime.timedelta(minutes=10) },
        'CheckPoint': {
            'url': 'http://penny-arcade.com/feed/show/checkpoint',
            'lastUpdate': datetime.datetime.utcnow(),
            'lastTitle': '',
            'lastLink': '',
            'lastCheck': datetime.datetime.utcnow() - datetime.timedelta(minutes=10) },
        'LRRCast': {
            'url': 'http://feeds.feedburner.com/lrrcast',
            'lastUpdate': datetime.datetime.utcnow(),
            'lastTitle': '',
            'lastLink': '',
            'lastCheck': datetime.datetime.utcnow() - datetime.timedelta(minutes=10) }
        }
    
    def GetResponse(self, message):
        responses = []
        for feedName, feedDeets in self.feeds.iteritems():
            if feedDeets['lastCheck'] > datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                continue
            
            self.feeds[feedName]['lastCheck'] = datetime.datetime.utcnow()
            
            feedPage = WebUtils.FetchURL(feedDeets['url'])
            root = ET.fromstring(feedPage.Page)
            item = root.find('channel/item')
            title = self.feeds[feedName]['lastTitle'] = item.find('title').text
            link = self.feeds[feedName]['lastLink'] = WebUtils.ShortenGoogl(item.find('link').text)
            newestDate = dparser.parse(item.find('pubDate').text, fuzzy=True, ignoretz=True)
            if newestDate > feedDeets['lastUpdate']:
                self.feeds[feedName]['lastUpdate'] = newestDate
                
                response = 'New {0}! Title: {1} | Link: {2}'.format(feedName, title, link)
                responses.append(IRCResponse(ResponseType.Say, response, '#desertbus'))
            
        return responses

