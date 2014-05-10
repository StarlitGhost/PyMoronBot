import json

ignoreList = None

path = 'Data/ignore_list.json'


def loadList():
    global ignoreList
    try:
        with open(path, 'r') as f:
            j = json.load(f)

        ignoreList = j

        ignoreList = [i.lower() for i in ignoreList]

    except IOError:
        j = []
        with open(path, 'w') as f:
            json.dump(j, f)

        ignoreList = []


def saveList():
    with open(path, 'w') as f:
        json.dump(ignoreList, f)
