import sys
from libs import tcpcl_controller

if len(sys.argv) > 0:
    local_id=sys.argv[0]
else:
    local_id='dtn_local'
controller = tcpcl_controller.TCPCL_Controller(local_id)

while controller.shutdown == False:
    sys.stdout.flush()
    sys.stdout.write('tcpcl> ')
    sys.stdout.flush()
    for key, mask in controller.selector.select():
        key.data['func'](key.fileobj, key.data, mask)
