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
from pyparsing import Suppress, Keyword, Word, oneOf, ZeroOrMore, OneOrMore, Group, Combine, StringEnd, SkipTo, Optional, ParseException

from netcliparsers.lib import comma_list, ipaddress, ipaddress_list, ipprefix


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
    acl_name = Word(alphanums, bodyChars=alphanums + '_')

    interface_name = Word(alphas, bodyChars=alphanums + '/.-')
    interface_status = oneOf(['up', 'down', 'deleted'])
    line_status = oneOf(['up', 'down'])

    interface_ip_unnumbered = Suppress('Interface is unnumbered. Using address of ') +\
                              interface_name('interface_unnumbered_name') +\
                              Suppress('(') + ipaddress('interface_unnumbered_ipaddress') + Suppress(')')

    interface_ip_prefix = Suppress('Internet address is') + ipprefix('ipprefix')

    internet_address = (interface_ip_prefix | interface_ip_unnumbered)

    mtu = Word(nums).setParseAction(lambda tokens: int(tokens[0]))
   
    # FIXME Returns list of lists, instead of just a list with ipaddresses
    helper_addresses = Suppress('Helper addresses are') + ipaddress_list('helper_addresses')

    helper_address = ipaddress
    helper_address.setParseAction(lambda x: [x])
    helper_address = Suppress('Helper address is')  + (Suppress('not set') | helper_address('helper_addresses'))
    ip_helper = (helper_address | helper_addresses)

    directed_broadcasts_acl = Suppress('- but restricted by access list') + acl_name('directed_broadcasts_acl')
    directed_broadcasts = Suppress('Directed broadcast forwarding is') + state_enabled_disabled('directed_broadcasts') +\
                          Optional(directed_broadcasts_acl)

    outgoing_acl = Suppress('Outgoing access list is') + (Suppress('not set') | acl_name('outbound_acl'))
    inbound_acl = Suppress('Inbound  access list is') + (Suppress('not set') | acl_name('inbound_acl'))

    proxyarp = Suppress('Proxy ARP is') + state_enabled_disabled('proxyarp')

    local_proxyarp = Suppress('Local Proxy ARP is') + state_enabled_disabled('local_proxyarp')

    # TODO
    securitylevel = Suppress('Security level is default')
    splithorizon = Suppress('Split horizon is') + state_enabled_disabled('splithorizon')

    icmp_redirects = Suppress('ICMP redirects are') + state_always_never('icmp_redirects') + Suppress('sent')
    icmp_unreachables = Suppress('ICMP unreachables are') + state_always_never('icmp_unreachables') + Suppress('sent')
    icmp_mask_replies = Suppress('ICMP mask replies are') + state_always_never('icmp_maskreplies') + Suppress('sent')

    ip_fast_switching = Suppress('IP fast switching is') + state_enabled_disabled('ip_fast_switching')
    ip_fast_switching_sameinterface = Suppress('IP fast switching on the same interface is') + state_enabled_disabled('ip_fast_switching_sameinterface')
    ip_flow_switching = Suppress('IP Flow switching is') + state_enabled_disabled('ip_flow_switching')
    ip_cef_switching = Suppress('IP CEF switching is') + state_enabled_disabled('ip_cef_switching')

    turbo_vector = oneOf(['CEF switching', 'CEF turbo switching', 'Null'])
    ip_turbo_vector = Suppress('IP') + turbo_vector('ip_turbo_vector') +  Suppress('turbo vector')
    ip_turbo_vector2 = Suppress('IP') + turbo_vector('ip_turbo_vector2') + Suppress('turbo vector')

    # TODO What are valid chars for VRF names?
    vrfname = Word(alphanums)
    vrf = Suppress('VPN Routing/Forwarding "') + Optional(vrfname('vrf')) + Suppress('"')
    downstreamvrf = Suppress('Downstream VPN Routing/Forwarding "') + Optional(vrfname('downstreamvrf')) + Suppress('"')

    ip_multicast_fastswitching = Suppress('IP multicast fast switching is') +\
                                 state_enabled_disabled('ip_multicast_fastswitching')
    ip_multicast_distributed_fastswitching = Suppress('IP multicast distributed fast switching is') +\
                                             state_enabled_disabled('ip_multicast_distributed_fastswitching')

    ip_routecache_flags = Suppress('IP route-cache flags are') + comma_list('ip_routecache_flags')
    routerdiscovery = Suppress('Router Discovery is') + state_enabled_disabled('routerdiscovery')
    ip_output_accounting = Suppress('IP output packet accounting is') + state_enabled_disabled('ip_output_accounting')
    ip_violation_accounting = Suppress('IP access violation accounting is') + state_enabled_disabled('ip_violation_accounting')
    tcpip_header_compression = Suppress('TCP/IP header compression is') + state_enabled_disabled('tcpip_header_compression')
    rtpip_header_compression = Suppress('RTP/IP header compression is') + state_enabled_disabled('rtpip_header_compression')

    routemap_name = Word(alphas, bodyChars=alphanums + '_-')
    policy_routing_enabled = Suppress(', using route map') + routemap_name('policy_routing_routemap')
    policy_routing = Suppress('Policy routing is') + state_enabled_disabled('policy_routing') + Optional(policy_routing_enabled)

    nat_inside_outside = oneOf(['inside', 'outside'])
    nat_domain = Suppress(', interface in domain') + nat_inside_outside('nat_domain')
    nat = Suppress('Network address translation is') + state_enabled_disabled('nat_state') + Optional(nat_domain)

    bgp_policy_map = Word(alphanums, bodyChars=alphanums + '-')
    bgp_policies = Optional(Suppress('(output') + bgp_policy_map('bgp_policy_map_output') + Suppress(')')) +\
                   Optional(Suppress('(input') + bgp_policy_map('bgp_policy_map_input') + Suppress(')'))

    bgp_policy = Suppress('BGP Policy Mapping is') + state_enabled_disabled('bgp_policy') + bgp_policies

    input_features = Suppress('Input features:') + comma_list('input_features')
    output_features = Suppress('Output features:') + comma_list('output_features')

    wccp_outbound = Optional(Suppress('IPv4')) + Suppress('WCCP Redirect outbound is') + state_enabled_disabled('wccp_outbound')
    wccp_inbound = Optional(Suppress('IPv4')) + Suppress('WCCP Redirect inbound is') + state_enabled_disabled('wccp_inbound')
    wccp_exclude = Optional(Suppress('IPv4')) + Suppress('WCCP Redirect exclude is') + state_enabled_disabled('wccp_exclude')

    interface = interface_name('interface_name') + Suppress('is') + Optional(Suppress('administratively')) +\
                                             interface_status('interface_status') + Suppress(',') +\
             Suppress('line protocol is') + line_status('line_status') +\
             internet_address +\
             Suppress('Broadcast address is') + ipaddress('broadcast_address')+\
             Optional(Suppress('Address determined by setup command')) +\
             Suppress('MTU is') + mtu('mtu') + Suppress('bytes') +\
             ip_helper +\
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
             ip_fast_switching +\
             ip_fast_switching_sameinterface +\
             ip_flow_switching +\
             ip_cef_switching +\
             ip_turbo_vector +\
             Optional(ip_turbo_vector2) +\
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
             policy_routing +\
             nat +\
             bgp_policy +\
             input_features +\
             Optional(output_features) +\
             wccp_outbound +\
             wccp_inbound +\
             wccp_exclude

    interface_ip_disabled = interface_name('interface_name') + Suppress('is') + Optional(Suppress('administratively')) +\
                                                          interface_status('interface_status') +\
                                                          Suppress(',') +\
                                                          Suppress('line protocol is') + line_status('line_status') +\
                            Suppress('Internet protocol processing') + state_enabled_disabled('ip_state')

    parser = OneOrMore(Group(interface) | Group(interface_ip_disabled)) + StringEnd()

    return parser


parse_show_ip_interface = partial(lambda x: show_ip_interface().parseString(x))
