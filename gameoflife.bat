rem PROGRAM OPTIONS:
rem '-s', '--size', type=int, default=CELL_SIZE, help='startup size of each cell (INT x INT) between MIN_CELL_SIZE andMAX_CELL_SIZE', required=False
rem '-f', '--fps', type=int, default=FPS, help='set the framerate cap during the game, must be greater or equal 1', required=False
rem '-g', '--gens_per_sec', metavar='INT', type=int, default=START_GENS_PER_SEC, help='startup number of generations per sec, between MIN_GENS_PER_SEC and MAX_GENS_PER_SEC', required=False
rem '-W', '--width', metavar='INT', type=int, default=WIDTH, help='startup screen width, must be greater than MIN_WIDTH', required=False
rem '-H', '--height', metavar='INT', type=int, default=HEIGHT, help='startup screen height, must be greater than MIN_HEIGHT', required=False
rem '-F', '--file', metavar='PATH', type=str, default=None, help='relative path from __main__ to the folder with the file,  ex. ../patterns/glider.txt', required=False
cd game
@py __main__.py -s 16 --gens_per_sec 10 -F "../patterns/spacefiller.txt"