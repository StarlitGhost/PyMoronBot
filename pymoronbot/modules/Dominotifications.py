# -*- coding: utf-8 -*-
import re
import json

from twisted.internet import task, threads

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.moduleinterface import ModuleInterface
from pymoronbot.utils import web


class Dominotifications(ModuleInterface):
    help = "Automatic module that tracks Domino's pizza tracker links, " \
           "informing you of the progress of your pizza until delivery"

    runInThread = True

    def onLoad(self):
        self.trackers = {}
        """@type : dict[str, TrackingDetails]"""

        self.regex = r'www\.dominos\.(co\.uk|ie)/pizzatracker/?\?id=(?P<orderID>[a-zA-Z0-9=]+)'

        commands = self.bot.moduleHandler.commands
        if 'URLFollow' in commands:
            commands['URLFollow'].handledExternally['Dominotifications'] = [self.regex]

    def onUnload(self):
        self._stopAllPizzaTrackers()
        commands = self.bot.moduleHandler.commands
        if 'URLFollow' in commands and 'Dominotifications' in commands['URLFollow'].handledExternally:
            del commands['URLFollow'].handledExternally['Dominotifications']

    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Type in self.acceptedTypes:
            return True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        match = re.search(self.regex, message.MessageString, re.IGNORECASE)

        if not match:
            return

        orderID = match.group('orderID')

        if orderID not in self.trackers:
            self.trackers[orderID] = TrackingDetails(message.User.Name, message.Channel,
                                                     task.LoopingCall(self._pizzaLoop, orderID))
            self._startPizzaTracker(orderID)
            return IRCResponse(ResponseType.Say,
                               u"PIZZA DETECTED! Now tracking {}'s Domino's pizza order!".format(message.User.Name),
                               message.ReplyTo)
        else:
            return IRCResponse(ResponseType.Say,
                               u"I'm already tracking that pizza for {}".format(self.trackers[orderID].orderer),
                               message.ReplyTo)

    def _startPizzaTracker(self, orderID):
        """
        @type orderID: str
        """
        self.trackers[orderID].tracker.start(30)

    def _pizzaLoop(self, orderID):
        return threads.deferToThread(self._pizzaTracker, orderID)

    def _pizzaTracker(self, orderID):
        """
        @type orderID: str
        """
        steps = {6: u"{}'s pizza order has been placed",
                 7: u"{}'s pizza is being prepared",
                 5: u"{}'s pizza is in the oven",
                 8: u"{}'s pizza is sitting on a shelf, waiting for a driver",
                 9: u"{}'s pizza is out for delivery",
                 3: u"{}'s pizza has been delivered! Tracking stopped"}

        trackingDetails = self.trackers[orderID]

        trackURL = u'https://www.dominos.co.uk/pizzaTracker/getOrderDetails?id={}'.format(orderID)
        page = web.fetchURL(trackURL)

        if page is None:
            # tracking API didn't respond
            self._stopPizzaTracker(orderID)
            self.bot.sendResponse(IRCResponse(ResponseType.Say,
                                  u"The pizza tracking page linked by {} "
                                  u"had some kind of error, tracking stopped".format(trackingDetails.orderer),
                                  trackingDetails.channel.Name))
            return

        j = json.loads(page.body)

        if j['customerName'] is None:
            self._stopPizzaTracker(orderID)
            self.bot.sendResponse(IRCResponse(ResponseType.Say,
                                  u"There are no pizza tracking details at the page linked by {}.".format(trackingDetails.orderer),
                                  trackingDetails.channel.Name))
            return
        
        response = None
        
        step = j['statusId']
        if step != trackingDetails.step:
            trackingDetails.step = step
            response = IRCResponse(ResponseType.Say,
                                   steps[step].format(trackingDetails.orderer),
                                   trackingDetails.channel.Name)

        if step == 3:
            self._stopPizzaTracker(orderID)
        
        if response is not None:
            self.bot.sendResponse(response)

    def _stopPizzaTracker(self, orderID):
        """
        @type orderID: str
        """
        if orderID in self.trackers:
            if self.trackers[orderID].tracker.running:
                self.trackers[orderID].tracker.stop()
            del self.trackers[orderID]
            return True
        return False

    def _stopAllPizzaTrackers(self):
        for orderID in self.trackers.keys():
            self._stopPizzaTracker(orderID)


class TrackingDetails(object):
    def __init__(self, orderer, channel, tracker):
        """
        @type orderer: str
        @type channel: IRCChannel
        @type tracker: task.LoopingCall
        """
        self.orderer = orderer
        self.channel = channel
        self.tracker = tracker
        self.step = 0
