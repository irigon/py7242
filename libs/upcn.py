import time

def create_contact(uuid, address, port, contact_list):
    clist = ','.join(contact_list)
    msg_str = '1({}):({}:{})::[{}];'.format(uuid, address, port, clist)
    return str.encode(msg_str)


# From git@gitlab.dtnsat.de:upcn/upcn.git
def make_contact_from_offset(start_offset, end_offset, bitrate, ctime=None):
    if ctime is None:
        ctime = int(time.time()) - 946684800
    return (ctime + int(start_offset), ctime + int(end_offset), bitrate)

