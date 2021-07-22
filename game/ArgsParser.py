from argparse import ArgumentParser


class ArgsParser:
    def __init__(self):
        par = ArgumentParser(description='github.com/m-zebrak implementation of conway\'s game of life')
        par.add_argument('-s', '--size', metavar='INT', type=int, default=0,
                         help='startup size of each cell (INT x INT)',
                         required=False)
        par.add_argument('-f', '--fps', metavar='INT', type=int, default=0,
                         help='set the framerate cap during the game',
                         required=False)
        par.add_argument('-g', '--gens_per_sec', metavar='INT', type=int, default=0,
                         help='startup number of generations per sec',
                         required=False)
        par.add_argument('-W', '--width', metavar='INT', type=int, default=0,
                         help='startup screen width',
                         required=False)
        par.add_argument('-H', '--height', metavar='INT', type=int, default=0,
                         help='startup screen height',
                         required=False)
        par.add_argument('-F', '--file', metavar='PATH', type=str, default=None,
                         help='relative path from __main__ to the folder with the file,  ex. ../patterns/glider.txt',
                         required=False)
        args = vars(par.parse_args())
        self.size = args['size']
        self.fps = args['fps']
        self.gens = args['gens_per_sec']
        self.width = args['width']
        self.height = args['height']
        self.file = args['file']
