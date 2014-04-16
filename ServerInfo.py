class ServerInfo:

    # I have used the defaults specified by RFC1459 here
    SupportedUserModes = ['i', 'o', 's', 'w']
    SupportedChannelListModes = ['b']
    SupportedChannelSetArgsModes = ['l']
    SupportedChannelSetUnsetArgsModes = ['k']
    SupportedChannelNormalModes = ['i','m','n','p','s','t']

    SupportedStatuses = {'o': '@', 'v': '+'}
    SupportedStatusesReverse = {'@': 'o', '+': 'v'}
