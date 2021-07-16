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
HEIGHT = 200
MENU_HEIGHT = 40
TITLE = 'conway\'s game of life'
ICON = 'icon.ico'
CELL_SIZES = cycle([5, 10, 16, 32, 40])

# Mouse buttons
LMB = 0
RMB = 2


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
        self.paused = False
        self.show_grid = True

    def new(self, randomize: int = 0):
        if randomize == 1:
            cols_before = self.grid_cols
            rows_before = self.grid_rows

        self.grid_cols = int(WIDTH / self.cell_size)
        self.grid_rows = int((HEIGHT - MENU_HEIGHT) / self.cell_size)

        if randomize == 0:
            self.grid = [[0] * self.grid_rows for _ in range(self.grid_cols)]
            self.fill_grid()
        elif randomize == 1:
            temp = [[0] * self.grid_rows for _ in range(self.grid_cols)]

            for c in range(cols_before):
                for r in range(rows_before):
                    temp[c][r] = self.grid[c][r]
            self.grid = temp

        self.width_margin = int((WIDTH - self.grid_cols * self.cell_size) / 2)
        self.height_margin = int((HEIGHT - MENU_HEIGHT - self.grid_rows * self.cell_size) / 2)

        self.screen.fill(WHITE)
        self.generation = 0
        self.alive_cells = 0

    def fill_grid(self, value=None):
        """
        Sets the entire grid to a single specified or random value
        fill_grid(0)                   - all dead
        fill_grid(1)                   - all alive
        fill_grid() or fill_grid(None)  - randomize

        :param value:  Value to set the cell to (0 or 1)
        """
        self.generation = 0
        self.grid = [[random.choice([0, 1]) if value is None else value for x in self.grid[0]] for y in self.grid]

    def draw_grid(self):
        width = self.grid_cols * self.cell_size + self.width_margin
        height = self.grid_rows * self.cell_size + self.height_margin

        for x in range(self.width_margin, width + self.width_margin, self.cell_size):
            pg.draw.line(self.screen, GREY, (x, self.height_margin), (x, height))

        for y in range(self.height_margin, height + self.height_margin, self.cell_size):
            pg.draw.line(self.screen, GREY, (self.width_margin, y), (width, y))

    def draw(self):
        """
        Draw the cells from active grid on the screen
        """
        self.alive_cells = 0

        for x in range(0, self.grid_cols):
            for y in range(0, self.grid_rows):
                if self.grid[x][y] == 1:
                    self.alive_cells += 1
                    color = BLACK
                else:
                    color = WHITE
                pg.draw.rect(self.screen, color,
                             (x * self.cell_size + self.width_margin, y * self.cell_size + self.height_margin,
                              self.cell_size,
                              self.cell_size))

        if self.show_grid:
            self.draw_grid()
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
                c = (col + i + self.grid_cols) % self.grid_cols
                r = (row + j + self.grid_rows) % self.grid_rows
                num_of_alive_neighbors += self.grid[c][r]

        num_of_alive_neighbors -= self.grid[col][row]
        return num_of_alive_neighbors

    def set_cells_state(self):
        """
        Sets the (0/1) state of every cell in the inactive grid depending on the number of neighbors from the active grid
        """
        temp = []

        for c in range(self.grid_cols):
            temp.append([])

            for r in range(self.grid_rows):
                state = self.grid[c][r]
                neighbors = self.count_cell_neighbors(c, r)

                if state == 0 and neighbors == 3:
                    temp[c].append(1)
                elif state == 1 and neighbors < 2 or neighbors > 3:
                    temp[c].append(0)
                else:
                    temp[c].append(state)
        self.grid = temp

    def update_generation(self):
        """
        Calls function which set the state of every cell then swaps the active and inactive grid and increments generation counter
        """
        self.set_cells_state()
        self.generation += 1

    def display_info(self):
        """
        Displaying information about generation and alive cells in the bottom
        """
        print(f'Generation: {self.generation}, alive cells: {self.alive_cells}')

        div = 1

        while True:
            font = pg.font.SysFont("Arial", int(MENU_HEIGHT / div))

            text1 = font.render(f'Generation: {self.generation}', True, (0, 0, 0), (255, 255, 255))
            text2 = font.render(f'Alive cells: {self.alive_cells}', True, (0, 0, 0), (255, 255, 255))

            text1_rect = text1.get_rect()
            text2_rect = text2.get_rect()

            div += 1

            if WIDTH > text1_rect.width + text2_rect.width:
                break

        text1_rect.topleft = (0, HEIGHT - MENU_HEIGHT)
        text2_rect.topleft = (WIDTH - text2_rect.width, HEIGHT - MENU_HEIGHT)

        pg.draw.rect(self.screen, WHITE,
                     (0, HEIGHT - MENU_HEIGHT, WIDTH, MENU_HEIGHT))
        self.screen.blit(text1, text1_rect)
        self.screen.blit(text2, text2_rect)
        pg.display.flip()

    def clear_screen(self):
        """
        Fill the entire screen with dead_color
        """
        self.screen.fill(WHITE)

    def get_col_row_by_mouse(self, pos):
        """
        A function that gets the tuple (col, row) of the clicked cell
        :param pos: Position in px where the mouse was when clicked
        :return: None if clicked below grid otherwise tuple (col, row)
        """
        # only if clicked above menu bar (on the grid)
        if self.width_margin < pos[0] < (self.grid_cols * self.cell_size + self.width_margin):
            if self.height_margin < pos[1] < (self.grid_rows * self.cell_size + self.height_margin):
                return floor((pos[0] - self.width_margin) / self.cell_size), floor(
                    (pos[1] - self.height_margin) / self.cell_size)
        return None

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
            elif click := pg.mouse.get_pressed(num_buttons=3):
                col_row = None

                try:
                    col_row = self.get_col_row_by_mouse(event.pos)
                except AttributeError:  # when the mouse is pressed down and moved out of the window
                    pass

                if col_row is None:
                    continue

                col, row = col_row
                cell = self.grid[col][row]

                if click[LMB] and cell == 0:
                    self.grid[col][row] = 1
                elif click[RMB] and cell == 1:
                    self.grid[col][row] = 0
                else:
                    continue

            self.draw()
            self.display_info()

    def run(self):
        """
        Starts the game and loops until the quit state
        """
        while True:
            self.handle_events()

            if not self.paused:
                self.draw()
                self.display_info()
                self.update_generation()

                # when paused - the user is able to set or delete cells by mouse with more fps
                pg.time.Clock().tick(self.max_fps)
