class ServerInfo:

    # I have used the defaults specified by RFC1459 here
    SupportedUserModes = 'iosw'
    SupportedChannelListModes = 'b'
    SupportedChannelSetArgsModes = 'l'
    SupportedChannelSetUnsetArgsModes = 'k'
    SupportedChannelNormalModes = 'imnpst'

    SupportedStatuses = {'o': '@', 'v': '+'}
    SupportedStatusesReverse = {'@': 'o', '+': 'v'}
