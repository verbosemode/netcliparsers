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

from pyparsing import Word, alphanums, nums, ParseException, Combine, OneOrMore

def parse_action_comma_list(tokens):
    try:
        l = tokens[0].split(',')

        return [e.strip() for e in l]
    except ValueError, ve:
        raise ParseException("Invalid comma list (%s)" % tokens[0])

# Parses: foo, bar, baz and returns all items in a list
comma_list = Word(alphanums, bodyChars=alphanums + ',- ').setParseAction(parse_action_comma_list)

# TODO This should be more strict
ipaddress = Combine(Word(nums) + '.' + Word(nums) + '.' + Word(nums) + '.' + Word(nums))
# def parse_action_ipaddress_list(tokens):
#     try:
#         return [e[0] for e in tokens]
#     except ValueError, ve:
#         raise ParseException("Invalid ipaddress list (%s)" % tokens[0])

ipaddress_list = OneOrMore(ipaddress)
#ipaddress_list.setParseAction(parse_action_ipaddress_list)

ipprefix = Combine(ipaddress + '/' + Word(nums))
