from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
import WebUtils

import re

from bs4 import BeautifulSoup

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
        
        webPage = WebUtils.FetchURL(searchTerm)
        page = webPage.Page
        page = re.sub('\s+', ' ', page)
        page = re.sub('\n', '', page)
        
        if page.find('Card Name:') <= 0:
            return IRCResponse(ResponseType.Say, 'Multiple or no cards found: ' + searchTerm, message.ReplyTo)
            
        soup = BeautifulSoup(webPage.Page)
        
        name = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_nameRow'}).find('div', 'value').text.strip()
        types = ' | T: ' + soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_typeRow'}).find('div', 'value').text.strip()
        rarity = ' | R: ' + soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_rarityRow'}).find('div', 'value').text.strip()
        
        manaCost = ''
        convCost = ''
        cardText = ''
        flavText = ''
        attDef = ''
        
        if page.find('Mana Cost:') >= 0:
            manaCost = re.search('Mana Cost:</div> <div class="value"> (?P<cost>.+?)</div>', page).group('cost')
            manaCost = ' | MC: ' + re.sub('<img.+?name=([^&"]+).+?>', "\\1", manaCost)
            convCost = ' | CMC: ' + re.search('d Mana Cost:</div> <div class="value"> (?P<cost>[^<]+)', page).group('cost')
        if page.find('Card Text:') >= 0:
            cardText = re.search('Card Text:</div> <div class="value"> (?P<text>.+?)</div></div>', page).group('text')
            cardText = re.sub('<img.+?name=([^&"]+).+?>', '\\1', cardText)
            cardText = re.sub('</div>', ' > ', cardText)
            cardText = ' | CT: ' + re.sub('<.*?>', '', cardText)
        if message.Command.endswith('f') and page.find('Flavor Text:') >= 0:
            flavText = re.search('Flavor Text:</div> (?P<flavour>.+?)</div></div>', page).group('flavour')
            flavText = ' | FT:' + re.sub('<.*?>', '', flavText)
        if page.find('P/T:') >= 0:
            attDef = ' | A/D: ' + re.search('P/T:</b></div> <div class="value"> (?P<attdef>[^<]+)', page).group('attdef').replace(' ', '')
    
        reply = name + manaCost + convCost + types + cardText + flavText + attDef + rarity
        
        reply = reply.replace(u' \u2014','-').encode('ascii', 'ignore')
    
        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)
