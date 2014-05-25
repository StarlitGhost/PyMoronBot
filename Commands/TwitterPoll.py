# -*- coding: utf-8 -*-
"""
Created on May 18, 2014

@author: Tyranic-Moron
"""
import base64
import json
import re
from urllib2 import Request, urlopen
import datetime
from twisted.internet import task, threads
from twisted.words.protocols.irc import assembleFormattedText, attributes as A
from twitter import Twitter, OAuth2, TwitterHTTPError

from CommandInterface import CommandInterface
from Data import api_keys
from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Utils import StringUtils


class TwitterPoll(CommandInterface):
    triggers = ['twitter']
    help = 'twitter <user>, twitter follow <user>, twitter unfollow <user>\n' \
           '<user> - returns the latest tweet from the specified twitter user\n' \
           'follow <user> - adds the specified twitter user to a list to be polled every few minutes for new tweets\n' \
           'unfollow <user> - removes the specified twitter user from the polling list'
    runInThread = True

    def onLoad(self):
        if 'TwitterPoll' not in self.bot.dataStore:
            self.bot.dataStore['TwitterPoll'] = {}

        self.follows = self.bot.dataStore['TwitterPoll']

        bearer_token = self._get_access_token()
        self.twitter = Twitter(auth=OAuth2(bearer_token=bearer_token))

        # start the thread that checks for new tweets
        self.scanner = task.LoopingCall(self._scanLoop)

        self._restartScanner()

    def onUnload(self):
        if self.scanner.running:
            self.scanner.stop()

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if len(message.ParameterList) == 0:  # no params, return list of follows
            if len(self.follows) == 0:
                return IRCResponse(ResponseType.Say,
                                   "I'm not following anyone right now, "
                                   "use {}twitter follow <user> to add some people".format(self.bot.commandChar),
                                   message.ReplyTo)
            else:
                return IRCResponse(ResponseType.Say,
                                   'Currently following {}'.format(', '.join(self.follows)),
                                   message.ReplyTo)

        subCommand = message.ParameterList[0].lower()

        if subCommand == 'follow':
            new, existing, invalid = self._follow(message.ParameterList[1:])
            responses = []
            if len(new) > 0:
                responses.append(IRCResponse(ResponseType.Say,
                                             'Now following: {0}'.format(', '.join(new)),
                                             message.ReplyTo))
            if len(existing) > 0:
                responses.append(IRCResponse(ResponseType.Say,
                                             'I am already following: {0}'.format(', '.join(existing)),
                                             message.ReplyTo))
            if len(invalid) > 0:
                responses.append(IRCResponse(ResponseType.Say,
                                             "These aren't valid twitter accounts: {0}".format(', '.join(invalid)),
                                             message.ReplyTo))
            return responses
        elif subCommand == 'unfollow':
            removed, nonexistent = self._unfollow(message.ParameterList[1:])
            responses = []
            if len(removed) > 0:
                responses.append(IRCResponse(ResponseType.Say,
                                             'Unfollowed: {0}'.format(', '.join(removed)),
                                             message.ReplyTo))
            if len(nonexistent) > 0:
                responses.append(IRCResponse(ResponseType.Say,
                                             "I'm already not following: {0}".format(', '.join(nonexistent)),
                                             message.ReplyTo))
            return responses
        else:
            # fetch latest tweet from specified user
            user = message.ParameterList[0]
            if self._checkUserExists(user):
                return IRCResponse(ResponseType.Say,
                                   "'{}' is not a valid twitter user".format(user),
                                   message.ReplyTo)

            tweet = self._latestTweet(user)
            if tweet['text'] is None:
                return IRCResponse(ResponseType.Say,
                                   "'{}' is a valid twitter user, but has not made any tweets".format(user),
                                   message.ReplyTo)

            tweetText = StringUtils.unescapeXHTML(tweet['text'])
            tweetText = re.sub('[\r\n]+', StringUtils.graySplitter, tweetText)
            for url in tweet['entities']['urls']:
                tweetText = tweetText.replace(url['url'], url['expanded_url'])

            formatString = unicode(assembleFormattedText(A.normal[A.bold['@{0}>'], ' {1}']))
            newTweet = formatString.format(tweet['user']['screen_name'], tweetText)
            return IRCResponse(ResponseType.Say, newTweet, message.ReplyTo)

    def _follow(self, users):
        """
        @type users: list[unicode]
        """
        new = []
        existing = []
        invalid = []
        for user in users:
            if user.lower() in self.follows:
                existing.append(user.lower())
            else:
                if self._checkUserExists(user):
                    new.append(user)
                    self.follows[user] = datetime.datetime.utcnow()
                else:
                    invalid.append(user)

        if len(existing) > 0:
            self._syncFollows()

        self._restartScanner()

        return new, existing, invalid

    def _unfollow(self, users):
        """
        @type users: list[unicode]
        """
        removed = []
        nonexistent = []
        for user in users:
            if user.lower() in self.follows:
                removed.append(user.lower())
                del self.follows[user.lower()]
            else:
                nonexistent.append(user)

        if len(removed) > 0:
            self._syncFollows()

        self._restartScanner()

        return removed, nonexistent

    def _syncFollows(self):
        self.bot.dataStore['TwitterPoll'] = self.follows

    def _checkUserExists(self, user):
        try:
            self.twitter.users.show(screen_name=user)
            return True
        except TwitterHTTPError:
            return False

    def _restartScanner(self):
        if self.scanner.running:
            self.scanner.stop()
        # * 2 here so we have some breathing room for multiple servers
        globalLimit = ((60 * 15) / 300) * len(self.follows) * 2 + 5
        perTimelineLimit = ((60 * 15) / 180) * 2 + 5
        self.scanner.start(max(perTimelineLimit, globalLimit), now=False)

    def _scanLoop(self):
        return threads.deferToThread(self._scanTwitter)

    def _scanTwitter(self):
        for user, lastTweetTimestamp in self.follows.iteritems():
            timeline = self.twitter.statuses.user_timeline(screen_name=user)

            newTweets = []
            for tweet in timeline:
                tweetTimestamp = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                if tweetTimestamp > lastTweetTimestamp:
                    newTweets.append(tweet)
                else:
                    if len(newTweets) > 0:
                        self.follows[user] = datetime.datetime.strptime(newTweets[0]['created_at'],
                                                                        '%a %b %d %H:%M:%S +0000 %Y')
                    else:
                        self.follows[user] = tweetTimestamp
                    self._syncFollows()
                    break

            if len(newTweets) > 0:
                newTweets = newTweets[::-1]  # reverse the list so oldest tweets are first

                for tweet in newTweets:
                    # skip replies
                    if tweet['in_reply_to_screen_name'] is not None:
                        continue

                    tweetText = StringUtils.unescapeXHTML(tweet['text'])
                    tweetText = re.sub('[\r\n]+', StringUtils.graySplitter, tweetText)
                    for url in tweet['entities']['urls']:
                        tweetText = tweetText.replace(url['url'], url['expanded_url'])

                    formatString = unicode(assembleFormattedText(A.normal['Tweet! ', A.bold['@{0}>'], ' {1}']))
                    newTweet = formatString.format(tweet['user']['screen_name'], tweetText)
                    for channel, _ in self.bot.channels.iteritems():
                        self.bot.sendResponse(IRCResponse(ResponseType.Say,
                                                          newTweet,
                                                          channel))

    def _latestTweet(self, user):
        timeline = self.twitter.statuses.user_timeline(screen_name=user)
        if len(timeline) > 0:
            return timeline[0]

    def _get_access_token(self):
        """Obtain a bearer token."""
        consumer_key = api_keys.load_key("Twitter Key")
        consumer_secret = api_keys.load_key("Twitter Secret")

        if consumer_key is None or consumer_secret is None:
            raise TwitterAPIKeysMissing('Twitter API Keys are missing, cannot use Twitter API')

        bearer_token = '%s:%s' % (consumer_key, consumer_secret)
        encoded_bearer_token = base64.b64encode(bearer_token.encode('ascii'))
        request = Request('https://api.twitter.com/oauth2/token')
        request.add_header('Content-Type',
                           'application/x-www-form-urlencoded;charset=UTF-8')
        request.add_header('Authorization',
                           'Basic %s' % encoded_bearer_token.decode('utf-8'))
        request.add_data('grant_type=client_credentials'.encode('ascii'))

        response = urlopen(request)
        raw_data = response.read().decode('utf-8')
        data = json.loads(raw_data)
        return data['access_token']


class TwitterAPIKeysMissing(Exception):
    pass
