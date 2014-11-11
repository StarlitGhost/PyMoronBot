# -*- coding: utf-8 -*-
import re
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from Utils import WebUtils

from bs4 import BeautifulSoup
from twisted.internet import task, threads


class DominosPizza(CommandInterface):
    help = "Automatic module that tracks Domino's pizza tracker links, " \
           "informing you of the progress of your pizza until delivery"

    runInThread = True

    def onLoad(self):
        self.trackers = {}
        """@type : dict[str, TrackingDetails]"""

        self.regex = r'www\.dominos\.co\.uk/checkout/pizzatracker\.aspx\?id=(?P<orderID>[a-zA-Z0-9]+)'

        commands = self.bot.moduleHandler.commands
        if 'URLFollow' in commands:
            commands['URLFollow'].handledExternally['DominosPizza'] = [self.regex]

    def onUnload(self):
        self._stopAllPizzaTrackers()
        commands = self.bot.moduleHandler.commands
        if 'URLFollow' in commands and 'DominosPizza' in commands['URLFollow'].handledExternally:
            del commands['URLFollow'].handledExternally['DominosPizza']

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
        match = re.search(self.regex, message.MessageString)

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
        steps = [u"{}'s pizza order has been placed",
                 u"{}'s pizza is being prepared",
                 u"{}'s pizza is in the oven",
                 u"{}'s pizza is sitting on a shelf, waiting for a driver",
                 u"{}'s pizza is out for delivery",
                 u"{}'s pizza has been delivered! Tracking stopped"]

        trackingDetails = self.trackers[orderID]

        trackURL = u'http://www.dominos.co.uk/checkout/pizzaTrackeriFrame.aspx?id={}'.format(orderID)
        page = WebUtils.fetchURL(trackURL)

        if page is not None:
            root = BeautifulSoup(page.body)
            stepImg = root.find('img')
            if stepImg is not None and stepImg.has_attr('alt'):
                stepImgAlt = stepImg['alt']
                stepMatch = re.search(r'^Step (?P<step>[0-9]+)$', stepImgAlt)

                if stepMatch:
                    step = int(stepMatch.group('step'))
                    if step > trackingDetails.step:
                        trackingDetails.step = step
                        self.bot.sendResponse(IRCResponse(ResponseType.Say,
                                                          steps[step-1].format(trackingDetails.orderer),
                                                          trackingDetails.channel.Name))

                    if step == 6:
                        self._stopPizzaTracker(orderID)

                    return

        # if we reach here the tracking page was invalid in some way
        self.bot.sendResponse(IRCResponse(ResponseType.Say,
                                          u"The pizza tracking page linked by {} "
                                          u"had some kind of error, tracking stopped".format(trackingDetails.orderer),
                                          trackingDetails.channel.Name))
        self._stopPizzaTracker(orderID)

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
