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
        self.follows = {u'desertbus': datetime.datetime.utcnow(),
                        u'official_pax': datetime.datetime.utcnow(),
                        u'loadingreadyrun': datetime.datetime.utcnow(),
                        u'lrrmtg': datetime.datetime.utcnow(),
                        u'tyranicmoron': datetime.datetime.utcnow()}

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
        # do the command stuff described in the help
        if len(message.ParameterList) == 0:
            return IRCResponse(ResponseType.Say, self.help, message.ReplyTo)

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
            # TODO fetch latest tweet from specified user
            pass

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

        self._restartScanner()

        return removed, nonexistent

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
        self.scanner.start(((60 * 15) / 300) * len(self.follows) * 2 + 5, now=False)

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
                    break

            if len(newTweets) > 0:
                newTweets = newTweets[::-1]  # reverse the list so oldest tweets are first

                for tweet in newTweets:
                    # skip replies
                    if tweet['in_reply_to_screen_name'] is not None:
                        continue

                    tweetText = re.sub('[\r\n]+', StringUtils.graySplitter, tweet['text'])
                    for url in tweet['entities']['urls']:
                        tweetText = tweetText.replace(url['url'], url['expanded_url'])

                    formatString = unicode(assembleFormattedText(A.normal['New tweet from ', A.bold['@{0}:'], ' {1}']))
                    newTweet = formatString.format(tweet['user']['screen_name'], tweetText)
                    for channel, _ in self.bot.channels.iteritems():
                        self.bot.sendResponse(IRCResponse(ResponseType.Say,
                                                          newTweet,
                                                          channel))

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
