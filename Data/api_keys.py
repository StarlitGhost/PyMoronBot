import json

path = 'Data/api_keys.json'

def load_key(keyName):
    try:
        j = {}
        with open(path, 'r') as f:
            j = json.load(f)

        if keyName in j:
            return j[keyName]
        else:
            j[keyName] = None
            with open(path, 'w') as f:
                json.dump(j, f)

    except IOError as e:
        j = {keyName: None}
        with open(path, 'w') as f:
            json.dump(j, f)

    return None
