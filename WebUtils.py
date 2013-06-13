import socket
origGetAddrInfo = socket.getaddrinfo
def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)
socket.getaddrinfo = getAddrInfoWrapper

import urllib, urllib2, urlparse
import json
import re

class WebPage():
    Domain = ''
    Page = ''
    
def FetchURL(url, headers=[('User-agent', 'Mozilla/5.0')]):
    opener = urllib2.build_opener()
    opener.addheaders = headers
    
    try:
        response = opener.open(url)
        pageType = response.info().gettype()
        
        if re.match('^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?)$', pageType):
            page = WebPage()
            page.Domain = urlparse.urlparse(response.geturl()).hostname
            page.Page = response.read()
            
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
    
    googlKey = 'AIzaSyCU7yKR6eTkme1cTUqFoSJxhG-v83trPy4'
    
    apiURL = 'https://www.googleapis.com/urlshortener/v1/url?key={0}'.format(googlKey)
    
    headers = {"Content-Type": "application/json"}
    
    try:
        request = urllib2.Request(apiURL, post, headers)
        response = json.loads(urllib2.urlopen(request).read())
        return response['id']

    except Exception, e:
        print "Goo.gl error: %s" % e

