import pygame as pg
from pygame import RESIZABLE, DOUBLEBUF, HWSURFACE, VIDEORESIZE, QUIT, KEYDOWN, MOUSEBUTTONDOWN
from itertools import cycle
from random import choice
from sys import exit
from datetime import datetime

# Colors
WHITE = (255, 255, 255)
LIGHTEST_GREY = (200, 200, 200)
LIGHTER_GREY = (150, 150, 150)
LIGHT_GREY = (110, 110, 110)
GREY = (64, 64, 64)
BLACK = (0, 0, 0)

COLORS = [LIGHTEST_GREY, LIGHTER_GREY, LIGHT_GREY, WHITE]
COLORS_CYCLE = cycle(COLORS)

# Game settings
FPS = 144
WIDTH = 1280
HEIGHT = 720
MIN_WIDTH = 640
MIN_HEIGHT = 360
MENU_HEIGHT = 40
TITLE = 'conway\'s game of life'
ICON = '../icon.ico'

CELL_SIZES = cycle([16, 32, 64, 8])
CELL_SIZE = next(CELL_SIZES)
MIN_CELL_SIZE = 6
MAX_CELL_SIZE = 200
CHANGE_CELL_SIZE = 1

START_GENS_PER_SEC = 20
MIN_GENS_PER_SEC = 1
MAX_GENS_PER_SEC = 50
CHANGE_GENS_PER_SEC = 1

# Mouse buttons
LMB = 0
RMB = 2
WHEEL_UP = 4
WHEEL_DOWN = 5

# Fonts
FONT = 'calibri'
FONT_MENU = 'arial'
