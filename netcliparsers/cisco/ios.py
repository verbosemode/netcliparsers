#!/usr/bin/env python

# Only for development
from pyparsing import *
#from pyparsing import Suppress, Keyword, Word, alphanums, nums, oneOf, OneOrMore, Group, StringEnd

def show_class_map():
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


def show_cdp_neighbor_detail():
    hostname = Word(alphanums, bodyChars=alphanums + '_-.')
    deviceid = Suppress(Keyword('Device ID:')) + hostname('deviceid')

    ipaddrs = Suppress(Keyword('IP address:')) + Combine(Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '.' + Word(nums))
    # FIXME last match overwrites first address
    entryaddrs = Suppress(Keyword('Entry address(es):')) + OneOrMore(ipaddrs('ipaddress'))

    platform = Word(alphanums, bodyChars=alphanums + '- ') 
    # FIXME Strip whitespace off string end
    capabilities = Word(alphanums, bodyChars=alphanums + '- ') 
    platformcapabilities = Suppress(Keyword('Platform:')) + platform('platform') + Suppress(',') +\
                           Keyword('Capabilities:') + capabilities('capabilities')

    interface = Word(alphas, bodyChars=alphanums + '/.')
    interfaces = Suppress(Keyword('Interface:')) + interface('localinterface') + Suppress(',') +\
                 Suppress(Keyword('Port ID (outgoing port):')) + interface('remoteinterface')

    holdtimenum = Word(nums).setParseAction(lambda tokens: int(tokens[0]))
    holdtime = Suppress('Holdtime') + Suppress(':') + holdtimenum('holdtime') + Suppress('sec')

    cdpentry = deviceid + entryaddrs + platformcapabilities + interfaces + holdtime

    parser = OneOrMore(cdpentry)

    return parser
