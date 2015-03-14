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


For convenience all functions also exist with a prepended *parse_*.

::

    for e in parse_show_cdp_neighbor_detail(text)
        print(e['deviceid'])


TODO
----

* Tests

  - CLI output examples: netcliparsers/tests/data

* Version number scheme
* Should be Python >= 2.7 compatible

  - Pyparsing is Python 3 compatible

* PyPi if the topics above are implemented
* Use Sphinx/autodoc for generating documentation under docs/


How to contribute
-----------------

* Code should follow PEP8
* If you add CLI output to the tests (netcliparsers/tests/data), make sure you
  are sanitizing the output to not leak any data of your network equipment.
* Feel free to fix grammer mistakes. I'm not a native English speaker
* Make a pull request


Windows
-------

If you run the setup on Windows you'll need to have git installed. Pbr tries to figure out the version number via git. I'll need to fix this "soon".


License
-------

GPLv3

Feedback
--------

Bug reports, patches and ideas are welcome.

Just send me an e-mail (jochenbartl@mailbox.org) or open an issue on GitHub
