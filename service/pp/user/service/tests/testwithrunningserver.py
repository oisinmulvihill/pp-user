# -*- coding: utf-8 -*-
"""
Integration Test against a running instance of the WebService.

PythonPro Limited
2012-01-15

"""
import json
import unittest

from . import svrhelp
from pp.bookingsys import restclient


# Start the test app running on module set up and stop it running on teardown.
#
def setup_module():
    svrhelp.setup_module()
    restclient.init(svrhelp.webapp.URI)

teardown_module = svrhelp.teardown_module


class WebServiceTestCase(unittest.TestCase):

    def test_organisation_load(self):
        """Test the load/dump Organisation operations.
        """
        cfg = json.dumps(dict(
            expert_names=['Alan', 'Barbara', 'Charles', 'David'],
            room_names=['Room One', 'Room Two', 'The Studio'],
            massage_table_names=['one-piece', 'one-piece2', 'folding', 'large', 'use mat instead'],
            requirements=[
                ('alan', 'room one'),
                ('alan', 'folding'),
                ('barbara', 'room two'),
                ('barbara', 'one-piece', 'prefer'),
                ('room two', 'large'),
                ('david', 'folding'),
            ]
        ))

        print "Send set up to server: "

        org = restclient.Organisation()

        org.load('massaaage', cfg)

        print "Recovering set up from server: "

        fixture = org.dump('massaaage')

        print "fixture:\n%s\n\n" % fixture

        # The web server should be running at this point.
        #print "Press return to exit." ; raw_input("")

        return

        #org = Organisation.load(cfg)

        # ok cases
        found = org.resource_by_name('alan')
        self.assertTrue(isinstance(found, resources.expert.Expert))
        self.assertEquals(found.name, 'alan')

        found = org.resource_by_name('room two')
        self.assertTrue(isinstance(found, resources.location.Room))
        self.assertEquals(found.name, 'room two')

        found = org.resource_by_name('ROOM two') # case shouldn't matter
        self.assertTrue(isinstance(found, resources.location.Room))
        self.assertEquals(found.name, 'room two')

        found = org.resource_by_name(' ROOM two ') # start/end whitespace shouldn't matter
        self.assertTrue(isinstance(found, resources.location.Room))
        self.assertEquals(found.name, 'room two')
