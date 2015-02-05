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


