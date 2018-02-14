# -*- coding: utf-8 -*-
import json

path = 'data/api_keys.json'


def load_key(keyName):
    try:
        with open(path, 'r') as f:
            j = json.load(f)

        if keyName in j:
            return j[keyName]
        else:
            j[keyName] = None
            with open(path, 'w') as f:
                json.dump(j, f)

    except IOError:
        j = {keyName: None}
        with open(path, 'w') as f:
            json.dump(j, f)

    return None
