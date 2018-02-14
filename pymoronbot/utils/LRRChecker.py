# -*- coding: utf-8 -*-
import datetime

aYearAgo = datetime.datetime.utcnow() - datetime.timedelta(days=365)
tenMinsAgo = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)

LRRChecker = {
    'LRRCast': {
        'url': 'http://feeds.feedburner.com/lrrcast',
        'lastUpdate': aYearAgo,
        'lastTitle': '',
        'lastLink': '',
        'lastCheck': tenMinsAgo,
        'aliases': ["podcast", "cast", "lrrc", "llrc", "lcast", "lc", 'chat'],
        'suppress': True},
    'LRR Blog': {
        'url': 'http://loadingreadyrun.com/blog/feed/',
        'lastUpdate': aYearAgo,
        'lastTitle': '',
        'lastLink': '',
        'lastCheck': tenMinsAgo,
        'aliases': ['blog'],
        'suppress': True}
}

