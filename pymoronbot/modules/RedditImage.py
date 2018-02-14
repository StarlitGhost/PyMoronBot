# -*- coding: utf-8 -*-
"""
Created on Mar 03, 2015

@author: Tyranic-Moron
"""
import json
import random

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType
from pymoronbot.moduleinterface import ModuleInterface

from pymoronbot.utils.api_keys import load_key
from pymoronbot.utils import web

from twisted.words.protocols.irc import assembleFormattedText, attributes as A


# Idea for this initially taken from Heufneutje's RE_HeufyBot Aww module, but I made it more generic for aliasing
# https://github.com/Heufneutje/RE_HeufyBot/blob/f45219d1a61f0ed0fd60a89dcaeb2e962962356e/modules/Aww/src/heufybot/modules/Aww.java
# Future plans:
# - multiple fetch types beyond the current random, eg reddit sort types (top rated, hot, best, etc)
class RedditImage(ModuleInterface):
    triggers = ['redditimage']
    help = "redditimage <subreddit> [<range>] - fetches a random image from the top 100 (or given range) of the specified subreddit"
    runInThread = True

    def onLoad(self):
        self.imgurClientID = load_key(u'imgur Client ID')
        self.headers = [('Authorization', 'Client-ID {}'.format(self.imgurClientID))]

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0 or len(message.ParameterList) > 2:
            return IRCResponse(ResponseType.Say, self.help, message.ReplyTo)

        if not self.imgurClientID:
            return IRCResponse(ResponseType.Say,
                               u'[imgur client ID not found]',
                               message.ReplyTo)

        subreddit = message.ParameterList[0].lower()
        if len(message.ParameterList) == 2:
            try:
                if len(message.ParameterList[1]) < 20:
                    topRange = int(message.ParameterList[1])
                else:
                    raise ValueError
                if topRange < 0:
                    raise ValueError
            except ValueError:
                return IRCResponse(ResponseType.Say, "The range should be a positive integer!", message.ReplyTo)
        else:
            topRange = 100

        url = "https://api.imgur.com/3/gallery/r/{}/time/all/{}"
        url = url.format(subreddit, random.randint(0, topRange))
        response = web.fetchURL(url, self.headers)
        jsonResponse = json.loads(response.body)
        images = jsonResponse['data']

        if not images:
            return IRCResponse(ResponseType.Say,
                               "The subreddit '{}' doesn't seem to have any images posted to it (or it doesn't exist!)"
                               .format(subreddit),
                               message.ReplyTo)

        image = random.choice(images)

        data = []
        if 'title' in image and image['title'] is not None:
            data.append(image['title'])
        if 'nsfw' in image and image['nsfw']:
            data.append(u'\x034\x02NSFW!\x0F')
        if 'animated' in image and image['animated']:
            data.append(u'\x032\x02Animated!\x0F')
        if 'gifv' in image:
            data.append(image['gifv'])
        else:
            data.append(image['link'])

        graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])
        return IRCResponse(ResponseType.Say, graySplitter.join(data), message.ReplyTo)
