from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function

import socket
origGetAddrInfo = socket.getaddrinfo
def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)
socket.getaddrinfo = getAddrInfoWrapper

import re
import urllib, urllib2

class Instantiate(Function):
    Help = 'mtg(f) <card name> - fetches details of the Magic: The Gathering card you specify from gatherer.wizards.com. mtgf includes the flavour text, if it has any'
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        match = re.search('^mtgf?$', message.Command, re.IGNORECASE)
        if not match:
            return
        
        searchTerm = 'http://gatherer.wizards.com/pages/search/default.aspx?name='
        for param in message.ParameterList:
            searchTerm += '+[%s]' % param
        
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        
        conn = opener.open(searchTerm)
        page = conn.read()
        conn.close()
        page = re.sub('\s+', ' ', page)
        page = re.sub('\n', '', page)
        
        if page.find('Card Name:') <= 0:
            return IRCResponse(ResponseType.Say, 'Multiple or no cards found: ' + searchTerm, message.ReplyTo)
        
        name = ''
        manaCost = ''
        convCost = ''
        types = ''
        cardText = ''
        flavText = ''
        attDef = ''
        rarity = ''
    
        name = re.search('Card Name:</div> <div class="value"> (?P<name>[^<]+)', page).group('name')
        if page.find('Mana Cost:') >= 0:
            manaCost = re.search('Mana Cost:</div> <div class="value"> (?P<cost>.+?)</div>', page).group('cost')
            manaCost = ' | MC: ' + re.sub('<img.+?name=([^&"]+).+?>', "\\1", manaCost)
            convCost = ' | CMC: ' + re.search('d Mana Cost:</div> <div class="value"> (?P<cost>[^<]+)', page).group('cost')
        types = ' | T: ' + re.search('Types:</div> <div class="value"> (?P<types>[^<]+)', page).group('types')
        if page.find('Card Text:') >= 0:
            cardText = re.search('Card Text:</div> <div class="value"> (?P<text>.+?)</div></div>', page).group('text')
            cardText = re.sub('<img.+?name=([^&"]+).+?>', '\\1', cardText)
            cardText = re.sub('</div>', ' > ', cardText)
            cardText = ' | CT: ' + re.sub('<.*?>', '', cardText)
        if message.Command.endswith('f') and page.find('Flavor Text:') >= 0:
            flavText = re.search('Flavor Text:</div> (?P<flavour>.+?)</div></div>', page).group('flavour')
            flavText = ' | FT:' + re.sub('<.*?>', '', flavText)
        if page.find('P/T:') >= 0:
            attDef = ' | A/D: ' + re.search('P/T:</div> <div class="value"> (?P<attdef>[^<]+)', page).group('attdef').replace(' ', '')
        rarity = ' | R: ' + re.search('Rarity:</div> <div class="value"> <.+?>(?P<rarity>[^<]+)', page).group('rarity')
    
        reply = name + manaCost + convCost + types + cardText + flavText + attDef + rarity
    
        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)
