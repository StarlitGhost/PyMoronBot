from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import WebUtils

import re
import HTMLParser
import json

class Instantiate(Function):
    Help = 'automatic function that follows urls and grabs information about the resultant webpage'
    
    htmlParser = HTMLParser.HTMLParser()
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('(?P<url>https?://[^\s]+)', message.MessageString, re.IGNORECASE)
        if not match:
            return
        
        youtubeMatch = re.search('(www\.youtube\.com/watch.+v=|youtu\.be/)(?P<videoID>[^&#]+)', match.group('url'))
        imgurMatch   = re.search('(i\.)?imgur\.com/(?P<imgurID>[^\.]+)', match.group('url'))
        if youtubeMatch:
            return self.FollowYouTube(youtubeMatch.group('videoID'), message)
        elif imgurMatch:
            return self.FollowImgur(imgurMatch.group('imgurID'), message)
        elif not re.search('\.(jpe?g|gif|png|bmp)$', match.group('url')):
            return self.FollowStandard(match.group('url'), message)
        
    def FollowYouTube(self, videoID, message):
        url = 'https://gdata.youtube.com/feeds/api/videos/%s?v=2&key=AI39si4LaIHfBlDmxNNRIqZjXYlDgVTmUVa7p8dSE8_bI45a9leskPQKauV7qi-qmAqjf6zjTdhwAfJxOfkxNcYOmloh8B1X9Q' % videoID
        
        webPage = WebUtils.FetchURL(url)
        
        titleMatch = re.search('<title>(?P<title>[^<]+?)</title><content', webPage.Page)
        
        if titleMatch:
            lengthMatch = re.search("<yt:duration seconds='(?P<length>[0-9]+?)'/>", webPage.Page)
            descMatch = re.search("<media:description type='plain'>(?P<desc>[^<]+?)</media:description>", webPage.Page)
            
            title = titleMatch.group('title')
            title = self.htmlParser.unescape(title)
            length = lengthMatch.group('length')
            m, s = divmod(int(length), 60)
            h, m = divmod(m, 60)
            if h > 0:
                length = '{0:02d}:{1:02d}:{2:02d}'.format(h,m,s)
            else:
                length = '{0:02d}:{1:02d}'.format(m,s)
            description = descMatch.group('desc')
            description = re.sub('<[^<]+?>', '', description)
            description = self.htmlParser.unescape(description)
            description = re.sub('\n+', ' ', description)
            description = re.sub('\s+', ' ', description)
            if len(description) > 200:
                description = description[:197] + '...'
                
            return IRCResponse(ResponseType.Say, '{0} | {1} | {2}'.format(title, length, description), message.ReplyTo)
        
        return
    
    def FollowImgur(self, id, message):
        clientID = 'cc2c410cd122a79'
        clientSecret = '501db78ba87c47393db86c4a557073ee97efdc88'
        
        url = 'https://api.imgur.com/3/image/{0}'.format(id)
        headers = [('Authorization', 'Client-ID {0}'.format(clientID))]
        
        webPage = WebUtils.FetchURL(url, headers)
        
        if webPage is None:
            return
        
        response = json.loads(webPage.Page)
        
        imageData = response['data']
        
        data = []
        data.append(imageData['title'])
        data.append('{0}x{1}'.format(imageData['width'], imageData['height']))
        data.append('Animated: {0}'.format(imageData['animated']))
        data.append('Size: {0}kb'.format(int(imageData['size'])/1024))
        data.append('Views: {0}'.format(imageData['views']))
        
        return IRCResponse(ResponseType.Say, ' | '.join(data), message.ReplyTo)
    
    def FollowStandard(self, url, message):
        webPage = WebUtils.FetchURL(url)
        
        if webPage is None:
            return
        
        match = re.search('<title\s*>\s*(?P<title>.*?)</title\s*>', webPage.Page, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group('title')
            title = re.sub('(\n|\r)+', '', title)
            title = title.strip()
            title = re.sub('\s+', ' ', title)
            title = re.sub('<[^<]+?>', '', title)
            title = self.htmlParser.unescape(title)
        
            return IRCResponse(ResponseType.Say, '{0} (at {1})'.format(title, webPage.Domain), message.ReplyTo)
        
        return

