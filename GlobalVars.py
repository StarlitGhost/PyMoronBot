import os

functions = {}
functionCaseMapping = {}

CurrentNick = 'PyMoronBot'

admins = ['Tyranic-Moron', 'T-M|Work', 'Tyranic_Moron', 'T-M|Asleep', 'LordCustardSmingleigh', 'HappyHAL9k', 'XelaReko', 'XelaReco', 'dave_random', 'ElementalAlchemist', 'Homoglyph', 'Heufy|Work', 'Heufneutje', 'Mara']

finger = 'GET YOUR FINGER OUT OF THERE'
version = '0.6.0' # 4 major features left to implement before I'll consider it 1.0.0 (listed below)
# Channel & User knowledge
# Unified function data storage (may decide not to bother, independent also works and has its own benefits)
# Function Aliasing
# Function Chaining
source = 'https://github.com/MatthewCox/PyMoronBot/'

CommandChar = '\\'

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
logPath = os.path.join(dname, 'logs')

