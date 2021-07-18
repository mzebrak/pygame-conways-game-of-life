from itertools import cycle
from math import floor
import random
import sys
import pygame as pg

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (64, 64, 64)

# Game settings
WIDTH = 1024
HEIGHT = 768
MENU_HEIGHT = 40
TITLE = 'conway\'s game of life'
ICON = 'icon.ico'
CELL_SIZES = cycle([5, 10, 15, 20, 32, 64])

# Mouse buttons
LMB = 0
RMB = 2

# Fonts
FONT = 'calibri'


class Cell(pg.sprite.Sprite):
    def __init__(self, game, cell_size, x, y, ):
        super().__init__(game.sprites)
        self.image = pg.Surface([cell_size, cell_size])
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * cell_size, y * cell_size)
        self.kill()

    def kill(self, color=WHITE):
        self.alive = False
        self.image.fill(color)

    def revive(self, color=BLACK):
        self.alive = True
        self.image.fill(color)


class GameOfLife:
    def __init__(self, cell_size=15, max_fps=20):
        """
        Initialize screen, initialize grid, set game settings, draw first frame

        :param cell_size: Dimension of the square
        :param max_fps: Framerate cap to limit the speed of the game
        """
        pg.init()
        pg.display.set_icon(pg.image.load(ICON))
        pg.display.set_caption(TITLE)

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))

        self.cell_size = 1 if cell_size < 1 else cell_size
        self.max_fps = 1 if max_fps < 1 else max_fps

        self.new()
        self.calculate_font_size()

        self.paused = False
        self.show_grid = True

    def new(self, randomize: int = 0):
        self.sprites = pg.sprite.Group()

        if randomize == 1 or randomize == 2:
            width_before = self.grid_width
            height_before = self.grid_height

        self.grid_width = int(WIDTH / self.cell_size)
        self.grid_height = int((HEIGHT - MENU_HEIGHT) / self.cell_size)

        self.margin_x = int((WIDTH - self.grid_width * self.cell_size) / 2)
        self.grid_image = pg.Surface((self.grid_width * self.cell_size + 1, self.grid_height * self.cell_size + 1))

        if randomize == 0:
            self.cells = []
            for x in range(self.grid_width):
                self.cells.append([])
                for y in range(self.grid_height):
                    self.cells[x].append(Cell(self, self.cell_size, x, y))

            self.fill_grid()
        else:
            temp = [[False] * self.grid_height for _ in range(self.grid_width)]

            if randomize == 1:
                for x in range(width_before):
                    for y in range(height_before):
                        if self.cells[x][y].alive:
                            temp[x][y] = True
            elif randomize == 2:
                for x in range(self.grid_width):
                    for y in range(self.grid_height):
                        if self.cells[x][y].alive:
                            temp[x][y] = True

            self.cells = []

            for x in range(self.grid_width):
                self.cells.append([])
                for y in range(self.grid_height):
                    self.cells[x].append(Cell(self, self.cell_size, x, y))
                    if temp[x][y]:
                        self.cells[x][y].revive()

        self.screen.fill(WHITE)
        self.generation = 0
        self.alive_cells = 0

    def calculate_font_size(self):
        sample = "Generation: XXXXXX  Alive cells: XXXXXX"
        div = 1

        while True:
            div += 1
            self.font = pg.font.SysFont(FONT, int(WIDTH / div))
            text_width, text_height = self.font.size(sample)

            if text_width < WIDTH and text_height < MENU_HEIGHT:
                break

    def fill_grid(self, value=None):
        """
        Sets the entire grid to a single specified or random value
        fill_grid(0)                   - all dead
        fill_grid(1)                   - all alive
        fill_grid() or fill_grid(None)  - randomize

        :param value:  Value to set the cell to (0 or 1)
        """
        self.generation = 0

        for x in range(self.grid_width):
            for y in range(self.grid_height):

                if value is None:
                    if random.choice([0, 1]) == 1:
                        self.cells[x][y].revive()
                    else:
                        self.cells[x][y].kill()
                elif value == 0:
                    self.cells[x][y].kill()
                elif value == 1:
                    self.cells[x][y].revive()

    def draw_grid(self):
        width = self.grid_width * self.cell_size
        height = self.grid_height * self.cell_size

        for x in range(0, width, self.cell_size):
            pg.draw.line(self.grid_image, GREY, (x, 0), (x, height))

        for y in range(0, height, self.cell_size):
            pg.draw.line(self.grid_image, GREY, (0, y), (width, y))

    def count_alive_cells(self):
        total = 0
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if self.cells[x][y].alive:
                    total += 1
        self.alive_cells = total

    def draw_info(self):
        """
        Displaying information about generation and alive cells
        """
        self.count_alive_cells()
        print(f'Generation: {self.generation}, alive cells: {self.alive_cells}')

        text1 = self.font.render(f'Generation: {self.generation}', True, BLACK, WHITE)
        text2 = self.font.render(f'Alive cells: {self.alive_cells}', True, BLACK, WHITE)

        text1_rect = text1.get_rect()
        text2_rect = text2.get_rect()

        text1_rect.topleft = (0, HEIGHT - MENU_HEIGHT + 1)
        text2_rect.topleft = (WIDTH - text2_rect.width, HEIGHT - MENU_HEIGHT + 1)

        pg.draw.rect(self.screen, WHITE, (0, HEIGHT - MENU_HEIGHT + 1, WIDTH, MENU_HEIGHT))
        self.screen.blit(text1, text1_rect)
        self.screen.blit(text2, text2_rect)

    def draw(self):
        self.sprites.draw(self.grid_image)

        if self.show_grid:
            self.draw_grid()

        self.screen.blit(self.grid_image, (self.margin_x, 0))
        self.draw_info()
        pg.display.flip()

    def count_cell_neighbors(self, col, row):
        """
        Get the number of alive neighbors of a specific cell from the active grid

        :param col: The index of the specific cell
        :param row: The index of the specific cell
        :return: The number of alive neighbors
        """
        num_of_alive_neighbors = 0

        for i in range(-1, 2):
            for j in range(-1, 2):
                x = (col + i + self.grid_width) % self.grid_width
                y = (row + j + self.grid_height) % self.grid_height
                if self.cells[x][y].alive:
                    num_of_alive_neighbors += 1

        if self.cells[col][row].alive:
            num_of_alive_neighbors -= 1
        return num_of_alive_neighbors

    def set_cells_state(self):
        """
        Sets the (0/1) state of every cell in the inactive grid depending on the number of neighbors from the active grid
        """
        temp = []

        for x in range(self.grid_width):
            temp.append([])

            for y in range(self.grid_height):
                state = self.cells[x][y].alive
                neighbors = self.count_cell_neighbors(x, y)

                if state == 0 and neighbors == 3:
                    temp[x].append(True)
                elif state == 1 and neighbors < 2 or neighbors > 3:
                    temp[x].append(False)
                else:
                    temp[x].append(state)

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if temp[x][y]:
                    self.cells[x][y].revive()
                else:
                    self.cells[x][y].kill()

    def update_generation(self):
        """
        Calls function which set the state of every cell then swaps the active and inactive grid and increments generation counter
        """
        self.set_cells_state()
        self.generation += 1

    def compute_mouse_pos(self, pos):
        """
        A function that gets the tuple (col, row) of the clicked cell
        :param pos: Position in px where the mouse was when clicked
        :return: None if clicked below grid otherwise tuple (col, row)
        """
        # only if clicked above menu bar (on the grid image)
        if self.margin_x < pos[0] < (self.grid_width * self.cell_size + self.margin_x):
            if 0 < pos[1] < (self.grid_height * self.cell_size):
                return floor((pos[0] - self.margin_x) / self.cell_size), floor(pos[1] / self.cell_size)
        return None, None

    @staticmethod
    def quit():
        pg.quit()
        sys.exit()

    def handle_events(self):
        """
        Handle key presses
        g - toggle on/off grid
        p - toggle start/stop (pause) the game
        t - switch between cell sizes
        z - decrease cell size
        x - increase cell size
        n - display next generation
        r - randomize grid
        c - clear grid
        q - quit
        LMB - pressed or held sets cell alive
        RMB - pressed or held sets cell dead
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    print("'p' pressed! - toggling pause")
                    self.paused = not self.paused
                elif event.key == pg.K_q:
                    print("'q' pressed! - quitting the game")
                    self.quit()
                elif event.key == pg.K_r:
                    print("'r' pressed! - randomizing grid")
                    self.fill_grid()
                elif self.paused and event.key == pg.K_n:
                    print("'n' pressed! - displaying next generation")
                    self.update_generation()
                elif self.paused and event.key == pg.K_c:
                    print("'c' pressed! - clearing active grid")
                    self.fill_grid(0)
                elif event.key == pg.K_t:
                    print("'t' pressed! - changing cell size")
                    self.cell_size = next(CELL_SIZES)
                    self.new()
                elif event.key == pg.K_g:
                    print("'g' pressed! - toggling grid")
                    self.show_grid = not self.show_grid
                elif event.key == pg.K_x:
                    print("'x' pressed! - cell size increased")
                    self.cell_size += 2 if self.cell_size < 100 else 0
                    self.new(randomize=2)
                elif event.key == pg.K_z:
                    print("'z' pressed! - cell size decreased")
                    self.cell_size -= 2 if self.cell_size > 5 else 0
                    self.new(randomize=1)
            elif button := pg.mouse.get_pressed(num_buttons=3):
                col, row = None, None

                try:
                    col, row = self.compute_mouse_pos(event.pos)
                except AttributeError:  # when the mouse is pressed down and moved out of the window
                    pass

                if not col:
                    continue

                state = self.cells[col][row].alive

                if button[LMB] and not state:
                    self.cells[col][row].revive()
                elif button[RMB] and state:
                    self.cells[col][row].kill()
                else:
                    continue

            self.draw()

    def run(self):
        """
        Starts the game and loops until the quit state
        """
        while True:
            self.handle_events()

            if not self.paused:
                self.draw()
                self.update_generation()

                # when paused - the user is able to set or delete cells by mouse with more fps
                pg.time.Clock().tick(self.max_fps)
