import json

def load_key(keyName):
    try:
        j = {}
        with open('Data/api_keys.json', 'r') as f:
            j = json.load(f)

        if keyName in j:
            return j[keyName]
        else:
            j[keyName] = None
            with open('Data/api_keys.json', 'w') as f:
                json.dump(j, f)

    except IOError as e:
        j = {keyName: None}
        with open('Data/api_keys.json', 'w') as f:
            json.dump(j, f)

    return None
