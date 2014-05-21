# -*- coding: utf-8 -*-

# somewhat hacky and I forget what this is solving
import socket

origGetAddrInfo = socket.getaddrinfo

def getAddrInfoWrapper(host, port, _=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

socket.getaddrinfo = getAddrInfoWrapper

from urllib import urlencode, quote
from urllib2 import build_opener, Request, urlopen, URLError
from urlparse import urlparse
import json
import re
import time

from Data.api_keys import load_key


class URLResponse(object):
    def __init__(self, domain, body, headers):
        self.domain = domain
        self.body = body
        self.headers = headers


def fetchURL(url, extraHeaders=None):
    """
    @type url: unicode
    @type extraHeaders: dict
    @rtype: URLResponse
    """
    headers = [("User-agent", "Mozilla/5.0")]
    if extraHeaders:
        for header in extraHeaders:
            # For whatever reason headers are defined in a different way in opener than they are in a normal urlopen
            headers.append((header, extraHeaders[header]))
    try:
        opener = build_opener()
        opener.addheaders = headers
        response = opener.open(url)
        responseHeaders = response.info().dict
        print '{0} headers: {1}'.format(urlparse(response.geturl()).hostname, responseHeaders)
        pageType = responseHeaders["content-type"]

        # Make sure we don't download any unwanted things
        #              |   text|                       rss feeds and xml|                      json|
        if re.match(r"^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$", pageType):
            urlResponse = URLResponse(urlparse(response.geturl()).hostname, response.read(), responseHeaders)
            response.close()
            return urlResponse
        else:
            response.close()

    except URLError as e:
        today = time.strftime("[%H:%M:%S]")
        reason = None
        if hasattr(e, "reason"):
            reason = "We failed to reach the server, reason: {}".format(e.reason)
        elif hasattr(e, "code"):
            reason = "The server couldn't fulfill the request, code: {}".format(e.code)
        print "{} *** ERROR: Fetch from \"{} \" failed: {}".format(today, url, reason)


# mostly taken directly from Heufneutje's PyHeufyBot
# https://github.com/Heufneutje/PyHeufyBot/blob/eb10b5218cd6b9247998d8795d93b8cd0af45024/pyheufybot/utils/webutils.py#L43
def postURL(url, values, extraHeaders=None):
    """
    @type url: unicode
    @type values: dict[unicode, T]
    @type extraHeaders: dict[unicode, unicode]
    @rtype: URLResponse
    """
    headers = {"User-agent": "Mozilla/5.0"}
    if extraHeaders:
        for header in extraHeaders:
            headers[header] = extraHeaders[header]

    data = urlencode(values)

    try:
        request = Request(url, data, headers)
        response = urlopen(request)
        responseHeaders = response.info().dict
        pageType = responseHeaders["content-type"]

        # Make sure we don't download any unwanted things
        #              |   text|                       rss feeds and xml|                      json|
        if re.match(r"^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$", pageType):
            urlResponse = URLResponse(urlparse(response.geturl()).hostname, response.read(), responseHeaders)
            response.close()
            return urlResponse
        else:
            response.close()

    except URLError as e:
        today = time.strftime("[%H:%M:%S]")
        reason = None
        if hasattr(e, "reason"):
            reason = "We failed to reach the server, reason: {}".format(e.reason)
        elif hasattr(e, "code"):
            reason = "The server couldn't fulfill the request, code: {}".format(e.code)
        print "{} *** ERROR: Post to \"{} \" failed: {}".format(today, url, reason)


def shortenGoogl(url):
    """
    @type url: unicode
    @rtype: unicode
    """
    post = '{{"longUrl": "{0}"}}'.format(url)

    googlKey = load_key(u'goo.gl')

    if googlKey is None:
        return "[goo.gl API key not found]"

    apiURL = 'https://www.googleapis.com/urlshortener/v1/url?key={0}'.format(googlKey)

    headers = {"Content-Type": "application/json"}

    try:
        request = Request(apiURL, post, headers)
        response = json.loads(urlopen(request).read())
        return response['id']

    except Exception, e:
        print "Goo.gl error: %s" % e


def googleSearch(query):
    """
    @type query: unicode
    @rtype: dict[unicode, T]
    """
    googleAPI = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q='
    webPage = fetchURL('{0}{1}'.format(googleAPI, quote(query)))
    j = json.loads(webPage.body)
    return j


# mostly taken directly from Heufneutje's PyHeufyBot
# https://github.com/Heufneutje/PyHeufyBot/blob/eb10b5218cd6b9247998d8795d93b8cd0af45024/pyheufybot/utils/webutils.py#L74
def pasteEE(data, description, expire):
    """
    @type data: unicode
    @type description: unicode
    @type expire: int
    @rtype: unicode
    """
    values = {u"key": u"public",
              u"description": description,
              u"paste": data,
              u"expiration": expire,
              u"format": u"json"}
    result = postURL(u"http://paste.ee/api", values)
    if result:
        jsonResult = json.loads(result.body)
        if jsonResult["status"] == "success":
            return jsonResult["paste"]["link"]
        elif jsonResult["status"] == "error":
            return u"An error occurred while posting to Paste.ee, code: {}, reason: {}".format(jsonResult["errorcode"],
                                                                                               jsonResult["error"])