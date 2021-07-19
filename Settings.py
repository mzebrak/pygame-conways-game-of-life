from itertools import cycle

# Colors
WHITE = (255, 255, 255)
LIGHTEST_GREY = (200, 200, 200)
LIGHTER_GREY = (150, 150, 150)
LIGHT_GREY = (110, 110, 110)
GREY = (64, 64, 64)
BLACK = (0, 0, 0)

COLORS = [LIGHTEST_GREY, LIGHTER_GREY, LIGHT_GREY, WHITE]
COLORS_CYCLE = cycle(COLORS)
DEAD_COLOR = next(COLORS_CYCLE)

# Game settings
WIDTH = 1280
HEIGHT = 720
MENU_HEIGHT = 40
TITLE = 'conway\'s game of life'
ICON = 'icon.ico'

CELL_SIZES = cycle([16, 32, 64, 8])
CELL_SIZE = next(CELL_SIZES)
GENS_PER_SEC = 20
FPS = 144

# Mouse buttons
LMB = 0
RMB = 2
WHEEL_UP = 4
WHEEL_DOWN = 5

# Font
FONT = 'calibri'
FONT_MENU = 'arial'
