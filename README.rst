netcliparsers - Parser library for screen scraping CLI output from network devices
==================================================================================

This will become a library of parsers based on `pyparsing <http://pyparsing.wikispaces.com/>`_ for parsing screen scraped CLI text output from network devices.


Usage Examples
--------------

Functions return a pyparsing parser instance.

::

    from netcliparsers.cisco.ios import show_cdp_neighbor_detail

    parser = show_cdp_neighbor_detail()
    for e in parser.parseString(text):
        print("{deviceid} {localinterface} {remoteinterface}".format(**e)):

    ap1.example.com FastEthernet0/25 GigabitEthernet0.1
    ap2.example.com FastEthernet0/37 GigabitEthernet0.1
    sw1.example.com GigabitEthernet0/1 GigabitEthernet2/4
    sw2.example.com GigabitEthernet0/2 GigabitEthernet0/26


For convenience all functions also exist with a prepended 'parse_'.

::

    for e in parse_show_cdp_neighbor_detail(text)
        print(e['deviceid'])


Windows
-------

If you run the setup on Windows you'll need to have git installed. Pbr tries to figure out the version number via git. I'll need to fix this "soon".


Feedback
--------

Bug reports, patches and ideas are welcome.

Just send me an e-mail (jochenbartl@mailbox.org) or open an issue on GitHub
