# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

import datetime
import xml.etree.ElementTree as ET
from six import iteritems

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

import pymoronbot.utils.LRRChecker as DataStore

import dateutil.parser as dparser


@implementer(IPlugin, IModule)
class LRR(BotCommand):
    def triggers(self):
        return ['lrr', 'llr']

    def actions(self):
        return super(LRR, self).actions() + [('message-channel', 1, self.checkLRR)]

    def help(self, query):
        if query[0] in self.triggers():
            return "lrr (<series>) - returns a link to the latest LRR video, " \
                "or the latest of a series if you specify one; " \
                "series are: {0}".format(", ".join(DataStore.LRRChecker.keys()))
        return "Automatic function, scans LRR video RSS feeds and reports new items in the channel."

    def checkLRR(self, _):
        """
        @type _: IRCMessage
        """
        responses = []
        for feedName, feedDeets in iteritems(DataStore.LRRChecker):
            if feedDeets['lastCheck'] > datetime.datetime.utcnow() - datetime.timedelta(minutes=10):
                continue
            
            DataStore.LRRChecker[feedName]['lastCheck'] = datetime.datetime.utcnow()
            
            feedPage = self.bot.moduleHandler.runActionUntilValue('fetch-url', feedDeets['url'])
            
            if feedPage is None:
                #TODO: log an error here that the feed likely no longer exists!
                continue
            
            root = ET.fromstring(feedPage.body)
            item = root.find('channel/item')
            
            if item is None:
                #TODO: log an error here that the feed likely no longer exists!
                continue

            newestDate = dparser.parse(item.find('pubDate').text, fuzzy=True, ignoretz=True)
            
            if newestDate > feedDeets['lastUpdate']:
                DataStore.LRRChecker[feedName]['lastUpdate'] = newestDate
                
                if feedDeets['suppress']:
                    DataStore.LRRChecker[feedName]['suppress'] = False
                else:
                    title = item.find('title').text
                    DataStore.LRRChecker[feedName]['lastTitle'] = title
                    link = self.bot.moduleHandler.runActionUntilValue('shorten-url', item.find('link').text)
                    DataStore.LRRChecker[feedName]['lastLink'] = link
                    response = 'New {0}! Title: {1} | {2}'.format(feedName, title, link)
                    responses.append(IRCResponse(ResponseType.Say, response, '#desertbus'))
            
        return responses

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.Parameters.strip()) > 0:
            feed = self.handleAliases(message.Parameters)
            lowerMap = {key.lower(): key for key in DataStore.LRRChecker}
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
            latestDate = datetime.datetime.utcnow() - datetime.timedelta(days=365 * 10)
            latestFeed = None
            latestTitle = None
            latestLink = None
            for feedName, feedDeets in iteritems(DataStore.LRRChecker):
                if feedDeets['lastUpdate'] > latestDate:
                    latestDate = feedDeets['lastUpdate']
                    latestFeed = feedName
                    latestTitle = feedDeets['lastTitle']
                    latestLink = feedDeets['lastLink']

            response = u'Latest {0}: {1} | {2}'.format(latestFeed, latestTitle, latestLink)
            return IRCResponse(ResponseType.Say, response, message.ReplyTo)

    @classmethod
    def handleAliases(cls, series):
        for feedName, feedDeets in iteritems(DataStore.LRRChecker):
            if series.lower() in feedDeets['aliases']:
                return feedName
        return series


lrr = LRR()
