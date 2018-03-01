# -*- coding: utf-8 -*-
from twisted.plugin import IPlugin
from pymoronbot.moduleinterface import IModule
from pymoronbot.modules.commandinterface import BotCommand
from zope.interface import implementer

from html.parser import HTMLParser
import json
import math
import re
import time
import datetime

from builtins import str
from six import iteritems

from pymoronbot.message import IRCMessage
from pymoronbot.response import IRCResponse, ResponseType

from pymoronbot.utils.api_keys import load_key
from pymoronbot.utils import string, web

from bs4 import BeautifulSoup
from isodate import parse_duration
import dateutil.parser
import dateutil.tz
from twisted.words.protocols.irc import assembleFormattedText, attributes as A


@implementer(IPlugin, IModule)
class URLFollow(BotCommand):
    def actions(self):
        return super(URLFollow, self).actions() + [('action-channel', 1, self.handleURL),
                                                   ('action-user', 1, self.handleURL),
                                                   ('message-channel', 1, self.handleURL),
                                                   ('message-user', 1, self.handleURL),
                                                   ('urlfollow', 1, self.dispatchToFollows)]

    def triggers(self):
        return ['urlfollow', 'follow']

    def help(self, query):
        return 'Automatic module that follows urls and grabs information about the resultant webpage'

    runInThread = True

    htmlParser = HTMLParser()
    
    graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])

    def onLoad(self):
        self.youtubeKey = load_key(u'YouTube')
        self.imgurClientID = load_key(u'imgur Client ID')
        self.twitchClientID = load_key(u'Twitch Client ID')
        
        self.autoFollow = True
    
    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.ParameterList[0].lower() == 'on':
            self.autoFollow = True
            return IRCResponse(ResponseType.Say, 'Auto-follow on', message.ReplyTo)
        if message.ParameterList[0].lower() == 'off':
            self.autoFollow = False
            return IRCResponse(ResponseType.Say, 'Auto-follow off', message.ReplyTo)

        return self.handleURL(message, auto=False)

    def handleURL(self, message, auto=True):
        if auto and not self.autoFollow:
            return
        if auto and self.checkIgnoreList(message):
            return

        match = re.search(r'(?P<url>(https?://|www\.)[^\s]+)', message.MessageString, re.IGNORECASE)
        if not match:
            return

        follows = self.bot.moduleHandler.runActionUntilValue('urlfollow', match.group('url'))
        if not follows:
            return
        if not isinstance(follows, list):
            follows = [follows]

        responses = []
        for follow in follows:
            responses.append(IRCResponse(ResponseType.Say, follow, message.ReplyTo))

        return responses

    def dispatchToFollows(self, url):
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
            return self.FollowYouTube(youtubeMatch.group('videoID'))
        elif imgurMatch:
            return self.FollowImgur(imgurMatch.group('imgurID'))
        elif twitterMatch:
            return self.FollowTwitter(twitterMatch.group('tweeter'), twitterMatch.group('tweetID'))
        elif steamMatch:
            return self.FollowSteam(steamMatch.group('steamType'), steamMatch.group('steamID'))
        elif ksMatch:
            return self.FollowKickstarter(ksMatch.group('ksID'))
        elif twitchMatch:
            return self.FollowTwitch(twitchMatch.group('twitchChannel'))
        elif not re.search('\.(jpe?g|gif|png|bmp)$', url):
            return self.FollowStandard(url)
        
    def FollowYouTube(self, videoID):
        if self.youtubeKey is None:
            return '[YouTube API key not found]'

        fields = 'items(id,snippet(title,description,channelTitle,liveBroadcastContent),contentDetails(duration),statistics(viewCount),liveStreamingDetails(scheduledStartTime))'
        parts = 'snippet,contentDetails,statistics,liveStreamingDetails'
        url = 'https://www.googleapis.com/youtube/v3/videos?id={}&fields={}&part={}&key={}'.format(videoID, fields, parts, self.youtubeKey)
        
        webPage = web.fetchURL(url)
        j = json.loads(webPage.body)

        if 'items' not in j:
            return None

        data = []

        vid = j['items'][0]

        title = vid['snippet']['title']
        data.append(title)
        channel = vid['snippet']['channelTitle']
        data.append(channel)
        if vid['snippet']['liveBroadcastContent'] == 'none':
            length = parse_duration(vid['contentDetails']['duration']).total_seconds()
            m, s = divmod(int(length), 60)
            h, m = divmod(m, 60)
            if h > 0:
                length = u'{0:02d}:{1:02d}:{2:02d}'.format(h, m, s)
            else:
                length = u'{0:02d}:{1:02d}'.format(m, s)

            data.append(length)
        elif vid['snippet']['liveBroadcastContent'] == 'upcoming':
            startTime = vid['liveStreamingDetails']['scheduledStartTime']
            startDateTime = dateutil.parser.parse(startTime)
            now = datetime.datetime.now(dateutil.tz.tzutc())
            delta = startDateTime - now
            timespan = string.deltaTimeToString(delta, 'm')
            timeString = assembleFormattedText(A.normal['Live in ', A.fg.cyan[A.bold[timespan]]])
            data.append(timeString)
            pass # time till stream starts, indicate it's upcoming
        elif vid['snippet']['liveBroadcastContent'] == 'live':
            status = str(assembleFormattedText(A.normal[A.fg.red[A.bold['{} Live']]]))
            status = status.format(u'●')
            data.append(status)
        else:
            pass # if we're here, wat

        views = int(vid['statistics']['viewCount'])
        data.append('{:,}'.format(views))

        description = vid['snippet']['description']
        if not description:
            description = u'<no description available>'
        description = re.sub('(\n|\s)+', ' ', description)
        limit = 150
        if len(description) > limit:
            description = u'{} ...'.format(description[:limit].rsplit(' ', 1)[0])
        data.append(description)

        return self.graySplitter.join(data)
    
    def FollowImgur(self, imgurID):
        if self.imgurClientID is None:
            return '[imgur Client ID not found]'

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
        
        webPage = web.fetchURL(url, headers)
        
        if webPage is None:
            url = 'https://api.imgur.com/3/gallery/{0}'.format(imgurID)
            webPage = web.fetchURL(url, headers)

        if webPage is None:
            return
        
        response = json.loads(webPage.body)
        
        imageData = response['data']

        if imageData['title'] is None:
            url = 'https://api.imgur.com/3/gallery/{0}'.format(imgurID)
            webPage = web.fetchURL(url, headers)
            if webPage is not None:
                imageData = json.loads(webPage.body)['data']

            if imageData['title'] is None:
                webPage = web.fetchURL('http://imgur.com/{0}'.format(imgurID))
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
                data.append(u'Size: {0:,d}kb'.format(int(imageData['size']/1024)))
        data.append(u'Views: {0:,d}'.format(imageData['views']))
        
        return self.graySplitter.join(data)

    def FollowTwitter(self, tweeter, tweetID):
        webPage = web.fetchURL('https://twitter.com/{0}/status/{1}'.format(tweeter, tweetID))

        soup = BeautifulSoup(webPage.body, 'lxml')

        tweet = soup.find(class_='permalink-tweet')
        
        user = tweet.find(class_='username').text

        tweetText = tweet.find(class_='tweet-text')
        
        tweetTimeText = tweet.find(class_='client-and-actions').text.strip()
        try:
            tweetTimeText = time.strftime('%Y/%m/%d %H:%M', time.strptime(tweetTimeText, '%I:%M %p - %d %b %Y'))
        except ValueError:
            pass
        tweetTimeText = re.sub(r'[\r\n\s]+', u' ', tweetTimeText)

        links = tweetText.find_all('a', {'data-expanded-url': True})
        for link in links:
            link.string = ' ' + link['data-expanded-url']

        embeddedLinks = tweetText.find_all('a', {'data-pre-embedded': 'true'})
        for link in embeddedLinks:
            link.string = ' ' + link['href']

        text = string.unescapeXHTML(tweetText.text)
        text = re.sub('[\r\n]+', self.graySplitter, text)

        formatString = str(assembleFormattedText(A.normal[A.fg.gray['[{0}]'], A.bold[' {1}:'], ' {2}']))

        return formatString.format(tweetTimeText, user, text)

    def FollowSteam(self, steamType, steamId):
        steamType = {'app': 'app', 'sub': 'package'}[steamType]
        webPage = web.fetchURL('http://store.steampowered.com/api/{0}details/?{0}ids={1}&cc=US&l=english&v=1'.format(steamType, steamId))

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
                data.append(u'Released: ' + releaseDate['date'])
        else:
            data.append(assembleFormattedText(A.normal['To Be Released: ', A.fg.cyan[A.bold[str(releaseDate['date'])]]]))

        # metacritic
        # http://www.metacritic.com/faq#item32 (Why is the breakdown of green, yellow, and red scores different for games?)
        if 'metacritic' in appData:
            metaScore = appData['metacritic']['score']
            if metaScore < 50:
                metacritic = assembleFormattedText(A.normal[A.fg.red[str(metaScore)]])
            elif metaScore < 75:
                metacritic = assembleFormattedText(A.normal[A.fg.orange[str(metaScore)]])
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
            prices = {key: val for key, val in iteritems(prices) if val}

            priceString = u'/'.join([currencies[val['currency']] + str(val['final'] / 100.0) for val in prices.values()])
            if prices['USD']['discount_percent'] > 0:
                priceString += assembleFormattedText(A.normal[A.fg.green[A.bold[' ({0}% sale!)'.format(prices['USD']['discount_percent'])]]])

            data.append(priceString)

        # platforms
        if 'platforms' in appData:
            platforms = appData['platforms']
            platformArray = []
            if platforms['windows']:
                platformArray.append(u'Win')
            else:
                platformArray.append(u'---')
            if platforms['mac']:
                platformArray.append(u'Mac')
            else:
                platformArray.append(u'---')
            if platforms['linux']:
                platformArray.append(u'Lin')
            else:
                platformArray.append(u'---')
            data.append(u'/'.join(platformArray))
        
        # description
        if 'about_the_game' in appData and appData['about_the_game'] is not None:
            limit = 100
            description = re.sub(r'(<[^>]+>|[\r\n\t])+', assembleFormattedText(A.normal[' ', A.fg.gray['>'], ' ']), appData['about_the_game'])
            if len(description) > limit:
                description = u'{0} ...'.format(description[:limit].rsplit(' ', 1)[0])
            data.append(description)

        return self.graySplitter.join(data)

    @classmethod
    def getSteamPrice(cls, appType, appId, region):
        webPage = web.fetchURL('http://store.steampowered.com/api/{0}details/?{0}ids={1}&cc={2}&l=english&v=1'.format(appType, appId, region))
        priceField = {'app': 'price_overview', 'package': 'price'}[appType]
        response = json.loads(webPage.body)
        
        if 'data' not in response[appId]:
            return
        
        if region == 'AU':
            response[appId]['data'][priceField]['currency'] = 'AUD'
        return response[appId]['data'][priceField]

    def FollowKickstarter(self, ksID):
        webPage = web.fetchURL('https://www.kickstarter.com/projects/{}/description'.format(ksID))

        soup = BeautifulSoup(webPage.body, 'lxml')

        data = []

        shorturl = soup.find(rel='shorturl')['href']
        if shorturl is None:
            shorturl = 'https://www.kickstarter.com/projects/{}/'.format(ksID)

        title = soup.find(property='og:title')
        if title is not None:
            # live projects
            creator = soup.find(attrs={'data-modal-class': 'modal_project_by'})
            # completed projects
            if creator is None or not creator.text:
                creator = soup.find(class_='green-dark', attrs={'data-modal-class': 'modal_project_by'})
            if creator is not None:
                data.append(str(assembleFormattedText(A.normal['{0}',
                                                                   A.fg.gray[' by '],
                                                                   '{1}'])).format(title['content'].strip(),
                                                                                   creator.text.strip()))
            else:
                data.append(title['content'].strip())

        stats = soup.find(id='stats')
        # projects in progress
        if stats is not None:
            backerCount = soup.find(id='backers_count')
            if backerCount is not None:
                backerCount = int(backerCount['data-backers-count'])
        # completed projects
        else:
            backerCount = soup.find(class_='NS_campaigns__spotlight_stats')
            if backerCount is not None:
                backerCount = int(backerCount.b.text.strip().split()[0].replace(',', ''))

        data.append('Backers: {:,d}'.format(backerCount))

        if stats is not None:
            pledgeData = soup.find(id='pledged')
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
                pledged = float(re.sub(r'[^0-9.]', u'', pledgedString))
                goal = float(re.sub(r'[^0-9.]', u'', goalString))
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
            percentageString = A.fg.green['({2:,.0f}% funded)']
        else:
            percentageString = A.fg.red['({2:,.0f}% funded)']

        pledgePerBackerString = A.fg.gray['{3:,.0f}/backer']

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
            duration = soup.find(id='project_duration_data')

            if duration is not None:
                remaining = float(duration['data-hours-remaining'])
                days = math.floor(remaining/24)
                hours = remaining % 24

                data.append('Duration: {0:.0f} days {1:.1f} hours to go'.format(days, hours))

        return self.graySplitter.join(data)

    def FollowTwitch(self, channel):
        # Heavily based on Didero's DideRobot code for the same
        # https://github.com/Didero/DideRobot/blob/06629fc3c8bddf8f729ce2d27742ff999dfdd1f6/commands/urlTitleFinder.py#L37
        # TODO: other stats?
        if self.twitchClientID is None:
            return '[Twitch Client ID not found]'
        
        chanData = {}
        channelOnline = False
        twitchHeaders = [('Accept', 'application/vnd.twitchtv.v3+json'),
                         ('Client-ID', self.twitchClientID)]
        webPage = web.fetchURL(u'https://api.twitch.tv/kraken/streams/{}'.format(channel), twitchHeaders)

        streamData = json.loads(webPage.body)

        if 'stream' in streamData and streamData['stream'] is not None:
            chanData = streamData['stream']['channel']
            channelOnline = True
        elif 'error' not in streamData:
            webPage = web.fetchURL(u'https://api.twitch.tv/kraken/channels/{}'.format(channel), twitchHeaders)
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

            return channelInfo
    
    def FollowStandard(self, url):
        webPage = web.fetchURL(url)
        
        if webPage is None:
            return

        if webPage.responseUrl != url:
            return self.dispatchToFollows(webPage.responseUrl)
        
        title = self.GetTitle(webPage.body)
        if title is not None:
            return u'{0} (at {1})'.format(title, webPage.domain)
        
        return

    def GetTitle(self, webpage):
        soup = BeautifulSoup(webpage, 'lxml')
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


urlfollow = URLFollow()
