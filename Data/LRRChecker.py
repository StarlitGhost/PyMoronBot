import datetime

aYearAgo = datetime.datetime.utcnow() - datetime.timedelta(days=365)
tenMinsAgo = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)

LRRChecker = {
    'Unskippable': {
        'url': 'http://www.escapistmagazine.com/rss/videos/list/82.xml',
        'lastUpdate': aYearAgo,
        'lastTitle': '',
        'lastLink': '',
        'lastCheck': tenMinsAgo,
        'aliases': ['unskipable', 'unskip', 'us', 'u', 'skip'],
        'suppress': True },
    'LRR': {
        'url': 'http://www.escapistmagazine.com/rss/videos/list/123.xml',
        'lastUpdate': aYearAgo,
        'lastTitle': '',
        'lastLink': '',
        'lastCheck': tenMinsAgo,
        'aliases': ["loadingreadyrun", "l", "llr"],
        'suppress': True },
    'Feed Dump': {
        'url': 'http://www.escapistmagazine.com/rss/videos/list/171.xml',
        'lastUpdate': aYearAgo,
        'lastTitle': '',
        'lastLink': '',
        'lastCheck': tenMinsAgo,
        'aliases': ["feed", "dump", "fdump", "fd", "f", 'fump', 'frump', 'feeddump'],
        'suppress': True },
    'CheckPoint': {
        'url': 'http://penny-arcade.com/feed/show/checkpoint',
        'lastUpdate': aYearAgo,
        'lastTitle': '',
        'lastLink': '',
        'lastCheck': tenMinsAgo,
        'aliases': ["check", "point", "cp", "c"],
        'suppress': True },
    'LRRCast': {
        'url': 'http://feeds.feedburner.com/lrrcast',
        'lastUpdate': aYearAgo,
        'lastTitle': '',
        'lastLink': '',
        'lastCheck': tenMinsAgo,
        'aliases': ["podcast", "cast", "lrrc", "llrc", "lcast", "lc", 'chat'],
        'suppress': True },
    'Strip Search': {
        'url': 'http://www.penny-arcade.com/feed/show/strip-search',
        'lastUpdate': aYearAgo,
        'lastTitle': '',
        'lastLink': '',
        'lastCheck': tenMinsAgo,
        'aliases': ['strip', 'ss', 's', 'stripsearch', 'search'],
        'suppress': True }
    }

