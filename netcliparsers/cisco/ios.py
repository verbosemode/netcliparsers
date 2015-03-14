#!/usr/bin/env python
#
# netcliparsers is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# netcliparsers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with netcliparsers.  If not, see <http://www.gnu.org/licenses/>.
#
# If you need to contact the author, you can do so by emailing:
# jochenbartl [~at~] mailbox [/dot\] org

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


def show_ip_interface():
    interface = Word(alphas, bodyChars=alphanums + '/.')
    interfacestatus = oneOf(['up', 'down'])
    linestatus = oneOf(['up', 'down'])
    ipaddress = Combine(Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '.' + Word(nums))
    ipprefix = Combine(Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '/' + Word(nums))
    mtu = Word(nums).setParseAction(lambda tokens: int(tokens[0]))

    # TODO make sure 'helperaddress' is a list and contains zero or more items. Parser user shouldn't need to
    # check if key exists in data structure
    # FIXME Fails with multiple helper addresses
    helperaddress = Suppress('Helper address' | 'Helper addresses') +\
                    ('is not set' | ('is' + ipaddress('helperaddress')) | ('are' + OneOrMore(ipaddress)))

    directedbroacastsstate = oneOf(['enabled', 'disabled'])
    directedbroadcastsacl = ' - but restricted by access list 110'
    directedbroadcasts = Suppress('Directed broadcast forwarding is') + directedbroacastsstate('directedbroadcasts')

    parser = interface('interface') + Suppress('is') + interfacestatus('interfacestatus') + Suppress(',') +\
             Suppress('line protocol is') + linestatus('linestatus') +\
             Suppress('Internet address is') + ipprefix('ipaddress') +\
             Suppress('Broadcast address is') + ipaddress('broadcastaddress')+\
             Suppress('Address determined by setup command')+\
             Suppress('MTU is') + mtu('mtu') + Suppress('bytes') +\
             helperaddress

