import sys
import logging
from libs import tcpcl_controller

if len(sys.argv) > 1:
    local_id=sys.argv[1]
    if local_id == 'upcn_server':
        print('{} is a reserved id. Choose another id and try again.'.format(local_id))
        exit()
else:
    print('Usage: {} uuid'.format(sys.argv[0]))
    exit()

formatter = logging.Formatter("%(asctime)s - [%(levelname)s] (%(module)s:%(lineno)d) %(message)s")
fh = logging.FileHandler('/tmp/{}.log'.format(local_id))
fh.setFormatter(formatter)
logging.getLogger().addHandler(fh)
logging.getLogger().setLevel(logging.INFO)
logging.info('Initializing tcpcl')

controller = tcpcl_controller.TCPCL_Controller(local_id)
sys.stdout.write('{}> '.format(local_id))
sys.stdout.flush()

while controller.shutdown == False:
    for key, mask in controller.selector.select():
        key.data['func'](key.fileobj, key.data, mask)
