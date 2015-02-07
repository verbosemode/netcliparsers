#!/usr/bin/env python

from functools import partial
# Only for development
#from pyparsing import *
from pyparsing import alphas, alphanums, nums
from pyparsing import Suppress, Keyword, Word, oneOf, ZeroOrMore, OneOrMore, Group, Combine, StringEnd, SkipTo, Optional


def show_class_map():
    """
    """
    classmapstart = Suppress(Keyword('Class Map'))

    matchtype = oneOf(['match-all', 'match-any'])

    classmapname = Word(alphanums, bodyChars=alphanums + '-')

    classmapid = Suppress('(id' + Word(nums) + ')')

    # match dscp ...
    dscpnum = Word(nums).setParseAction(lambda tokens: int(tokens[0]))
    dscpphb = Keyword('ef') | Word('afcs' + nums) | Keyword('default')
    matchdscp = Suppress(Keyword('Match')) + Suppress(Keyword('dscp')) + dscpphb('phb') + Suppress('(') +  dscpnum('dscpnum') + Suppress(')')

    # match access-group
    matchacl = Suppress(Keyword('Match')) + Keyword('access-group') + Word(nums)

    # match any
    matchany = Suppress(Keyword('Match')) + Keyword('any')

    # parse individual match lines within a class-map
    classmapmatch = OneOrMore(Group(matchany)('matchany*') | Group(matchdscp)('matchdscp*') | Group(matchacl)('matchacl*'))

    # Parse "show class-map"
    classmap = Group(classmapstart + matchtype('matchtype') + classmapname('name') + classmapid + classmapmatch('matches'))

    parser = OneOrMore(classmap) + StringEnd()

    return parser


parse_show_class_map = partial(lambda x: show_class_map().parseString(x))


def show_cdp_neighbor_detail():
    """
    Example
    -------

    for e in parser.parseString(text):
        print("{deviceid} {localinterface} {remoteinterface}".format(**e)):

    ap1.example.com FastEthernet0/25 GigabitEthernet0.1
    ap2.example.com FastEthernet0/37 GigabitEthernet0.1
    sw1.example.com GigabitEthernet0/1 GigabitEthernet2/4
    sw2.example.com GigabitEthernet0/2 GigabitEthernet0/26
    """

    entrystart = Suppress(Word('-'))
    hostname = Word(alphanums, bodyChars=alphanums + '_-.')
    deviceid = Suppress(Keyword('Device ID:')) + hostname('deviceid')

    ipaddrs = Suppress(Keyword('IP address:')) + Combine(Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '.' + Word(nums))
    # FIXME last match overwrites first address
    entryaddrs = Suppress(Keyword('Entry address(es):')) + OneOrMore(ipaddrs('ipaddress'))

    platform = Word(alphanums, bodyChars=alphanums + '- ') 
    capabilities = Word(alphanums, bodyChars=alphanums + '- ') 
    platformcapabilities = Suppress(Keyword('Platform:')) + platform('platform') + Suppress(',') +\
            Keyword('Capabilities:') + capabilities('capabilities').setParseAction(lambda tokens: tokens[0].strip())

    interface = Word(alphas, bodyChars=alphanums + '/.')
    interfaces = Suppress(Keyword('Interface:')) + interface('localinterface') + Suppress(',') +\
                 Suppress(Keyword('Port ID (outgoing port):')) + interface('remoteinterface')

    holdtimenum = Word(nums).setParseAction(lambda tokens: int(tokens[0]))
    holdtime = Suppress('Holdtime') + Suppress(':') + holdtimenum('holdtime') + Suppress('sec')

    versionstr = Word(alphanums + ' .,-_()')
    version = Suppress('Version') + Suppress(':') + versionstr('version')

    techsupport = Suppress('Technical Support:')

    managementaddresses = Suppress('Management address(es):') + ZeroOrMore(ipaddrs)

    unidirectionalmodestatus = Word(alphas)
    unidirectionalmode = Suppress(Keyword('Unidirectional Mode:')) + unidirectionalmodestatus('unidirectionalmode')

    cdpentry = entrystart + deviceid + entryaddrs + platformcapabilities + interfaces + holdtime + version + techsupport +\
               SkipTo('Management address(es):') + managementaddresses + Optional(unidirectionalmode)

    parser = OneOrMore(Group(cdpentry)) + StringEnd()

    return parser


parse_show_cdp_neighbor_detail = partial(lambda x: show_cdp_neighbor_detail().parseString(x))
