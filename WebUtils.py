import socket
origGetAddrInfo = socket.getaddrinfo
def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)
socket.getaddrinfo = getAddrInfoWrapper

import urllib, urllib2, urlparse
import json
import re

from Data.api_keys import load_key

class WebPage():
    Domain = ''
    Page = ''
    Headers = {}
    
def FetchURL(url, headers=[('User-agent', 'Mozilla/5.0')]):
    opener = urllib2.build_opener()
    opener.addheaders = headers
    
    try:
        response = opener.open(url)
        response_headers = response.info().dict
        pageType = response_headers['content-type']
        
        #             |   text|                       rss feeds and xml|            json|
        if re.match('^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/json)$', pageType):
            page = WebPage()
            page.Domain = urlparse.urlparse(response.geturl()).hostname

            page.Page = response.read()
            page.Headers = response_headers

            response.close()
            return page

        response.close()
        
    except IOError, e:
        print url
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code

def SendToServer(url, text=None):
    opener = urllib2.build_opener()
    try:
        response = opener.open(url)
        return response.read()
        
    except IOError, e:
        print url
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code

def ShortenGoogl(url):
    post = '{{"longUrl": "{0}"}}'.format(url)
    
    googlKey = load_key(u'goo.gl')

    if googlKey is None:
        return "[goo.gl API key not found]"
    
    apiURL = 'https://www.googleapis.com/urlshortener/v1/url?key={0}'.format(googlKey)
    
    headers = {"Content-Type": "application/json"}
    
    try:
        request = urllib2.Request(apiURL, post, headers)
        response = json.loads(urllib2.urlopen(request).read())
        return response['id']

    except Exception, e:
        print "Goo.gl error: %s" % e

