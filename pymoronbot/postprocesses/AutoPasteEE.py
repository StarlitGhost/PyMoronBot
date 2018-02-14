# -*- coding: utf-8 -*-
"""
Created on May 21, 2014

@author: Tyranic-Moron
"""

from pymoronbot.postprocessinterface import PostProcessInterface
from pymoronbot.utils import string, web


class AutoPasteEE(PostProcessInterface):

    priority = -99

    def execute(self, response):
        """
        @type response: IRCResponse
        """
        limit = 700  # chars
        expire = 10  # minutes
        if len(response.Response) > limit:
            replaced = web.pasteEE(string.stripFormatting(response.Response),
                                        u'Response longer than {0} chars intended for {1}'.format(limit,
                                                                                                  response.Target),
                                   expire)

            response.Response = u'Response too long, pasted here instead: {0} (Expires in {1} minutes)'.format(replaced,
                                                                                                               expire)
        return response
