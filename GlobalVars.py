# -*- coding: utf-8 -*-
import os

admins = ['Tyranic-Moron', 'T-M|Work', 'Tyranic_Moron', 'T-M|Asleep', 'GarrusVakarian', 'LordCustardSmingleigh', 'XelaReko', 'XelaReco', 'Xel|Work', 'dave_random', 'ElementalAlchemist', 'Homoglyph', 'Heufy|Work', 'Heufneutje', 'HeufyDroid', 'HeufyCloud', 'HeufyTrain', 'HeufyBus', 'HubbeKing', 'HubbeWork', 'HubbeTrain', 'Mara', 'ekimekim']

finger = 'GET YOUR FINGER OUT OF THERE'
version = '0.7.0'  # 3 major features left to implement before I'll consider it 1.0.0 (listed below)
# Unified command data storage (may decide not to bother, independent also works and has its own benefits)
# Command Aliasing
# Command Chaining
source = 'https://github.com/MatthewCox/PyMoronBot/'

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
logPath = os.path.join(dname, 'logs')
