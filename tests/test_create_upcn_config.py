import unittest
import sys, os
import time

sys.path.insert(0, os.path.abspath('.'))

from libs import upcn


class TestCreateConfig(unittest.TestCase):
    # given the node_id, peername, contact list, prepare message for upcn
    def test_create_config(self):
        addr = '127.0.0.1'
        port = 42421
        uuid = 'dtn:1'
        clist = ['{575106956,575106958,500}']
        contact = upcn.create_contact(uuid, addr, port, clist)
        # values copied from upcn current run
        self.assertEqual(contact, b'1(dtn:1):(127.0.0.1:42421)::[{575106956,575106958,500}];')

    def test_make_contact_from_offset(self):
        now = int(time.time())
        contact = upcn.make_contact_from_offset(10, 12, 500, now)
        self.assertEqual(contact, (now + 10, now + 12, 500))

    def test_read_clist_from_file(self):
        file = 'tests/clist_example'
        addr = '127.0.0.1'
        port = 42421
        uuid = 'dtn:1'

        with open(file, 'r') as contact_list:
            lines = [x.rstrip() for x in contact_list.readlines()]

        contacts = [ upcn.make_contact_from_offset(*(x.split(' '))) for x in lines]
        #ctest = upcn.create_contact(uuid, addr, port, contacts)
        print(contacts)
