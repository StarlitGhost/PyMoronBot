import os

functions = {}

CurrentNick = 'PyMoronBot'

admins = ['Tyranic-Moron', 'T-M|Work', 'Tyranic_Moron', 'T-M|Asleep', 'LordCustardSmingleigh', 'HappyHAL9k', 'XelaReko', 'XelaReco', 'dave_random', 'ElementalAlchemist', 'Homoglyph', 'Heufy|Work', 'Heufneutje', 'Mara']

finger = 'GET YOUR FINGER OUT OF THERE'
version = '0.0.3' # arbitrarily decided!
source = 'https://github.com/MatthewCox/PyMoronBot/'

CommandChar = '\\'

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
logPath = os.path.join(dname, 'logs')

