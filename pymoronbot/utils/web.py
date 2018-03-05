# -*- coding: utf-8 -*-
import requests
import json
import re
import time

from builtins import str
from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlparse
from six import iteritems

from apiclient.discovery import build

from pymoronbot.utils.api_keys import load_key


class URLResponse(object):
    def __init__(self, response):
        self.domain = urlparse(response.url).netloc
        self._body = None
        self._response = response
        self._responseCloser = response.close
        self.headers = response.headers
        self.responseUrl = response.url

    def __del__(self):
        if self._body is None:
            self._responseCloser()

    @property
    def body(self):
        if self._body is None:
            self._body = self._response.content.decode('utf-8', 'ignore')
            self._responseCloser()
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @body.deleter
    def body(self):
        del self._body


def fetchURL(url, params=None, extraHeaders=None):
    """
    @type url: unicode
    @type extraHeaders: dict
    @rtype: URLResponse
    """
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Accept": "text/*, "
                  "application/xml, application/xhtml+xml, "
                  "application/rss+xml, application/atom+xml, application/rdf+xml, "
                  "application/json"
    }
    if extraHeaders:
        headers.update(extraHeaders)
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        responseHeaders = response.headers
        pageType = responseHeaders["content-type"]

        # Make sure we don't download any unwanted things
        #              |   text|                       rss feeds and xml|                      json|
        if re.match(r"^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$", pageType):
            urlResponse = URLResponse(response)
            return urlResponse
        else:
            response.close()

    except requests.exceptions.RequestException as e:
        today = time.strftime("[%H:%M:%S]")
        reason = str(e)
        print("{} *** ERROR: Fetch from \"{}\" failed: {}".format(today, url, reason))


# mostly taken directly from Heufneutje's PyHeufyBot
# https://github.com/Heufneutje/PyHeufyBot/blob/eb10b5218cd6b9247998d8795d93b8cd0af45024/pyheufybot/utils/webutils.py#L43
def postURL(url, data, extraHeaders=None):
    """
    @type url: unicode
    @type values: dict[unicode, T]
    @type extraHeaders: dict[unicode, unicode]
    @rtype: URLResponse
    """
    headers = {"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0"}
    if extraHeaders:
        headers.update(extraHeaders)

    for k, v in iteritems(data):
        data[k] = str(v)

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        responseHeaders = response.headers
        pageType = responseHeaders["content-type"]

        # Make sure we don't download any unwanted things
        #              |   text|                       rss feeds and xml|                      json|
        if re.match(r"^(text/.*|application/((rss|atom|rdf)\+)?xml(;.*)?|application/(.*)json(;.*)?)$", pageType):
            urlResponse = URLResponse(response)
            return urlResponse
        else:
            response.close()

    except requests.exceptions.RequestException as e:
        today = time.strftime("[%H:%M:%S]")
        reason = str(e)
        print("{} *** ERROR: Post to \"{}\" failed: {}".format(today, url, reason))


def shortenGoogl(url):
    """
    @type url: unicode
    @rtype: unicode
    """
    post = {"longUrl": url}

    googlKey = load_key(u'goo.gl')

    if googlKey is None:
        return "[goo.gl API key not found]"

    apiURL = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(googlKey)

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(apiURL, json=post, headers=headers)
        responseJson = response.json()
        if 'error' in responseJson:
            return '[Googl Error: {} {}]'.format(responseJson['error']['message'], post['longUrl'])
        return responseJson['id']

    except requests.exceptions.RequestException as e:
        print("Goo.gl error: {}".format(e))


def googleSearch(query):
    """
    @type query: unicode
    @rtype: dict[unicode, T]
    """
    googleKey = load_key(u'Google')
    if not googleKey:
        return None
    
    service = build('customsearch', 'v1', developerKey=googleKey)
    res = service.cse().list(
        q = query,
        cx = '002603151577378558984:xiv3qbttad0'
    ).execute()
    return res


# mostly taken directly from Heufneutje's PyHeufyBot
# https://github.com/Heufneutje/PyHeufyBot/blob/eb10b5218cd6b9247998d8795d93b8cd0af45024/pyheufybot/utils/webutils.py#L74
def pasteEE(data, description, expire, raw=True):
    """
    @type data: unicode
    @type description: unicode
    @type expire: int
    @type raw: bool
    @rtype: unicode
    """
    pasteEEKey = load_key(u'Paste.ee')

    values = {u"key": "public",
              u"description": description,
              u"paste": data,
              u"expiration": expire,
              u"format": u"json"}
    result = postURL(u"http://paste.ee/api", values)
    if result:
        jsonResult = json.loads(result.body)
        if jsonResult["status"] == "success":
            linkType = "raw" if raw else "link"
            return jsonResult["paste"][linkType]
        elif jsonResult["status"] == "error":
            return u"An error occurred while posting to Paste.ee, code: {}, reason: {}"\
                .format(jsonResult["errorcode"], jsonResult["error"])
