from Settings import CELL_SIZE, WIDTH, HEIGHT, FPS, START_GENS_PER_SEC
from argparse import ArgumentParser


class ArgsParser:
    def __init__(self):
        par = ArgumentParser(description='github.com/m-zebrak implementation of conway\'s game of life')
        par.add_argument('-s', '--size', metavar='INT', type=int, default=CELL_SIZE,
                         help='startup size of each cell (INT x INT) between MIN_CELL_SIZE and MAX_CELL_SIZE',
                         required=False)
        par.add_argument('-f', '--fps', metavar='INT', type=int, default=FPS,
                         help='set the framerate cap during the game, must be greater or equal 1',
                         required=False)
        par.add_argument('-g', '--gens', metavar='INT', type=int, default=START_GENS_PER_SEC,
                         help='startup number of generations per sec, between MIN_GENS_PER_SEC and MAX_GENS_PER_SEC',
                         required=False)
        par.add_argument('-W', '--width', metavar='INT', type=int, default=WIDTH,
                         help='startup screen width, must be greater than MIN_WIDTH',
                         required=False)
        par.add_argument('-H', '--height', metavar='INT', type=int, default=HEIGHT,
                         help='startup screen height, must be greater than MIN_HEIGHT',
                         required=False)
        par.add_argument('-F', '--file', metavar='PATH', type=str, default=None,
                         help='relative path from __main__ to the folder with the file,  ex. ../patterns/glider.txt',
                         required=False)
        args = vars(par.parse_args())
        self.size = args['size']
        self.fps = args['fps']
        self.gens = args['gens']
        self.width = args['width']
        self.height = args['height']
        self.file = args['file']
