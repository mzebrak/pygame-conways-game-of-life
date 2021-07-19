from itertools import cycle


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (64, 64, 64)

# Game settings
WIDTH = 1280
HEIGHT = 720
MENU_HEIGHT = 40
TITLE = 'conway\'s game of life'
ICON = 'icon.ico'
CELL_SIZE = 16
CELL_SIZES = cycle([8, 16, 32, 64])
GENS_PER_SEC = 20
FPS = 144

# Mouse buttons
LMB = 0
RMB = 2

# Font
FONT = 'calibri'
FONT_MENU = 'arial'