# -*- coding: utf-8 -*-

import HTMLParser
import json
import math
import re
import time

from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface

from Data.api_keys import load_key
from Data import ignores
from Utils import WebUtils, StringUtils

from bs4 import BeautifulSoup
from isodate import parse_duration
from twisted.words.protocols.irc import assembleFormattedText, attributes as A


class URLFollow(CommandInterface):
    triggers = ['urlfollow', 'follow']
    acceptedTypes = ['PRIVMSG', 'ACTION']
    help = 'automatic function that follows urls and grabs information about the resultant webpage'
    runInThread = True

    htmlParser = HTMLParser.HTMLParser()
    
    graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])

    def onLoad(self):
        self.handledExternally = {}
        """@type : dict[str, list[str]]"""
        # dict of regex patterns not to follow. populated by other modules so they can handle them themselves

        self.youtubeKey = load_key(u'YouTube')
        self.imgurClientID = load_key(u'imgur Client ID')
        self.twitchClientID = load_key(u'Twitch Client ID')
        
        self.autoFollow = True

    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Type not in self.acceptedTypes:
            return False
        if ignores.ignoreList is not None:
            if message.User.Name.lower() in ignores.ignoreList:
                return False
        return True
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        match = None
        if message.Command.lower() in self.triggers:
            if message.ParameterList[0].lower() == 'on':
                self.autoFollow = True
                return IRCResponse(ResponseType.Say, 'Auto-follow on', message.ReplyTo)
            elif message.ParameterList[0].lower() == 'off': 
                self.autoFollow = False
                return IRCResponse(ResponseType.Say, 'Auto-follow off', message.ReplyTo)
            else:
                match = re.search(r'(?P<url>(https?://|www\.)[^\s]+)', message.Parameters, re.IGNORECASE)
        elif self.autoFollow:
            match = re.search(r'(?P<url>(https?://|www\.)[^\s]+)', message.MessageString, re.IGNORECASE)
        if not match:
            return

        for module, patterns in self.handledExternally.iteritems():
            for pattern in patterns:
                if re.search(pattern, message.MessageString):
                    return  # url will be handled by another module

        return self.DispatchToFollows(match.group('url'), message)

    def DispatchToFollows(self, url, message):
        """
        @type url: unicode
        @type message: IRCMessage
        """
        youtubeMatch = re.search(r'(youtube\.com/watch.+v=|youtu\.be/)(?P<videoID>[^&#\?]{11})', url)
        imgurMatch   = re.search(r'(i\.)?imgur\.com/(?P<imgurID>[^\.]+)', url)
        twitterMatch = re.search(r'twitter\.com/(?P<tweeter>[^/]+)/status(es)?/(?P<tweetID>[0-9]+)', url)
        steamMatch   = re.search(r'store\.steampowered\.com/(?P<steamType>(app|sub))/(?P<steamID>[0-9]+)', url)
        ksMatch      = re.search(r'kickstarter\.com/projects/(?P<ksID>[^/]+/[^/&#\?]+)', url)
        twitchMatch  = re.search(r'twitch\.tv/(?P<twitchChannel>[^/]+)/?(\s|$)', url)
        
        if youtubeMatch:
            return self.FollowYouTube(youtubeMatch.group('videoID'), message)
        elif imgurMatch:
            return self.FollowImgur(imgurMatch.group('imgurID'), message)
        elif twitterMatch:
            return self.FollowTwitter(twitterMatch.group('tweeter'), twitterMatch.group('tweetID'), message)
        elif steamMatch:
            return self.FollowSteam(steamMatch.group('steamType'), steamMatch.group('steamID'), message)
        elif ksMatch:
            return self.FollowKickstarter(ksMatch.group('ksID'), message)
        elif twitchMatch:
            return self.FollowTwitch(twitchMatch.group('twitchChannel'), message)
        elif not re.search('\.(jpe?g|gif|png|bmp)$', url):
            return self.FollowStandard(url, message)
        
    def FollowYouTube(self, videoID, message):
        if self.youtubeKey is None:
            return IRCResponse(ResponseType.Say, '[YouTube API key not found]', message.ReplyTo)

        fields = 'items(id,snippet(title,description,channelTitle),contentDetails(duration))'
        parts = 'snippet,contentDetails'
        url = 'https://www.googleapis.com/youtube/v3/videos?id={}&fields={}&part={}&key={}'.format(videoID, fields, parts, self.youtubeKey)
        
        webPage = WebUtils.fetchURL(url)
        webPage.body = webPage.body.decode('utf-8')
        j = json.loads(webPage.body)

        if 'items' not in j:
            return None

        title = j['items'][0]['snippet']['title']
        description = j['items'][0]['snippet']['description']
        channel = j['items'][0]['snippet']['channelTitle']
        length = parse_duration(j["items"][0]["contentDetails"]["duration"]).total_seconds()

        m, s = divmod(int(length), 60)
        h, m = divmod(m, 60)
        if h > 0:
            length = u'{0:02d}:{1:02d}:{2:02d}'.format(h, m, s)
        else:
            length = u'{0:02d}:{1:02d}'.format(m, s)

        if not description:
            description = u'<no description available>'
        description = re.sub('(\n|\s)+', ' ', description)
        limit = 150
        if len(description) > limit:
            description = u'{} ...'.format(description[:limit].rsplit(' ', 1)[0])

        return IRCResponse(ResponseType.Say,
                           self.graySplitter.join([title, length, channel, description]),
                           message.ReplyTo,
                           {'urlfollowURL': 'http://youtu.be/{}'.format(videoID)})
    
    def FollowImgur(self, imgurID, message):
        if self.imgurClientID is None:
            return IRCResponse(ResponseType.Say, '[imgur Client ID not found]', message.ReplyTo)

        if imgurID.startswith('gallery/'):
            imgurID = imgurID.replace('gallery/', '')

        albumLink = False
        if imgurID.startswith('a/'):
            imgurID = imgurID.replace('a/', '')
            url = 'https://api.imgur.com/3/album/{0}'.format(imgurID)
            albumLink = True
        else:
            url = 'https://api.imgur.com/3/image/{0}'.format(imgurID)

        headers = [('Authorization', 'Client-ID {0}'.format(self.imgurClientID))]
        
        webPage = WebUtils.fetchURL(url, headers)
        
        if webPage is None:
            url = 'https://api.imgur.com/3/gallery/{0}'.format(imgurID)
            webPage = WebUtils.fetchURL(url, headers)

        if webPage is None:
            return
        
        response = json.loads(webPage.body)
        
        imageData = response['data']

        if imageData['title'] is None:
            url = 'https://api.imgur.com/3/gallery/{0}'.format(imgurID)
            webPage = WebUtils.fetchURL(url, headers)
            if webPage is not None:
                imageData = json.loads(webPage.body)['data']

            if imageData['title'] is None:
                webPage = WebUtils.fetchURL('http://imgur.com/{0}'.format(imgurID))
                imageData['title'] = self.GetTitle(webPage.body).replace(' - Imgur', '')
                if imageData['title'] == 'imgur: the simple image sharer':
                    imageData['title'] = None
        
        data = []
        if imageData['title'] is not None:
            data.append(imageData['title'])
        else:
            data.append(u'<No Title>')
        if imageData['nsfw']:
            data.append(u'\x034\x02NSFW!\x0F')
        if albumLink:
            data.append(u'Album: {0} Images'.format(imageData['images_count']))
        else:
            if 'is_album' in imageData and imageData['is_album']:
                data.append(u'Album: {0:,d} Images'.format(len(imageData['images'])))
            else:
                if imageData[u'animated']:
                    data.append(u'\x032\x02Animated!\x0F')
                data.append(u'{0:,d}x{1:,d}'.format(imageData['width'], imageData['height']))
                data.append(u'Size: {0:,d}kb'.format(int(imageData['size'])/1024))
        data.append(u'Views: {0:,d}'.format(imageData['views']))
        
        return IRCResponse(ResponseType.Say,
                           self.graySplitter.join(data),
                           message.ReplyTo,
                           {'urlfollowURL': '[nope, imgur is too hard. also, pointless?]'})

    def FollowTwitter(self, tweeter, tweetID, message):
        webPage = WebUtils.fetchURL('https://twitter.com/{0}/status/{1}'.format(tweeter, tweetID))

        soup = BeautifulSoup(webPage.body)

        tweet = soup.find(class_='permalink-tweet')
        
        user = tweet.find(class_='username').text

        tweetText = tweet.find(class_='tweet-text')
        
        tweetTimeText = tweet.find(class_='client-and-actions').text.strip()
        try:
            tweetTimeText = time.strftime('%Y/%m/%d %H:%M', time.strptime(tweetTimeText, '%I:%M %p - %d %b %Y'))
        except ValueError:
            pass

        links = tweetText.find_all('a', {'data-expanded-url': True})
        for link in links:
            link.string = ' ' + link['data-expanded-url']

        embeddedLinks = tweetText.find_all('a', {'data-pre-embedded': 'true'})
        for link in embeddedLinks:
            link.string = ' ' + link['href']

        text = StringUtils.unescapeXHTML(tweetText.text)
        text = re.sub('[\r\n]+', self.graySplitter, text)

        formatString = unicode(assembleFormattedText(A.normal[A.fg.gray['[{0}]'], A.bold[' {1}:'], ' {2}']))

        return IRCResponse(ResponseType.Say,
                           formatString.format(tweetTimeText, user, text),
                           message.ReplyTo,
                           {'urlfollowURL': 'https://twitter.com/{}/status/{}'.format(tweeter, tweetID)})

    def FollowSteam(self, steamType, steamId, message):
        steamType = {'app': 'app', 'sub': 'package'}[steamType]
        webPage = WebUtils.fetchURL('http://store.steampowered.com/api/{0}details/?{0}ids={1}&cc=US&l=english&v=1'.format(steamType, steamId))

        response = json.loads(webPage.body)
        if not response[steamId]['success']:
            return  # failure

        appData = response[steamId]['data']

        data = []

        # name
        if 'developers' in appData:
            name = assembleFormattedText(A.normal[appData['name'], A.fg.gray[' by '], u', '.join(appData['developers'])])
        else:
            name = appData['name']
        data.append(name)
        
        # package contents (might need to trim this...)
        if 'apps' in appData:
            appNames = [app['name'] for app in appData['apps']]
            apps = u'Package containing: {}'.format(u', '.join(appNames))
            data.append(apps)

        # genres
        if 'genres' in appData:
            data.append(u'Genres: ' + ', '.join([genre['description'] for genre in appData['genres']]))

        # release date
        releaseDate = appData['release_date']
        if not releaseDate['coming_soon']:
            if releaseDate['date']:
                data.append(u'Release Date: ' + releaseDate['date'])
        else:
            data.append(assembleFormattedText(A.normal['Release Date: ', A.fg.cyan[str(releaseDate['date'])]]))

        # metacritic
        # http://www.metacritic.com/faq#item32 (Why is the breakdown of green, yellow, and red scores different for games?)
        if 'metacritic' in appData:
            metaScore = appData['metacritic']['score']
            if metaScore < 50:
                metacritic = assembleFormattedText(A.normal[A.fg.red[str(metaScore)]])
            elif metaScore < 75:
                metacritic = assembleFormattedText(A.normal[A.fg.yellow[str(metaScore)]])
            else:
                metacritic = assembleFormattedText(A.normal[A.fg.green[str(metaScore)]])
            data.append(u'Metacritic: {0}'.format(metacritic))

        # prices
        priceField = {'app': 'price_overview', 'package': 'price'}[steamType]
        if priceField in appData:
            prices = {'USD': appData[priceField],
                      'GBP': self.getSteamPrice(steamType, steamId, 'GB'),
                      'EUR': self.getSteamPrice(steamType, steamId, 'FR'),
                      'AUD': self.getSteamPrice(steamType, steamId, 'AU')}

            currencies = {'USD': u'$',
                          'GBP': u'\u00A3',
                          'EUR': u'\u20AC',
                          'AUD': u'AU$'}

            if not prices['AUD'] or prices['AUD']['final'] == prices['USD']['final']:
                del prices['AUD']
            
            # filter out any missing prices
            prices = {key: val for key, val in prices.iteritems() if val}

            priceString = u'/'.join([currencies[val['currency']] + unicode(val['final'] / 100.0) for val in prices.values()])
            if prices['USD']['discount_percent'] > 0:
                priceString += assembleFormattedText(A.normal[A.fg.green[' ({0}% sale!)'.format(prices['USD']['discount_percent'])]])

            data.append(priceString)
        
        # description
        if 'about_the_game' in appData and appData['about_the_game'] is not None:
            limit = 150
            description = re.sub(r'(<[^>]+>|[\r\n\t])+', assembleFormattedText(A.normal[' ', A.fg.gray['>'], ' ']), appData['about_the_game'])
            if len(description) > limit:
                description = u'{0} ...'.format(description[:limit].rsplit(' ', 1)[0])
            data.append(description)

        return IRCResponse(ResponseType.Say,
                           self.graySplitter.join(data),
                           message.ReplyTo,
                           {'urlfollowURL': 'http://store.steampowered.com/{}/{}'.format({'app': 'app', 'package': 'sub'}[steamType], steamId)})

    @classmethod
    def getSteamPrice(cls, appType, appId, region):
        webPage = WebUtils.fetchURL('http://store.steampowered.com/api/{0}details/?{0}ids={1}&cc={2}&l=english&v=1'.format(appType, appId, region))
        priceField = {'app': 'price_overview', 'package': 'price'}[appType]
        response = json.loads(webPage.body)
        
        if 'data' not in response[appId]:
            return
        
        if region == 'AU':
            response[appId]['data'][priceField]['currency'] = 'AUD'
        return response[appId]['data'][priceField]

    def FollowKickstarter(self, ksID, message):
        webPage = WebUtils.fetchURL('https://www.kickstarter.com/projects/{}/description'.format(ksID))

        soup = BeautifulSoup(webPage.body)

        data = []

        shorturl = soup.find(rel='shorturl')['href']
        if shorturl is None:
            shorturl = 'https://www.kickstarter.com/projects/{}/'.format(ksID)

        title = soup.find(property='og:title')
        if title is not None:
            # live projects
            creator = soup.find(attrs={'data-modal-class': 'modal_project_by'})
            # completed projects
            if creator is None:
                creator = soup.find(class_='green-dark', attrs={'data-modal-class': 'modal_project_by'})
            if creator is not None:
                data.append(unicode(assembleFormattedText(A.normal['{0}',
                                                                   A.fg.gray[' by '],
                                                                   '{1}'])).format(title['content'].strip(),
                                                                                   creator.text.strip()))
            else:
                data.append(title['content'].strip())

        stats = soup.find(id='stats')
        # projects in progress
        if stats is not None:
            backerCount = stats.find(id='backers_count')
            if backerCount is not None:
                backerCount = int(backerCount['data-backers-count'])
        # completed projects
        else:
            backerCount = soup.find(class_='NS_campaigns__spotlight_stats')
            if backerCount is not None:
                backerCount = int(backerCount.b.text.strip().split()[0].replace(',', ''))

        data.append('Backers: {0:,}'.format(backerCount))

        if stats is not None:
            pledgeData = stats.find(id='pledged')
            if pledgeData is not None:
                pledged = float(pledgeData['data-pledged'])
                goal = float(pledgeData['data-goal'])
                percentage = float(pledgeData['data-percent-raised'])
                if backerCount > 0:
                    pledgePerBacker = pledged / backerCount
                else:
                    pledgePerBacker = 0
        else:
            money = soup.select('span.money')
            if money:
                pledgedString = money[1].text.strip()
                goalString = money[2].text.strip()
                pledged = float(re.sub(ur'[^0-9.]', u'', pledgedString))
                goal = float(re.sub(ur'[^0-9.]', u'', goalString))
                percentage = (pledged / goal)
                if backerCount > 0:
                    pledgePerBacker = pledged / backerCount
                else:
                    pledgePerBacker = 0

        # no longer any way to get this?
        #currency = soup.select('span.money.no-code')[-1]['class']
        #currency.remove('money')
        #currency.remove('no-code')
        #currency = currency[0].upper()

        if percentage >= 1.0:
            percentageString = A.fg.green['({3:,.0f}% funded)']
        else:
            percentageString = A.fg.red['({3:,.0f}% funded)']

        pledgePerBackerString = A.fg.gray['{4:,.0f}/backer']

        pledgedString = assembleFormattedText(A.normal['Pledged: {0:,.0f}', A.fg.gray['/'], '{1:,.0f} ', percentageString, ' ', pledgePerBackerString])
        data.append(pledgedString.format(pledged,
                                         goal,
                                         percentage * 100,
                                         pledgePerBacker))

        findState = soup.find(id='main_content')
        if 'Campaign-state-canceled' in findState['class']:
            data.append(assembleFormattedText(A.normal[A.fg.red['Cancelled']]))
        
        elif 'Campaign-state-suspended' in findState['class']:
            data.append(assembleFormattedText(A.normal[A.fg.blue['Suspended']]))
            
        elif 'Campaign-state-failed' in findState['class']:
            data.append(assembleFormattedText(A.normal[A.fg.red['Failed']]))

        elif 'Campaign-state-successful' in findState['class']:
                data.append(assembleFormattedText(A.normal[A.fg.green['Successful']]))

        elif 'Campaign-state-live' in findState['class']:
            duration = stats.find(id='project_duration_data')

            if duration is not None:
                remaining = float(duration['data-hours-remaining'])
                days = math.floor(remaining/24)
                hours = remaining % 24

                data.append('Duration: {0:.0f} days {1:.1f} hours to go'.format(days, hours))

        return IRCResponse(ResponseType.Say,
                           self.graySplitter.join(data),
                           message.ReplyTo,
                           {'urlfollowURL': shorturl})

    def FollowTwitch(self, channel, message):
        # Heavily based on Didero's DideRobot code for the same
        # https://github.com/Didero/DideRobot/blob/06629fc3c8bddf8f729ce2d27742ff999dfdd1f6/commands/urlTitleFinder.py#L37
        # TODO: other stats?
        if self.twitchClientID is None:
            return IRCResponse(ResponseType.Say, '[Twitch Client ID not found]', message.ReplyTo)
        
        chanData = {}
        channelOnline = False
        twitchHeaders = [('Accept', 'application/vnd.twitchtv.v2+json'),
                         ('Client-ID', self.twitchClientID)]
        webPage = WebUtils.fetchURL(u'https://api.twitch.tv/kraken/streams/{}'.format(channel), twitchHeaders)

        streamData = json.loads(webPage.body)

        if 'stream' in streamData and streamData['stream'] is not None:
            chanData = streamData['stream']['channel']
            channelOnline = True
        elif 'error' not in streamData:
            webPage = WebUtils.fetchURL(u'https://api.twitch.tv/kraken/channels/{}'.format(channel), twitchHeaders)
            chanData = json.loads(webPage.body)

        if len(chanData) > 0:
            if channelOnline:
                channelInfo = assembleFormattedText(A.fg.green['']) + u'{}'.format(chanData['display_name']) + assembleFormattedText(A.normal[''])
            else:
                channelInfo = assembleFormattedText(A.fg.red['']) + u'{}'.format(chanData['display_name']) + assembleFormattedText(A.normal[''])
            channelInfo += u' "{}"'.format(re.sub(r'[\r\n]+', self.graySplitter, chanData['status'].strip()))
            if chanData['game'] is not None:
                channelInfo += assembleFormattedText(A.normal[A.fg.gray[', playing '], u'{}'.format(chanData['game'])])
            if chanData['mature']:
                channelInfo += assembleFormattedText(A.normal[A.fg.lightRed[' [Mature]']])
            if channelOnline:
                channelInfo += assembleFormattedText(A.normal[A.fg.green[' (Live with {0:,d} viewers)'.format(streamData['stream']['viewers'])]])
            else:
                channelInfo += assembleFormattedText(A.normal[A.fg.red[' (Offline)']])

            return IRCResponse(ResponseType.Say,
                               channelInfo,
                               message.ReplyTo,
                               {'urlfollowURL': 'https://twitch.tv/{}'.format(channel)})
    
    def FollowStandard(self, url, message):
        webPage = WebUtils.fetchURL(url)
        
        if webPage is None:
            return

        if webPage.responseUrl != url:
            return self.DispatchToFollows(webPage.responseUrl, message)
        
        title = self.GetTitle(webPage.body)
        if title is not None:
            return IRCResponse(ResponseType.Say,
                               u'{0} (at {1})'.format(title, webPage.domain),
                               message.ReplyTo,
                               {'urlfollowURL': url})
        
        return

    def GetTitle(self, webpage):
        soup = BeautifulSoup(webpage)
        title = soup.title
        if title:
            title = title.text
            title = re.sub(u'[\r\n]+', u'', title)  # strip any newlines
            title = title.strip()   # strip all whitespace either side
            title = re.sub(u'\s+', u' ', title)     # replace multiple whitespace chars with a single space
            title = self.htmlParser.unescape(title)     # unescape html entities

            # Split on the first space before 300 characters, and replace the rest with '...'
            if len(title) > 300:
                title = title[:300].rsplit(u' ', 1)[0] + u" ..."

            return title
        
        return None
