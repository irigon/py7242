import argparse

parser = argparse.ArgumentParser("do something")

parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer###')
parser.add_argument('--braulio', dest='acumulei', help='sum of something')
args=parser.parse_args(['4', '--braulio', 'foo'])
print(args)

