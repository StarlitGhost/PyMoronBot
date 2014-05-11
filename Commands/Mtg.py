from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from CommandInterface import CommandInterface
from Utils import WebUtils

import re

from bs4 import BeautifulSoup

class Command(CommandInterface):
    triggers = ['mtg', 'mtgf']
    help = 'mtg(f) <card name> - fetches details of the Magic: The Gathering card you specify ' \
           'from gatherer.wizards.com. mtgf includes the flavour text, if it has any'

    def execute(self, message=IRCMessage):
        searchTerm = 'http://gatherer.wizards.com/pages/search/default.aspx?name='
        for param in message.ParameterList:
            searchTerm += '+[%s]' % param

        webPage = WebUtils.fetchURL(searchTerm)

        soup = BeautifulSoup(webPage.Page)

        name = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_nameRow'})
        if name is None:
            searchResults = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_searchResultsContainer'})
            if searchResults is None:
                return IRCResponse(ResponseType.Say, 'No cards found: ' + searchTerm, message.ReplyTo)
            else:
                cardItems = searchResults.find_all(class_ = 'cardItem')
                # potentially return first item here
                return IRCResponse(ResponseType.Say, '{0} cards found: {1}'.format(len(cardItems), searchTerm), message.ReplyTo)

        name = name.find('div', 'value').text.strip()
        types = u' | T: ' + soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_typeRow'}).find('div', 'value').text.strip()
        rarity = u' | R: ' + soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_rarityRow'}).find('div', 'value').text.strip()

        manaCost = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_manaRow'})
        if manaCost is not None:
            manaCost = unicode(manaCost.find('div', 'value'))
            manaCost = u' | MC: ' + self.translateSymbols(manaCost)
            manaCost = re.sub('<[^>]+?>', '', manaCost)
            manaCost = manaCost.replace('\n', '')
        else:
            manaCost = u''

        convCost = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_cmcRow'})
        if convCost is not None:
            convCost = u' | CMC: ' + convCost.find('div', 'value').text.strip()
        else:
            convCost = u''

        cardText = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_textRow'})
        if cardText is not None:
            cardTexts = cardText.find_all('div', 'cardtextbox')
            texts = []
            for text in cardTexts:
                text = self.translateSymbols(text)
                text = re.sub('<[^>]+?>', '', text)
                texts.append(text)
            cardText = u' | CT: ' + u' > '.join(texts)
        else:
            cardText = u''

        flavText = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_FlavorText'})
        if message.Command.endswith('f') and flavText is not None:
            flavTexts = flavText.find_all('div', 'cardtextbox')
            texts = []
            for text in flavTexts:
                texts.append(unicode(text.text))
            flavText = u' | FT: ' + ' > '.join(texts)
        else:
            flavText = u''

        powTough = soup.find('div', {'id' : 'ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ptRow'})
        if powTough is not None:
            powTough = u' | P/T: ' + powTough.find('div', 'value').text.strip().replace(' ', '')
        else:
            powTough = u''

        reply = name + manaCost + convCost + types + cardText + flavText + powTough + rarity

        return IRCResponse(ResponseType.Say, reply, message.ReplyTo)

    def translateSymbols(self, text):
        text = unicode(text)
        text = re.sub(r'<img.+?name=(tap).+?>', r'Tap', text) # tap
        text = re.sub(r'<img.+?name=([0-9]{2,}).+?>', r'\1', text) # long numbers
        text = re.sub(r'<img.+?name=([^&"])([^&"]).+?>', r'{\1/\2}', text) # hybrids
        text = re.sub(r'<img.+?name=([^&"]+).+?>', r'\1', text) # singles and any 'others' left over

        return text
