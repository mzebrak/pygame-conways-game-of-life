from GameOfLife import GameOfLife
from ArgsParser import ArgsParser

args = ArgsParser()
GameOfLife(cell_size=args.size, fps=args.fps, gens_per_sec=args.gens, width=args.w, height=args.h).run()
