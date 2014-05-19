# -*- coding: utf-8 -*-
import socket

# somewhat hacky and I forget what this is solving
import urllib

origGetAddrInfo = socket.getaddrinfo

def getAddrInfoWrapper(host, port, _=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

socket.getaddrinfo = getAddrInfoWrapper

import urllib2
import urlparse
import json
import re

from Data.api_keys import load_key


class WebPage(object):
    Domain = ''
    Page = ''
    Headers = {}


def fetchURL(url, headers=None):
    if not headers:
        headers = [('User-agent', 'Mozilla/5.0')]
    opener = urllib2.build_opener()
    opener.addheaders = headers

    try:
        response = opener.open(url)
        response_headers = response.info().dict
        pageType = response_headers['content-type']

        #             |   text|                       rss feeds and xml|                       json|
        if re.match('^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$', pageType):
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


def sendToServer(url, _=None):
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


def shortenGoogl(url):
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


def googleSearch(query):
    googleAPI = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q='
    webPage = fetchURL('{0}{1}'.format(googleAPI, urllib.quote(query)))
    j = json.loads(webPage.Page)
    return j
