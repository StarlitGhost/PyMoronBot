from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import WebUtils
from Data.api_keys import load_key
from Data import ignores

import re
import HTMLParser
import json
from bs4 import BeautifulSoup
from twisted.words.protocols.irc import assembleFormattedText, attributes as A

class Instantiate(Function):
    Help = 'automatic function that follows urls and grabs information about the resultant webpage'
    
    htmlParser = HTMLParser.HTMLParser()
    
    graySplitter = assembleFormattedText(A.normal[' ', A.fg.gray['|'], ' '])

    def __init__(self):
        self.youtubeKey = load_key(u'YouTube')
        self.imgurClientID = load_key(u'imgur Client ID')
    
    def GetResponse(self, message):
        if message.Type not in ['PRIVMSG', 'ACTION']:
            return
        
        if ignores.ignoreList is not None:
            if message.User.Name in ignores.ignoreList:
                return

        match = re.search('(?P<url>https?://[^\s]+)', message.MessageString, re.IGNORECASE)
        if not match:
            return
        
        youtubeMatch = re.search('(www\.youtube\.com/watch.+v=|youtu\.be/)(?P<videoID>[^&#]+)', match.group('url'))
        imgurMatch   = re.search('(i\.)?imgur\.com/(?P<imgurID>[^\.]+)', match.group('url'))
        twitterMatch = re.search('twitter.com/(?P<tweeter>[^/]+)/status/(?P<tweetID>[0-9]+)', match.group('url'))
        steamMatch   = re.search('store.steampowered.com/app/(?P<steamAppID>[0-9]+)', match.group('url'))
        
        if youtubeMatch:
            return self.FollowYouTube(youtubeMatch.group('videoID'), message)
        elif imgurMatch:
            return self.FollowImgur(imgurMatch.group('imgurID'), message)
        elif twitterMatch:
            return self.FollowTwitter(twitterMatch.group('tweeter'), twitterMatch.group('tweetID'), message)
        elif steamMatch:
            return self.FollowSteam(steamMatch.group('steamAppID'), message)
        elif not re.search('\.(jpe?g|gif|png|bmp)$', match.group('url')):
            return self.FollowStandard(match.group('url'), message)
        
    def FollowYouTube(self, videoID, message):
        if self.youtubeKey is None:
            return IRCResponse(ResponseType.Say, '[YouTube API key not found]', message.ReplyTo)

        url = 'https://gdata.youtube.com/feeds/api/videos/{0}?v=2&key={1}'.format(videoID, self.youtubeKey)
        
        webPage = WebUtils.FetchURL(url)
        webPage.Page = webPage.Page.decode('utf-8')
        
        titleMatch = re.search('<title>(?P<title>[^<]+?)</title>', webPage.Page)
        
        if titleMatch:
            lengthMatch = re.search("<yt:duration seconds='(?P<length>[0-9]+?)'/>", webPage.Page)
            descMatch = re.search("<media:description type='plain'>(?P<desc>[^<]+?)</media:description>", webPage.Page)
            
            title = titleMatch.group('title')
            title = self.htmlParser.unescape(title)
            length = lengthMatch.group('length')
            m, s = divmod(int(length), 60)
            h, m = divmod(m, 60)
            if h > 0:
                length = u'{0:02d}:{1:02d}:{2:02d}'.format(h,m,s)
            else:
                length = u'{0:02d}:{1:02d}'.format(m,s)

            description = u'<no description available>'
            if descMatch:
                description = descMatch.group('desc')
                description = re.sub('<[^<]+?>', '', description)
                description = self.htmlParser.unescape(description)
                description = re.sub('\n+', ' ', description)
                description = re.sub('\s+', ' ', description)
                if len(description) > 150:
                    description = description[:147] + u'...'
                
            return IRCResponse(ResponseType.Say, self.graySplitter.join([title, length, description]), message.ReplyTo)
        
        return
    
    def FollowImgur(self, id, message):
        if self.imgurClientID is None:
            return IRCResponse(ResponseType.Say, '[imgur Client ID not found]', message.ReplyTo)

        if id.startswith('gallery/'):
            id = id.replace('gallery/', '')

        url = ''
        albumLink = False
        if id.startswith('a/'):
            id = id.replace('a/', '')
            url = 'https://api.imgur.com/3/album/{0}'.format(id)
            albumLink = True
        else:
            url = 'https://api.imgur.com/3/image/{0}'.format(id)

        headers = [('Authorization', 'Client-ID {0}'.format(self.imgurClientID))]
        
        webPage = WebUtils.FetchURL(url, headers)
        
        if webPage is None:
            url = 'https://api.imgur.com/3/gallery/{0}'.format(id)
            webPage = WebUtils.FetchURL(url, headers)

        if webPage is None:
            return
        
        response = json.loads(webPage.Page)
        
        imageData = response['data']

        if imageData['title'] is None:
            url = 'https://api.imgur.com/3/gallery/{0}'.format(id)
            webPage = WebUtils.FetchURL(url, headers)
            if webPage is not None:
                imageData = json.loads(webPage.Page)['data']

            if imageData['title'] is None:
                webPage = WebUtils.FetchURL('http://imgur.com/{0}'.format(id))
                imageData['title'] = self.GetTitle(webPage.Page).replace(' - Imgur', '')
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
            if imageData.has_key('is_album') and imageData['is_album']:
                data.append(u'Album: {0:,d} Images'.format(len(imageData['images'])))
            else:
                if imageData[u'animated']:
                    data.append(u'\x032\x02Animated!\x0F')
                data.append(u'{0:,d}x{1:,d}'.format(imageData['width'], imageData['height']))
                data.append(u'Size: {0:,d}kb'.format(int(imageData['size'])/1024))
        data.append(u'Views: {0:,d}'.format(imageData['views']))
        
        return IRCResponse(ResponseType.Say, self.graySplitter.join(data), message.ReplyTo)

    def FollowTwitter(self, tweeter, tweetID, message):
        webPage = WebUtils.FetchURL('https://twitter.com/{0}/status/{1}'.format(tweeter, tweetID))

        soup = BeautifulSoup(webPage.Page)

        tweet = soup.find('div', {'class' : 'permalink-tweet'})
        
        user = tweet.find('span', {'class' : 'username'}).text

        text = re.sub('[\r\n]+', self.graySplitter, tweet.find('p', {'class' : 'tweet-text'}).text)

        formatString = unicode(assembleFormattedText(A.normal[A.bold['{0}:'], ' {1}']))

        return IRCResponse(ResponseType.Say, formatString.format(user, text), message.ReplyTo)

    def FollowSteam(self, steamAppId, message):
        webPage = WebUtils.FetchURL('http://store.steampowered.com/app/{0}/'.format(steamAppId))

        soup = BeautifulSoup(webPage.Page)

        title = soup.find('div', {'class' : 'apphub_AppName'}).text.strip()
        description = soup.find('div', {'class' : 'game_description_snippet'}).text.strip()
        limit = 200
        if len(description) > limit:
            description = '{0} ...'.format(description[:limit].rsplit(' ', 1)[0])

        details = soup.find('div', {'class' : 'details_block'})
        genres = 'Genres: ' + ', '.join([link.text for link in details.select('a[href*="/genre/"]')])
        releaseDate = re.findall(u'Release Date\: .+', details.text, re.MULTILINE | re.IGNORECASE)[0]

        return IRCResponse(ResponseType.Say, self.graySplitter.join([title, genres, releaseDate, description]), message.ReplyTo)
    
    def FollowStandard(self, url, message):
        webPage = WebUtils.FetchURL(url)
        
        if webPage is None:
            return
        
        title = self.GetTitle(webPage.Page)
        if title is not None:
            return IRCResponse(ResponseType.Say, u'{0} (at {1})'.format(title, webPage.Domain), message.ReplyTo)
        
        return

    def GetTitle(self, webpage):
        match = re.search('<title\s*>\s*(?P<title>.*?)</title\s*>', webpage, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group('title')
            title = title.decode('utf-8')
            title = re.sub('(\n|\r)+', '', title)
            title = title.strip()
            title = re.sub('\s+', ' ', title)
            title = re.sub('<[^<]+?>', '', title)
            title = self.htmlParser.unescape(title)
            
            if len(title) > 300:
                title = title[:300] + "..."
            
            return title
        
        return None
