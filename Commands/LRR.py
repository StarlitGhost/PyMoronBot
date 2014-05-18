# -*- coding: utf-8 -*-
import datetime

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType

import Data.LRRChecker as DataStore


class LRR(CommandInterface):

    triggers = ['lrr', 'llr']

    @staticmethod
    def help(_):
        return "lrr (<series>) - returns a link to the latest LRR video, " \
               "or the latest of a series if you specify one; " \
               "series are: {0}".format(", ".join(DataStore.LRRChecker.keys()))
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.Parameters.strip()) > 0:
            feed = self.handleAliases(message.Parameters)
            lowerMap = {key.lower(): key for key in DataStore.LRRChecker.iterkeys()}
            if feed.lower() in lowerMap:
                feedName = lowerMap[feed.lower()]
                feedLatest = DataStore.LRRChecker[feedName]['lastTitle']
                feedLink = DataStore.LRRChecker[feedName]['lastLink']
                
                response = u'Latest {0}: {1} | {2}'.format(feedName, feedLatest, feedLink)
                
                return IRCResponse(ResponseType.Say, response, message.ReplyTo)
                
            return IRCResponse(ResponseType.Say,
                               u"{0} is not one of the LRR series being monitored "
                               u"(leave a tell for Tyranic-Moron if it's a new series or "
                               u"should be an alias!)".format(message.Parameters.strip()),
                               message.ReplyTo)
        else:
            latestDate = datetime.datetime.utcnow() - datetime.timedelta(days=365*10)
            latestFeed = None
            latestTitle = None
            latestLink = None
            for feedName, feedDeets in DataStore.LRRChecker.iteritems():
                if feedDeets['lastUpdate'] > latestDate:
                    latestDate = feedDeets['lastUpdate']
                    latestFeed = feedName
                    latestTitle = feedDeets['lastTitle']
                    latestLink = feedDeets['lastLink']
                    
            response = u'Latest {0}: {1} | {2}'.format(latestFeed, latestTitle, latestLink)
            return IRCResponse(ResponseType.Say, response, message.ReplyTo)

    @classmethod
    def handleAliases(cls, series):
        for feedName, feedDeets in DataStore.LRRChecker.iteritems():
            if series.lower() in feedDeets['aliases']:
                return feedName
        return series
