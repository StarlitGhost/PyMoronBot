from IRCMessage import IRCMessage
from IRCResponse import IRCResponse, ResponseType
from Function import Function
from GlobalVars import *
from MobroResponses import *

from Data import ignores

import re, random

class Instantiate(Function):
    Help = 'Talkwords from the mouth place - response <name> to enable/disable a particular response (might need to check the source for names)'
    
    def __init__(self):
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
            self.responses.add(MobroResponse(   'squishy',
                                'GODDAMMIT, GET YOUR HAND OUT OF THERE',
                                ["([^a-zA-Z]|^)wet (and|&|'?n'?) squishy([^a-zA-Z]|$)","([^a-zA-Z]|^)squishy (and|&|'?n'?) wet([^a-zA-Z]|$)"],
                                ResponseType.Say,
                                True,
                                300,
                                False))
            
            '''Responds to the ocean as a caffeinated Pika'''
            self.responses.add(MobroResponse(   'ocean',
                                'mimes out a *WHOOOOSH!*',
                                '([^a-zA-Z]|^)ocean([^a-zA-Z]|$)',
                                ResponseType.Do))
            
            '''Responds to incorrect windmill assumptions'''
            self.responses.add(MobroResponse(   'windmill',
                                ['WINDMILLS DO NOT WORK THAT WAY!','GOODNIGHT!'],
                                ['([^a-zA-Z]|^)windmills?([^a-zA-Z]|$)','([^a-zA-Z]|^)cool([^a-zA-Z]|$)']))
            
            '''Responds to Pokemon as Joseph Ducreux'''
            self.responses.add(MobroResponse(   'pokemon',
                                'Portable Atrocities! Must be encapsulated en masse!',
                                '([^a-zA-Z]|^)pokemon([^a-zA-Z]|$)'))
            
            '''Guards against the Dutch'''
            self.responses.add(MobroResponse(   'dutch',
                                'The Dutch, AGAIN!',
                                '([^a-zA-Z]|^)dutch([^a-zA-Z]|$)'))
            
            '''Sensitive to bees'''
            self.responses.add(MobroResponse(   'bees',
                                'BEES?! AAAARRGGHGHFLFGFGFLHL',
                                '([^a-zA-Z]|^)bee+s?([^a-zA-Z]|$)'))
            
            '''Responds to cheese'''
            self.responses.add(MobroResponse(   'cheese',
                                'loves cheese',
                                '([^a-zA-Z]|^)cheese([^a-zA-Z]|$)',
                                ResponseType.Do))
            
            '''Responds to JavaScript's insane shenanigans'''
            self.responses.add(MobroResponse(   'wat',
                                'NaNNaNNaNNaN https://www.destroyallsoftware.com/talks/wat man!',
                                '([^a-zA-Z]|^)wat([^a-zA-Z]|$)',
                                ResponseType.Say,
                                False))
            
            #Sorry man, I had to. I HAD to.
            '''Responds to Ponies'''
            self.responses.add(MobroResponse(   'ponies',
                                'Ponies Ponies Ponies SWAG! https://www.youtube.com/watch?v=hx30VHwKa0Q',
                                '([^a-zA-Z]|^)ponies([^a-zA-Z]|$)',
                                ResponseType.Say,
                                False))
            
            
            #This one needs to mess with the object to work right.
            '''Responds to DuctTape being a dick in minecraft'''
            def ducktapeMatch(message):
                match = re.search('([^a-zA-Z]|^)minecraft([^a-zA-Z]|$)', message, re.IGNORECASE)
                self.ductMatch = re.search('([^a-zA-Z]|^)(?P<duc>duc[kt]tape)([^a-zA-Z]|$)',message,re.IGNORECASE)
                return match and self.ductMatch
            
            def ducktapeTalkwords(chatMessage):
                return [IRCResponse(ResponseType.Say,'Just saying, %s is a dick in Minecraft' % self.ductMatch.group('duc'),chatMessage.ReplyTo)]
            
            ducktape = MobroResponse('ducktape','','')
            ducktape.match = ducktapeMatch
            ducktape.talkwords = ducktapeTalkwords
            self.responses.add(ducktape)
            
            '''Responds to boops'''
            def boopMatch(message):
                match = re.search('([^a-zA-Z]|^)b[o0][o0]+ps?([^a-zA-Z]|$)', message, re.IGNORECASE)
                return match
            
            def boopTalkwords(message):
                boops = [
                        "http://goo.gl/HJzfS",              # feline anatomy
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
                        "http://bit.ly/x9WGoy",             # fluttershy & rainbow dash
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
                        "http://i.minus.com/izXxGnlNFmVrN.gif", # horse & excitable puppy boop
                        "http://i.imgur.com/UaNm6fv.gif",   # boop to turn off kitten
                        "http://i.imgur.com/QmVjLNQ.png",   # snow leopard boop
                        "http://i.imgur.com/HaAovQK.gif",   # darting bed boop
                        "http://i.imgur.com/Le4lOKX.gif",   # kitten gonna get him boop
                        "http://i.imgur.com/so5M2Mk.gif",   # shibe back boop
                        "http://i.imgur.com/P7Ca5Si.gif",   # shibe pikachu boop
                        "http://i.imgur.com/yvlmyNI.gif",   # quick run up boop walk away (NewClassic)
                        "http://goo.gl/9FTseh",             # Fluttershy & Pinkie Pie boop
                        "http://i.imgur.com/yexMjOl.gif",   # Archer boop
                        ]
                return [IRCResponse(ResponseType.Say,
                           'Boop! %s' % random.choice(boops),
                           message.ReplyTo)]
            
            boop = MobroResponse('boop', '', '', ResponseType.Say, True, 120, True)
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
    
    
    
    def GetResponse(self, message):
        if message.Type != 'PRIVMSG':
            return
        
        if ignores.ignoreList is not None:
            if message.User.Name in ignores.ignoreList:
                return
        
        if message.Command:
            match = re.search('^responses?$', message.Command, re.IGNORECASE)
            if not match:
                return
            enableds = []
            for param in message.ParameterList:
                enableds.append(self.responses.toggle(param,message))
            return enableds
        else:
            triggers = []
            for response in self.responses.dict:
                trig = self.responses.dict[response].trigger(message)
                if isinstance(trig,str):
                    trig = [trig]
                try:
                    triggers.extend(trig)
                except:
                    triggers = triggers
            return triggers
