def is_number(s):
    """returns True if string s can be cast to a number, False otherwise"""
    try:
        float(s)
        return True
    except ValueError:
        return False

# http://stackoverflow.com/a/6043797/331047
def split_utf8(s, n):
    """Split UTF-8 s into chunks of maximum byte length n"""
    while len(s) > n:
        k = n
        while (ord(s[k]) & 0xc0) == 0x80:
            k -= 1
        yield s[:k]
        s = s[k:]
    yield s
