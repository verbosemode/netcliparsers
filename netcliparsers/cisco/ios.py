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
    # TODO move this to a seperate parser building blocks file
    # TODO combine them to IOS interface states??
    state_enabled_disabled = oneOf(['enabled', 'disabled'])
    state_always_never = oneOf(['always', 'never'])

    interface = Word(alphas, bodyChars=alphanums + '/.')
    interface_status = oneOf(['up', 'down', 'deleted'])
    line_status = oneOf(['up', 'down'])
    # TODO move this to a seperate parser building blocks file
    ipaddress = Combine(Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '.' + Word(nums))
    # TODO move this to a seperate parser building blocks file
    ipprefix = Combine(Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '/' + Word(nums))
    mtu = Word(nums).setParseAction(lambda tokens: int(tokens[0]))

    # TODO make sure 'helperaddress' is a list and contains zero or more items. Parser user shouldn't need to
    # check if key exists in data structure
    # FIXME Fails with multiple helper addresses
    # helperaddress = Suppress('Helper address') | Suppress('Helper addresses') +\
    #                 'is not set' | ('is' + ipaddress('helperaddress'))
    # helper_address = Suppress('Helper address') | Suppress('Helper addresses') +\
    #                 ('is not set' | ('is' + ipaddress('helperaddress')) | ('are' + OneOrMore(ipaddress)))
    helper_address = Suppress('Helper address is not set')

    # FIXME
    directed_broadcasts_acl = ' - but restricted by access list 111'
    directed_broadcasts = Suppress('Directed broadcast forwarding is') + state_enabled_disabled('directed_broadcasts')

    # TODO
    outgoing_acl = Suppress('Outgoing access list is not set')
    # TODO
    inbound_acl = Suppress('Inbound  access list is not set')

    proxyarp = Suppress('Proxy ARP is') + state_enabled_disabled('proxyarp')

    local_proxyarp = Suppress('Local Proxy ARP is') + state_enabled_disabled('local_proxyarp')

    # TODO
    securitylevel = Suppress('Security level is default')
    splithorizon = Suppress('Split horizon is') + state_enabled_disabled('splithorizon')

    icmp_redirects = Suppress('ICMP redirects are') + state_always_never('icmp_redirects') + Suppress('sent')
    icmp_unreachables = Suppress('ICMP unreachables are') + state_always_never('icmp_unreachables') + Suppress('sent')
    icmp_mask_replies = Suppress('ICMP mask replies are') + state_always_never('icmp_maskreplies') + Suppress('sent')

    ipfastswitching = Suppress('IP fast switching is') + state_enabled_disabled('ipfastswitching')
    ipfastswitching_sameinterface = Suppress('IP fast switching on the same interface is') + state_enabled_disabled('ipfastswitching_sameinterface')
    ipflowswitching = Suppress('IP Flow switching is') + state_enabled_disabled('ipflowswitching')
    ipcefswitching = Suppress('IP CEF switching is') + state_enabled_disabled('ipcefswitching')
    ipcefswitching_turboverctor = Suppress('IP CEF switching turbo vector')

    # TODO What are valid chars for VRF names?
    vrfname = Word(alphanums)
    vrf = Suppress('VPN Routing/Forwarding "') + Optional(vrfname('vrf')) + Suppress('"')
    downstreamvrf = Suppress('Downstream VPN Routing/Forwarding "') + Optional(vrfname('downstreamvrf')) + Suppress('"')

    ip_multicast_fastswitching = Suppress('IP multicast fast switching is') +\
                                 state_enabled_disabled('ip_multicast_fastswitching')
    ip_multicast_distributed_fastswitching = Suppress('IP multicast distributed fast switching is') +\
                                             state_enabled_disabled('ip_multicast_distributed_fastswitching')
    # TODO
    ip_routecache_flags = Suppress('IP route-cache flags are Fast, CEF')
    routerdiscovery = Suppress('Router Discovery is') + state_enabled_disabled('routerdiscovery')
    ip_output_accounting = Suppress('IP output packet accounting is') + state_enabled_disabled('ip_output_accounting')
    ip_violation_accounting = Suppress('IP access violation accounting is') + state_enabled_disabled('ip_violation_accounting')
    tcpip_header_compression = Suppress('TCP/IP header compression is') + state_enabled_disabled('tcpip_header_compression')
    rtpip_header_compression = Suppress('RTP/IP header compression is') + state_enabled_disabled('rtpip_header_compression')
    # TODO test with applied route-map
    policyrouting = Suppress('Policy routing is disabled')
    # TODO test with NAT
    nat = Suppress('Network address translation is disabled')
    # TODO
    bgppolicy = Suppress('BGP Policy Mapping is disabled')
    # TODO
    input_features = Suppress('Input features: MCI Check')
    # TODO
    output_features = Suppress('Output features: CCE Post NAT Classification')
    # TODO
    wccp_outbound = Suppress('WCCP Redirect outbound is disabled')
    # TODO
    wccp_inbound = Suppress('WCCP Redirect inbound is disabled')
    # TODO
    wccp_exclude = Suppress('WCCP Redirect exclude is disabled')

    # TODO account for multiple interfaces
    # TODO Test IPv6
    # TODO Test ip disabled -> "Internet protocol processing disabled"
    parser = interface('interface') + Suppress('is') + Optional(Suppress('administratively')) + interfacestatus('interface_status') + Suppress(',') +\
             Suppress('line protocol is') + line_status('line_status') +\
             Suppress('Internet address is') + ipprefix('ipaddress') +\
             Suppress('Broadcast address is') + ipaddress('broadcast_address')+\
             Suppress('Address determined by setup command')+\
             Suppress('MTU is') + mtu('mtu') + Suppress('bytes') +\
             helper_address +\
             directed_broadcasts +\
             outgoing_acl +\
             inbound_acl +\
             proxyarp +\
             local_proxyarp +\
             securitylevel +\
             splithorizon +\
             icmp_redirects +\
             icmp_unreachables +\
             icmp_mask_replies +\
             ipfastswitching +\
             ipfastswitching_sameinterface +\
             ipflowswitching +\
             ipcefswitching +\
             ipcefswitching_turboverctor +\
             Optional(vrf) +\
             Optional(downstreamvrf) +\
             ip_multicast_fastswitching +\
             ip_multicast_distributed_fastswitching +\
             ip_routecache_flags +\
             routerdiscovery +\
             ip_output_accounting +\
             ip_violation_accounting +\
             tcpip_header_compression +\
             rtpip_header_compression +\
             policyrouting +\
             nat +\
             bgppolicy +\
             input_features +\
             output_features +\
             wccp_outbound +\
             wccp_inbound +\
             wccp_exclude

    return parser


parse_show_ip_interface = partial(lambda x: show_ip_interface().parseString(x))
