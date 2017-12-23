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
                                             '([^a-zA-Z]|^)dutch([^a-zA-Z]|$)',
                                             ResponseType.Say,
                                             False))

            '''Sensitive to bees'''
            self.responses.add(MobroResponse('bees',
                                             'BEES?! AAAARRGGHGHFLFGFGFLHL',
                                             '([^a-zA-Z]|^)bee+s?([^a-zA-Z]|$)'))

            '''Responds to cheese'''
            self.responses.add(MobroResponse('cheese',
                                             'loves cheese',
                                             '([^a-zA-Z]|^)cheese([^a-zA-Z]|$)',
                                             ResponseType.Do))
                                             
            '''Also respond to French cheese'''
            self.responses.add(MobroResponse('fromage',
                                             'adore le fromage',
                                             '([^a-zA-Z]|^)fromage([^a-zA-Z]|$)',
                                             ResponseType.Do))
            
            '''And Dutch cheese because it'll be funny if it ever comes up'''                                 
            self.responses.add(MobroResponse('kaas',
                                             'is gek op kaas',
                                             '([^a-zA-Z]|^)kaas([^a-zA-Z]|$)',
                                             ResponseType.Do))
                                             
            '''Respond to Finnish cheese because lel'''
            self.responses.add(MobroResponse('juusto',
                                             'rakastaa juustoa',
                                             '([^a-zA-Z]|^)juusto([^a-zA-Z]|$)',
                                             ResponseType.Do))

            '''And why not German too?''' # because it breaks everything apparently
#            self.responses.add(MobroResponse(u'Käse',
#                                             u'liebt Käse',
#                                             ur'([^a-zA-Z]|^)Käse([^a-zA-Z]|$)',
#                                             ResponseType.Do))

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

            """Responds to traditional assertions."""
            self.responses.add(MobroResponse('tradition',
                                             'As is tradition.',
                                             '([^a-zA-Z]|^)as is tradition([^a-zA-Z]|$)'))

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
                    r'(woo+f|r+u+ff+|arf|ba+r+k)': 'puppeh',
                    r'squeak': 'mouse',
                    r'moo+': 'cow',
                    r'(twee+t|ca+w+)': 'bird',
                    r'ne+i+gh': 'horse',
                    r'ri+bb+i+t': 'frog',
                    r'bloo+p': 'fish',
                    r'o+i+n+k+': 'piggy',
                    r'ho+n+k+': 'goose',
                    r'hi+ss+': 'snake',
                    r'r+o+a+r+': 'lion',
                    r'(ho+w+l+|a+w?oo+)': 'wolf',
                    r'blee+p\s+bloo+p': 'droid',
                    r'y?arr+': 'pirate',
                    r'qua+ck': 'duck',
                    r'(hoo+t|whoo+)': 'owl',
                    r'br+a+i+n+s+': 'zombie',
                    r'(ba+w+k|clu+ck)': 'chicken',
                    r'baa+': 'sheep',
                    r'(blub(\s+)?)+': 'deep one',
                    r'bu*zz+': 'bee',
                    r'boo+': 'ghost',
                    r'(noo+t ?)+': 'penguin',
                }

                self.animal = None
                for match, animal in matchDict.iteritems():
                    if re.search(r'^{}([^\s\w]+)?$'.format(match), message, re.IGNORECASE):
                        self.animal = animal
                        return True

                return False

            def animalTalkwords(message):
                # Specific user animals
                if self.animal == 'cow' and message.User.Name.lower() == 'neo-gabi':
                    return [IRCResponse(ResponseType.Do,
                                        'points at {0}, and says "{0} was the cow all along!"'
                                        .format(message.User.Name),
                                        message.ReplyTo)]

                randomChance = random.randint(1, 20)

                # Emily Bonus
                if message.User.Name == 'Emily':
                    randomChance = random.randint(1, 25)
                    
                article = 'an' if self.animal[0] in 'aeiou' else 'a'

                # General user animals
                if randomChance == 1:
                    ''' User Critically Failed '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is DEFINITELY NOT the droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    elif self.animal == 'goose':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is a clown!'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} critically fails at being {} {}.'.format(message.User.Name, article, self.animal),
                                            message.ReplyTo)]

                elif randomChance <= 8:
                    ''' User Is Not A [animal] '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is not the droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} is not {} {}.'.format(message.User.Name, article, self.animal),
                                            message.ReplyTo)]
                elif randomChance <= 14:
                    '''User Might Be A [animal] '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} might be the droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} /might/ be {} {}.'.format(message.User.Name, article, self.animal),
                                            message.ReplyTo)]
                elif randomChance <= 19:
                    ''' User Is A [animal] '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is the droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    elif self.animal == 'puppeh':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is such doge. wow.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} is DEFINITELY {} {}.'.format(message.User.Name, article, self.animal),
                                            message.ReplyTo)]
                elif randomChance == 20:
                    ''' User Is A Critical [animal] '''
                    if self.animal == 'droid':
                        return [IRCResponse(ResponseType.Say,
                                            '{} is DEFINITELY the droid you are looking for.'.format(message.User.Name),
                                            message.ReplyTo)]
                    else:
                        return [IRCResponse(ResponseType.Say,
                                            '{} is a CRITICAL {}!'.format(message.User.Name, self.animal),
                                            message.ReplyTo)]
                else:
                    ''' Roll is outside of bounds, Magic! '''
                    return [IRCResponse(ResponseType.Say,
                                        'You are clearly a magician rolling out of bounds like that!',
                                        message.ReplyTo)]

            animalResponse = MobroResponse('animal', '', '', seconds=0)
            animalResponse.match = animalMatch
            animalResponse.talkwords = animalTalkwords
            self.responses.add(animalResponse)

            '''Responds to boops'''
            def boopMatch(message):
                match = re.search('(^|[^\w])b[o0]{2,}ps?([^\w]|$)', message, re.IGNORECASE)
                return match

            def boopTalkwords(message):
                boops = [
                    #"http://goo.gl/HJzfS",              # feline anatomy
                    "http://bit.ly/zA2bUY",             # i boop ur noes
                    "http://i.imgur.com/B2vDpq0.png",   # hey cat, imma boop ur head, lol
                    "http://bit.ly/ACbm0J",             # Iz gunna boop yer nose, k?
                    "http://bit.ly/qNyEZk",             # what do you think mr t is daydreaming about?
                    "http://bit.ly/zJrjGF",             # jeans kitty boop
                    "http://goo.gl/d054n",              # This is called "aversion therapy."
                    "http://goo.gl/6IoB0",              # my grumpy button, ur pushin' it
                    "http://imgur.com/O61oxTc.jpg",     # colonel goggie in the hallway with the nose boop
                    "http://bit.ly/yODbYA",             # You may go, but first I must boop your nose
                    #"http://bit.ly/AdX2cw",             # boop, gotchur nose
                    "http://goo.gl/1Xu0LK",             # fluttershy & rainbow dash
                    "http://i.imgur.com/vC5gy.jpg",     # dog in car boop
                    "http://i.imgur.com/xmzLY.gifv",    # cat lap booping dog
                    "http://i.imgur.com/NSAKo.jpg",     # orange cat perma-booping dog on bed
                    "http://i.imgur.com/jpcKLuy.png",   # pinkie pie and twilight sparkle boop
                    "http://i.imgur.com/qeNvd.png",     # elephant boop
                    "http://i.imgur.com/wtK1T.jpg",     # jet booping tanker truck
                    "http://goo.gl/JHBKUb",             # real men head boop with kittens
                    "http://i.imgur.com/hlCm7aA.png",   # sweetie belle booping apple bloom
                    "http://i.imgur.com/BLQoL61.gifv",  # darting boop
                    "http://i.imgur.com/3b2lSjd.gifv",  # pounce boops
                    "http://i.imgur.com/P83UL.gifv",    # reciprocated cat boop
                    "http://i.imgur.com/H7iNX8R.jpg",   # white cat nose boop
                    "http://i.imgur.com/NoYdYtU.jpg",   # Lil Retriever Learns How To Boop
                    "http://i.imgur.com/jWMdZ.jpg",     # black & white kitten boop
                    "http://i.imgur.com/dz81Dbs.jpg",   # puppy picnic boop
                    "http://i.imgur.com/0KWKb.gifv",    # spinspinspin BOOP!
                    #"http://i.minus.com/izXxGnlNFmVrN.gif",  # horse & excitable puppy boop - minus.com is dead for good?
                    "http://i.imgur.com/UaNm6fv.gif",   # boop to turn off kitten
                    "http://i.imgur.com/QmVjLNQ.png",   # snow leopard boop
                    "http://i.imgur.com/HaAovQK.gifv",  # darting bed boop
                    "http://i.imgur.com/Le4lOKX.gifv",  # kitten gonna get him boop
                    #"http://i.imgur.com/so5M2Mk.gifv",  # shibe back boop
                    "http://i.imgur.com/P7Ca5Si.gifv",  # shibe pikachu boop
                    "http://i.imgur.com/yvlmyNI.gifv",  # quick run up boop walk away (NewClassic)
                    "http://goo.gl/9FTseh",             # Fluttershy & Pinkie Pie boop
                    "http://i.imgur.com/yexMjOl.gifv",  # Archer boop
                    "http://goo.gl/l3lwH9",             # Cat boops a butt
                    "http://i.imgur.com/zOZvmTW.gifv",  # Bunny bumper cars
                    "http://i.imgur.com/P0a8dU2.gifv",  # Kitten beach boop loop
                    "http://i.imgur.com/LXFYmPU.gifv",  # Nose-booped cat retreats under blanket
                    "http://i.imgur.com/6ZJLftO.gifv",  # Cat booping a bunny's nose repeatedly
                    "http://i.imgur.com/MGKpBSE.gifv",  # Guillermo Del Toro pats Mana on the head, and they bow to each other
                    "http://i.imgur.com/lFhgLP8.gifv",  # Dolphin nose-boops a cat, who paws at it vaguely
                    "http://i.imgur.com/yEKxpSc.jpg",   # 2 Red Pandas nose-booping
                    "http://goo.gl/7YUnJF",             # pony gift boop?
                    "http://goo.gl/7yMb1y",             # Neil deGrasse Tyson science boop
                    "http://i.imgur.com/8VFggj4.gifv",  # What's in the boop box? (it's kittens)
                    "http://i.imgur.com/2dqTNoQ.gifv",  # Sheep and Cow charge boop
                    "http://i.imgur.com/h1TAtur.gifv",  # Young deer head boop
                    #"http://i.imgur.com/Bv6r4Lu.gif",   # Dancing boxer boop
                    "http://i.imgur.com/zHrQoMT.gifv",  # run-by cat boop
                    "http://i.imgur.com/RKzPhan.gifv",  # kitteh using every kind of boop for attention
                    "http://i.imgur.com/CqTlFaX.gifv",  # snow leopard boops a cat, then flees
                    "http://i.imgur.com/oMDVg1b.gifv",  # mantis shrimp boops an octopus
                    "https://imgur.com/r/aww/Ih2NvGP",  # dog boops another dog with its paw "The hoomins do it all the time"
                    "http://i.imgur.com/gFcKWDM.gifv",  # fish jump-boops a bear
                    "http://i.imgur.com/kgPiK.jpg",     # pony with a small human riding it boops a horse
                    "http://goo.gl/S8LUk4",             # kitten boops a puppy, puppy tries to return it but falls over
                    "http://i.imgur.com/SkBaRNR.gifv",  # horse and cat boop and then facerub on the wall of a stable
                    "http://i.imgur.com/kc4SQIz.gifv",  # dog boops itself, paws ensue
                    "http://i.imgur.com/ddiNHHz.jpg",   # cartoon wolf boop, pass it on!
                    "http://i.imgur.com/6QPFAkO.gifv",  # monkey flings itself between trees, messing with a bunch of tiger cubs
                    "http://i.imgur.com/mncYpu5.gifv",  # hockey goalkeeper ass-boops another hockey player into a wall
                    "http://i.imgur.com/NZRxzNe.gifv",  # sneaky cupboard cat boops another cat
                    "http://i.imgur.com/1jMYf8U.gifv",  # a couple of guinea pigs boop a cat
                    "http://i.imgur.com/k6YicPf.gifv",  # dog gets booped on nose with a toy, then cat runs up and boops its back. dog is very confuse
                    "https://i.imgur.com/m67qRsQ.gifv", # lamb repeatedly boops its face into a dog's paw, dog doesn't care
                    "http://i.imgur.com/32H1kkw.gifv",  # HD BBC nature show boop
                    "http://i.imgur.com/pcksMNP.gifv",  # Kitten sitting on its back legs boops a doge (Corgi?) with its front legs
                    "https://i.imgur.com/8TKVJ63.gifv", # Goat stands on its back legs to boop with a horse
                    "http://i.imgur.com/1AgMAbK.gifv",  # cat runs out of a dark room, eyes glowing, and leaps into the camera
                    "http://i.imgur.com/i7J5VHI.gifv",  # kitten on a sofa jumps around and boops a dog peering up at it on the nose
                    "http://i.imgur.com/XTuRoOs.gifv",  # bunny boop triforce
                    "http://i.imgur.com/FkVNWlc.gifv",  # cat reaches up to grab and boop the camera with its nose
                    "http://i.imgur.com/lVxFUGF.gifv",  # secret bag cat boops other cat on bed
                    "http://i.imgur.com/bLIBH6J.gifv",  # orange kitten eyes up another kitten, then pounces. En Garde!
                    "http://i.imgur.com/V35yPa0.gifv",  # 2 dogs boop their snoots in an expert manner
                    "http://i.imgur.com/ihS28BF.gifv",  # dog boops a cat standing on the edge of a bath into it
                    "https://i.imgur.com/GBniOtO.gifv", # touch lamp cat gets booped on the nose
                    "http://i.imgur.com/GufY1ag.gif",   # puppy boops the camera
                    "http://www.gfycat.com/FarflungTeemingAtlasmoth",   # one cat boops another sitting in a bag, while another in a basket looks on
                    "https://i.imgur.com/NHCSPxj.jpg",  # 2 bunnies boop noses on a towel
                    "https://i.imgur.com/8tZ9wBy.gifv", # a red koala walks up to another and boops it on the nose
                    "http://imgur.com/dkLJLrt.mp4",     # corgi is wiggle nose booped, then turns to camera with tongue out
                    "https://i.imgur.com/JOwvswE.gifv", # finger pokes frog in the head until frog has had enough of that shit
                    "http://i.imgur.com/li9KPAD.gifv",  # corgi butt finger boops
                    "http://i.imgur.com/IciHp73.gifv",  # cat lying on its back gets a nose-boop, wiggles paws (image title: Excessive reaction to a booping)
                    "https://i.imgur.com/tMIW18y.jpg",  # dog on a swing boops another dog's nose, like Michelangelo's Creation of Adam (image title: the creashun of pupper)
                    "https://media.giphy.com/media/y1yTg5UheAqXK/giphy.gif", # iz safe? iz nottt! (cat pokes head out of sofa cushions, is booped and retreats)
                    "https://i.imgur.com/QkozEpp.gifv", # corgi lying on someone's lap in a car is booped (title: In case you had a bad day :))
                    "http://i.imgur.com/hP7RMSo.gifv",  # snek is booped, was not prepared (hello, *boop*, oh heck, i was not prepare)
                    "https://i.imgur.com/zZle0Sw.gifv", # horse in paddock is booped, sticks out tongue
                    "https://i.imgur.com/PxzCKCO.gifv", # toy robot approaches dog, dog boops it over
                    "http://hats.retrosnub.uk/DesertBus10/db10_penelope_boop_ian.gif", # Penelope boops Ian on the nose at DBX
                    "http://i.imgur.com/ECkZI3F.gifv",  # cat and puppy boop each other's noses with their paws
                    "https://i.imgur.com/FmMNIPy.mp4",  # dog boops the shadow of a pen being waggled
                    "http://i.imgur.com/Iipr2lg.png",   # red panda getting booped on the forehead
                    "http://i.imgur.com/WmRnfbX.png",   # can you smash my sadness? / *boop* / :)
                    "https://i.imgur.com/1R2dOmJ.gifv", # labrador aggressively boops other dog to steal their treat
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
        except Exception as e:
            print(e)

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
            if re.search(regex, message, re.IGNORECASE | re.UNICODE):
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
        return self.chat("Response {!r} {}".format(self.name, 'enabled' if self.enabled else 'disabled'), chatMessage)

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
