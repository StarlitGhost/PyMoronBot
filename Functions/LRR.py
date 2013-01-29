from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import FunctionData
import WebUtils

import re, datetime

class Instantiate(Function):
    Help = "lrr (<series>) - returns a link to the latest LRR video, or the latest of a series if you specify one"
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('lrr|llr', message.Command, re.IGNORECASE)
        if not match:
            return
        
        if len(message.Parameters.strip()) > 0:
            feed = self.handleAliases(message.Parameters)
            lowerMap = dict(zip(map(lambda x:x.lower(),FunctionData.LRRChecker.iterkeys()),FunctionData.LRRChecker.iterkeys()))
            if feed.lower() in lowerMap:
                feedName = lowerMap[feed.lower()]
                feedLatest = FunctionData.LRRChecker[feedName]['lastTitle']
                feedLink = FunctionData.LRRChecker[feedName]['lastLink']
                
                response = 'Latest {0}: {1} | Link: {2}'.format(feedName, feedLatest, feedLink)
                
                return IRCResponse(ResponseType.Say, response, message.ReplyTo)
                
            return IRCResponse(ResponseType.Say, '{0} is not one of the LRR series being monitored', message.ReplyTo)
        else:
            latestDate = datetime.datetime.utcnow() - datetime.timedelta(days=365*10)
            latestFeed = None
            latestTitle = None
            latestLink = None
            for feedName, feedDeets in FunctionData.LRRChecker.iteritems():
                if feedDeets['lastUpdate'] > latestDate:
                    latestDate = feedDeets['lastUpdate']
                    latestFeed = feedName
                    latestTitle = feedDeets['lastTitle']
                    latestLink = feedDeets['lastLink']
                    
            response = 'Latest {0}: {1} | Link: {2}'.format(latestFeed, latestTitle, latestLink)
            return IRCResponse(ResponseType.Say, response, message.ReplyTo)

    def handleAliases(self, series):
        for feedName, feedDeets in FunctionData.LRRChecker.iteritems():
            if series.lower() in feedDeets['aliases']:
                return feedName
        return series

