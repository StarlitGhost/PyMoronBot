# -*- coding: utf-8 -*-
import random
import datetime
import re

from CommandInterface import CommandInterface
from IRCMessage import IRCMessage
from IRCResponse import ResponseType, IRCResponse
from Data import ignores


class Responses(CommandInterface):
    acceptedTypes = ['PRIVMSG', 'ACTION']
    help = 'Talkwords from the mouth place - response <name> to enable/disable a particular response ' \
           '(might need to check the source for names)'

    def onLoad(self):
        try:
            self.responses = MobroResponseDict()

            ##################################
            #                                #
            #    ADD RESPONSES HERE, BRO     #
            #                                #
            ##################################

            #'''Example'''
            #self.responses.add(MobroResponse(	Name,
            #                   Response Message(s),
            #                   Regex(es),
            #                   ResponseType (default Say),
            #                   Enabled (default True),
            #                   Seconds Until Response Can Trigger Again (default 300),
            #                   All Regexes Must Match (default True)))

            '''Responds to inappropriately combined adjectives'''
            self.responses.add(MobroResponse('squishy',
                                             'GODDAMMIT, GET YOUR HAND OUT OF THERE',
                                             ["([^a-zA-Z]|^)wet (and|&|'?n'?) squishy([^a-zA-Z]|$)",
                                              "([^a-zA-Z]|^)squishy (and|&|'?n'?) wet([^a-zA-Z]|$)"],
                                             ResponseType.Say,
                                             True,
                                             300,
                                             False))

            '''Responds to the ocean as a caffeinated Pika'''
            self.responses.add(MobroResponse('ocean',
                                             'mimes out a *WHOOOOSH!*',
                                             '([^a-zA-Z]|^)ocean([^a-zA-Z]|$)',
                                             ResponseType.Do))

            '''Responds to incorrect windmill assumptions'''
            self.responses.add(MobroResponse('windmill',
                                             ['WINDMILLS DO NOT WORK THAT WAY!', 'GOODNIGHT!'],
                                             ['([^a-zA-Z]|^)windmills?([^a-zA-Z]|$)',
                                              '([^a-zA-Z]|^)cool([^a-zA-Z]|$)']))

            '''Responds to Pokemon as Joseph Ducreux'''
            self.responses.add(MobroResponse('pokemon',
                                             'Portable Atrocities! Must be encapsulated en masse!',
                                             '([^a-zA-Z]|^)pokemon([^a-zA-Z]|$)'))

            '''Guards against the Dutch'''
            self.responses.add(MobroResponse('dutch',
                                             'The Dutch, AGAIN!',
                                             '([^a-zA-Z]|^)dutch([^a-zA-Z]|$)'))

            '''Sensitive to bees'''
            self.responses.add(MobroResponse('bees',
                                             'BEES?! AAAARRGGHGHFLFGFGFLHL',
                                             '([^a-zA-Z]|^)bee+s?([^a-zA-Z]|$)'))

            '''Responds to cheese'''
            self.responses.add(MobroResponse('cheese',
                                             'loves cheese',
                                             '([^a-zA-Z]|^)cheese([^a-zA-Z]|$)',
                                             ResponseType.Do))

            '''Responds to JavaScript's insane shenanigans'''
            self.responses.add(MobroResponse('wat',
                                             'NaNNaNNaNNaN https://www.destroyallsoftware.com/talks/wat man!',
                                             '([^a-zA-Z]|^)wat([^a-zA-Z]|$)',
                                             ResponseType.Say,
                                             False))

            #Sorry man, I had to. I HAD to.
            '''Responds to Ponies'''
            self.responses.add(MobroResponse('ponies',
                                             'Ponies Ponies Ponies SWAG! https://www.youtube.com/watch?v=hx30VHwKa0Q',
                                             '([^a-zA-Z]|^)ponies([^a-zA-Z]|$)',
                                             ResponseType.Say,
                                             False))

            '''Responds to EVERYTHING being FINE'''
            self.responses.add(MobroResponse('everythingfine',
                                             "IT'S FINE, EVERYTHING IS FINE",
                                             "([^a-zA-Z]|^)everything('?s| is) fine([^a-zA-Z]|$)"))

            #This one needs to mess with the object to work right.
            '''Responds to DuctTape being a dick in minecraft'''
            def ducktapeMatch(message):
                match = re.search('([^a-zA-Z]|^)minecraft([^a-zA-Z]|$)', message, re.IGNORECASE)
                self.ductMatch = re.search('([^a-zA-Z]|^)(?P<duc>duc[kt]tape)([^a-zA-Z]|$)', message, re.IGNORECASE)
                return match and self.ductMatch

            def ducktapeTalkwords(message):
                return [IRCResponse(ResponseType.Say,
                                    'Just saying, %s is a dick in Minecraft' % self.ductMatch.group('duc'),
                                    message.ReplyTo)]

            ducktape = MobroResponse('ducktape', '', '')
            ducktape.match = ducktapeMatch
            ducktape.talkwords = ducktapeTalkwords
            self.responses.add(ducktape)

            '''Responds randomly to various animal sounds'''
            def animalMatch(message):
                matchDict = {
                    r'(w[o0]{2,}f|r+u+f{2,}|[a4]rf)': 'puppeh',
                    r'[s5]qu[e3][a4]k': 'mouse',
                    r'm[o0]{2,}': 'cow',
                    r'(tw[e3]{2,}t|c[a4]+w+)': 'bird',
                    r'n[e3]+[i1]+gh': 'horse',
                    r'r[i1]+b{2,}[i1]+t': 'frog',
                    r'bl[o0]{2,}p': 'fish',
                    r'[o0]+[i1]+n+k+': 'piggy',
                    r'h[o0]+n+k+': 'goose',
                    r'h[i1]+[s5]{2,}': 'snake',
                    r'r+[o0]+[a4]+r+': 'lion',
                    r'(h[o0]+w+l+|[a4]+w?[o0]{2,})': 'wolf',
                    r'bl[e3]{2,}p\s+bl[o0]{2,}p': 'droid',
                    r'y?[a4]r{2,}': 'pirate',
                    r'qu[a4]+ck': 'duck',
                    r'wh[o0]{2,}': 'owl',
                }

                self.animal = None
                for match, animal in matchDict.iteritems():
                    if re.search(r'^{}([^\sa-z]+)?$'.format(match), message, re.IGNORECASE):
                        self.animal = animal
                        return True

                return False

            def animalTalkwords(message):
                randomChance = random.randint(1, 20)
                if message.User.Name == 'Emily':
                    randomChance = random.randint(1, 25)
                if randomChance == 1:
                    ''' User Critically Failed '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is DEFINITELY NOT the Droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} critically fails at being a {}.'.format(message.User.Name, self.animal),
                                            message.ReplyTo)]

                elif randomChance <= 8:
                    ''' User Is Not A [animal] '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is not the Droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} is not a {}.'.format(message.User.Name, self.animal),
                                            message.ReplyTo)]
                elif randomChance <= 14:
                    '''User Might Be A [animal] '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} might be the Droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} /might/ be a {}.'.format(message.User.Name, self.animal),
                                            message.ReplyTo)]
                elif randomChance <= 19:
                    ''' User Is A [animal] '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is the Droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    elif self.animal == 'puppeh':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is such doge. wow.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} is DEFINITELY a {}.'.format(message.User.Name, self.animal),
                                            message.ReplyTo)]
                elif randomChance == 20:
                    ''' User Is A Critical [animal] '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is DEFINITELY the Droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} is a CRITICAL {}!'.format(message.User.Name, self.animal),
                                            message.ReplyTo)]
                else:
                    ''' Roll is outside of bounds, Magic! '''
                    return [IRCResponse(ResponseType.Say,
                                        'You are clearly a Magician rolling out of bounds like that.',
                                        message.ReplyTo)]

            animalResponse = MobroResponse('animal', '', '', seconds=0)
            animalResponse.match = animalMatch
            animalResponse.talkwords = animalTalkwords
            self.responses.add(animalResponse)

            '''Responds to boops'''
            def boopMatch(message):
                match = re.search('(^|[^a-z]+)b[o0]{2,}ps?([^a-z]+|$)', message, re.IGNORECASE)
                return match

            def boopTalkwords(message):
                boops = [
                    #"http://goo.gl/HJzfS",              # feline anatomy
                    "http://goo.gl/Umt61b",             # not boop ur nose, bite tur nose
                    "http://bit.ly/zA2bUY",             # i boop ur noes
                    "http://bit.ly/wQoI8p",             # hey cat, imma boop ur head, lol
                    "http://bit.ly/ACbm0J",             # Iz gunna boop yer nose, k?
                    "http://bit.ly/qNyEZk",             # what do you think mr t is daydreaming about?
                    "http://bit.ly/zJrjGF",             # jeans kitty boop
                    "http://goo.gl/d054n",              # This is called "aversion therapy."
                    "http://goo.gl/6IoB0",              # my grumpy button, ur pushin' it
                    "http://bit.ly/z79CJv",             # colonel goggie in the hallway with the nose boop
                    "http://bit.ly/yODbYA",             # You may go, but first I must boop your nose
                    "http://bit.ly/AdX2cw",             # boop, gotchur nose
                    "http://goo.gl/1Xu0LK",             # fluttershy & rainbow dash
                    "http://i.imgur.com/vC5gy.jpg",     # dog in car boop
                    "http://i.imgur.com/xmzLY.gif",     # cat lap booping dog
                    "http://i.imgur.com/NSAKo.jpg",     # orange cat perma-booping dog on bed
                    "http://bit.ly/NI0jYk",
                    "http://bit.ly/MKZqCJ",             # pinkie pie and twilight sparkle boop
                    "http://i.imgur.com/qeNvd.png",     # elephant boop
                    "http://i.imgur.com/wtK1T.jpg",     # jet booping tanker truck
                    "http://goo.gl/Nh4PK",              # demon booping the earth
                    "http://goo.gl/JHBKUb",             # real men head boop with kittens
                    "http://goo.gl/Juhcv",              # sweetie belle booping apple bloom
                    "http://i.imgur.com/BLQoL61.gif",   # darting boop
                    "http://i.imgur.com/3b2lSjd.gif",   # pounce boops
                    "http://i.imgur.com/P83UL.gif",     # reciprocated cat boop
                    "http://i.imgur.com/H7iNX8R.jpg",   # white cat nose boop
                    "http://i.imgur.com/NoYdYtU.jpg",   # Lil Retriever Learns How To Boop
                    "http://i.imgur.com/jWMdZ.jpg",     # black & white kitten boop
                    "http://i.imgur.com/dz81Dbs.jpg",   # puppy picnic boop
                    "http://i.imgur.com/0KWKb.gif",     # spinspinspin BOOP!
                    "http://i.minus.com/izXxGnlNFmVrN.gif",  # horse & excitable puppy boop
                    "http://i.imgur.com/UaNm6fv.gif",   # boop to turn off kitten
                    "http://i.imgur.com/QmVjLNQ.png",   # snow leopard boop
                    "http://i.imgur.com/HaAovQK.gif",   # darting bed boop
                    "http://i.imgur.com/Le4lOKX.gif",   # kitten gonna get him boop
                    "http://i.imgur.com/so5M2Mk.gif",   # shibe back boop
                    "http://i.imgur.com/P7Ca5Si.gif",   # shibe pikachu boop
                    "http://i.imgur.com/yvlmyNI.gif",   # quick run up boop walk away (NewClassic)
                    "http://goo.gl/9FTseh",             # Fluttershy & Pinkie Pie boop
                    "http://i.imgur.com/yexMjOl.gif",   # Archer boop
                    "http://goo.gl/l3lwH9",             # Cat boops a butt
                    "http://i.imgur.com/zOZvmTW.gif",   # Bunny bumper cars
                    "http://i.imgur.com/P0a8dU2.gif",   # Kitten beach boop loop
                    "http://i.imgur.com/LXFYmPU.gif",   # Nose-booped cat retreats under blanket
                    "http://i.imgur.com/6ZJLftO.gif",   # Cat booping a bunny's nose repeatedly
                    "http://i.imgur.com/MGKpBSE.gif",   # Guillermo Del Toro pats Mana on the head, and they bow to each other
                    "http://i.imgur.com/lFhgLP8.gif",   # Dolphin nose-boops a cat, who paws at it vaguely
                    "http://i.imgur.com/yEKxpSc.jpg",   # 2 Red Pandas nose-booping
                    "http://goo.gl/7YUnJF",             # pony gift boop?
                    "http://goo.gl/7yMb1y",             # Neil deGrasse Tyson science boop
                    "http://i.imgur.com/8VFggj4.gif",   # What's in the boop box? (it's kittens)
                    "http://i.imgur.com/2dqTNoQ.gif",   # Sheep and Cow charge boop
                    "http://i.imgur.com/h1TAtur.gif",   # Young deer head boop
                    #"http://i.imgur.com/Bv6r4Lu.gif",   # Dancing boxer boop
                    "http://i.imgur.com/zHrQoMT.gif",   # run-by cat boop
                    "http://i.imgur.com/RKzPhan.gif",   # kitteh using every kind of boop for attention
                    "http://i.imgur.com/CqTlFaX.gif",   # snow leopard boops a cat, then flees
                    "http://i.imgur.com/oMDVg1b.gif",   # mantis shrimp boops an octopus
                    "https://imgur.com/r/aww/Ih2NvGP",  # dog boops another dog with its paw "The hoomins do it all the time"
                    "http://i.imgur.com/gFcKWDM.gif",   # fish jump-boops a bear
                    "http://i.imgur.com/kgPiK.jpg",     # pony with a small human riding it boops a horse
                    "http://goo.gl/S8LUk4",             # kitten boops a puppy, puppy tries to return it but falls over
                ]
                return [IRCResponse(ResponseType.Say,
                                    'Boop! {}'.format(random.choice(boops)),
                                    message.ReplyTo)]

            boop = MobroResponse('boop', '', '', seconds=120)
            boop.match = boopMatch
            boop.talkwords = boopTalkwords
            self.responses.add(boop)

            ##################################
            #                                #
            #   OK I'VE GOT THIS NOW, BRO    #
            #                                #
            ##################################
        except Exception, e:
            print e

    def shouldExecute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Type not in self.acceptedTypes:
            return False
        if ignores.ignoreList is not None:
            if message.User.Name.lower() in ignores.ignoreList:
                return False

        return True

    def execute(self, message):
        """
        @type message: IRCMessage
        """
        if message.Command:
            match = re.search('^responses?$', message.Command, re.IGNORECASE)
            if not match:
                return
            if len(message.ParameterList) > 0:
                enableds = []
                for param in message.ParameterList:
                    enableds.append(self.responses.toggle(param, message))
                return enableds
            else:
                enabled = []
                disabled = []
                for name, response in self.responses.dict.iteritems():
                    if response.enabled:
                        enabled.append(name)
                    else:
                        disabled.append(name)
                        
                enabled = sorted(enabled)
                disabled = sorted(disabled)
                
                return [IRCResponse(ResponseType.Say,
                                    'Enabled responses: {}'.format(', '.join(enabled)),
                                    message.ReplyTo),
                        IRCResponse(ResponseType.Say,
                                    'Disabled responses: {}'.format(', '.join(disabled)),
                                    message.ReplyTo)]
                
        else:
            triggers = []
            for response in self.responses.dict:
                trig = self.responses.dict[response].trigger(message)
                if isinstance(trig, str):
                    trig = [trig]
                try:
                    triggers.extend(trig)
                except:
                    triggers = triggers
            return triggers


class MobroResponse(object):
    lastTriggered = datetime.datetime.min

    def __init__(self, name, response, regex, responseType=ResponseType.Say,
                 enabled=True, seconds=300, regexMustAllMatch=True):
        self.name = name
        self.response = response
        self.regex = regex
        self.enabled = enabled
        self.seconds = seconds
        self.mustAllMatch = regexMustAllMatch
        self.responseType = responseType

    #overwrite this with your own match(message) function if a response calls for different logic
    def match(self, message):
        if isinstance(self.regex, str):
            self.regex = [self.regex]
        for regex in self.regex:
            if re.search(regex, message, re.IGNORECASE):
                if not self.mustAllMatch:
                    return True
            elif self.mustAllMatch:
                return False
        return self.mustAllMatch

    def eligible(self, message):
        return (self.enabled and
                (datetime.datetime.utcnow() - self.lastTriggered).seconds >= self.seconds and
                self.match(message))

    def chat(self, saywords, chatMessage):
        """
        @type saywords: str
        @type chatMessage: IRCMessage
        @return: IRCResponse
        """
        return IRCResponse(self.responseType, saywords, chatMessage.ReplyTo)

    def toggle(self, chatMessage):
        """
        @type chatMessage: IRCMessage
        """
        self.enabled = not self.enabled
        return self.chat("Response '%s' %s" % (self.name, {True: "Enabled", False: "Disabled"}[self.enabled]),
                         chatMessage)

    #overwrite this with your own talkwords(IRCMessage) function if a response calls for it
    def talkwords(self, chatMessage):
        """
        @type chatMessage: IRCMessage
        """
        if isinstance(self.response, str):
            self.response = [self.response]
        responses = []
        for response in self.response:
            responses.append(self.chat(response, chatMessage))
        return responses

    def trigger(self, chatMessage):
        """
        @type chatMessage: IRCMessage
        """
        if self.eligible(chatMessage.MessageString):
            self.lastTriggered = datetime.datetime.utcnow()
            return self.talkwords(chatMessage)


class MobroResponseDict(object):
    dict = {}

    def add(self, mbr):
        self.dict[mbr.name] = mbr

    def toggle(self, name, chatMessage=IRCMessage):
        if name.lower() in self.dict:
            return self.dict[name.lower()].toggle(chatMessage)
        return
