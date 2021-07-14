from math import floor
import random
import sys
import pygame as pg

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game settings
WIDTH = 640
HEIGHT = 480
MENU_HEIGHT = 50
TITLE = 'conway\'s game of life'
ICON = 'icon.ico'


class GameOfLife:
    def __init__(self, cell_size=10, max_fps=20):
        """
        Initialize screen, initialize grid, set game settings, draw first frame

        :param cell_size: Dimension of the square
        :param max_fps: Framerate cap to limit the speed of the game
        """
        pg.init()
        pg.display.set_icon(pg.image.load(ICON))
        pg.display.set_caption(TITLE)

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()

        self.cell_size = 1 if cell_size < 1 else cell_size
        self.max_fps = 1 if max_fps < 1 else max_fps

        self.new()

    def new(self):
        self.grid_width = int(WIDTH / self.cell_size)
        self.grid_height = int((HEIGHT - MENU_HEIGHT) / self.cell_size)

        print(f'num of cols: {self.grid_width}, num of rows: {self.grid_height}')

        self.grids = [[[0] * self.grid_height for _ in range(self.grid_width)],
                      [[0] * self.grid_height for _ in range(self.grid_width)],
                      ]

        self.active_grid = 0
        self.fill_grid()

        self.generation = 0
        self.alive_cells = 0
        self.paused = False
        self.exit = False

    def fill_grid(self, value=None):
        """
        Sets the entire grid to a single specified or random value
        fill_grid(0)                   - all dead
        fill_grid(1)                   - all alive
        fill_grid() or fill_grid(None)  - randomize

        :param value:  Value to set the cell to (0 or 1)
        """
        self.grids[self.active_grid] = [[random.choice([0, 1]) if value is None else value for x in
                                         self.grids[self.active_grid][0]] for y in
                                        self.grids[self.active_grid]]

    def draw_grid(self):
        """
        Draw the cells from active grid on the screen
        """
        self.alive_cells = 0
        for c in range(self.grid_width):
            for r in range(self.grid_height):
                if self.grids[self.active_grid][c][r] == 1:
                    self.alive_cells += 1
                    color = BLACK
                else:
                    color = WHITE
                pg.draw.rect(self.screen, color,
                             (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size))
        pg.display.flip()

    def get_inactive_grid(self):
        """
        :return: The index of the inactive grid
        """
        return (self.active_grid + 1) % 2

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
                c = (col + i + self.grid_width) % self.grid_width
                r = (row + j + self.grid_height) % self.grid_height
                num_of_alive_neighbors += self.grids[self.active_grid][c][r]

        num_of_alive_neighbors -= self.grids[self.active_grid][col][row]
        return num_of_alive_neighbors

    def set_cells_state(self):
        """
        Sets the (0/1) state of every cell in the inactive grid depending on the number of neighbors from the active grid
        """
        for c in range(self.grid_width):
            for r in range(self.grid_height):
                state = self.grids[self.active_grid][c][r]
                inactive = self.get_inactive_grid()
                neighbors = self.count_cell_neighbors(c, r)

                if state == 0 and neighbors == 3:
                    self.grids[inactive][c][r] = 1
                elif state == 1 and neighbors < 2 or neighbors > 3:
                    self.grids[inactive][c][r] = 0
                else:
                    self.grids[inactive][c][r] = state

    def update_generation(self):
        """
        Calls function which set the state of every cell then swaps the active and inactive grid and increments generation counter
        """
        self.set_cells_state()
        self.active_grid = self.get_inactive_grid()
        self.generation += 1

    def display_info(self):
        """
        Displaying information about generation and alive cells in the bottom
        """
        print(f'Generation: {self.generation}')
        print(f'Alive cells: {self.alive_cells}')

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
        if pos[1] < (HEIGHT - MENU_HEIGHT):
            return floor(pos[0] / self.cell_size), floor(pos[1] / self.cell_size)
        return None

    def handle_events(self):
        """
        Handle key presses

        p - toggle start/stop (pause) the game
        r - randomize grid
        n - display next generation
        c - clear grid
        q - quit
        LMB - pressed or held sets cell alive
        RMB - pressed or held sets cell dead
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    print("'p' pressed! - toggling pause")
                    self.paused = not self.paused
                elif event.key == pg.K_q:
                    print("q pressed! - quitting the game")
                    self.exit = True
                elif event.key == pg.K_r:
                    print("'r' pressed! - randomizing grid")
                    self.generation = 0
                    self.alive_cells = 0
                    self.fill_grid()
                    self.draw_grid()
                    self.display_info()
                elif self.paused and event.key == pg.K_n:
                    print("'n' pressed! - displaying next generation")
                    self.update_generation()
                    self.draw_grid()
                    self.display_info()
                elif self.paused and event.key == pg.K_c:
                    print("'c' pressed! - clearing active grid")
                    self.generation = 0
                    self.alive_cells = 0
                    self.fill_grid(0)
                    self.draw_grid()
                    self.display_info()
            elif pg.mouse.get_pressed():
                try:
                    col_row = None
                    # LMB [0] or RMB [2] pressed
                    if pg.mouse.get_pressed()[0] or pg.mouse.get_pressed()[2]:
                        col_row = self.get_col_row_by_mouse(event.pos)

                    if col_row is not None:
                        col, row = col_row

                        if pg.mouse.get_pressed()[0]:
                            if self.grids[self.active_grid][col][row] == 1:
                                return
                            self.grids[self.active_grid][col][row] = 1
                        elif pg.mouse.get_pressed()[2]:
                            if self.grids[self.active_grid][col][row] == 0:
                                return
                            self.grids[self.active_grid][col][row] = 0

                        self.draw_grid()
                        self.display_info()
                # when the mouse is pressed down and moved out of the window
                except AttributeError:
                    pass

    def run(self):
        """
        Starts the game and loops until the quit state
        """
        while True:
            if self.exit:
                pg.quit()
                return

            self.handle_events()

            if not self.paused:
                update = True

                self.draw_grid()
                self.display_info()
                self.update_generation()

                # when paused - the user is able to set or delete cells by mouse with more fps
                self.clock.tick(self.max_fps)
            elif update:
                self.draw_grid()
                self.display_info()
                update = False
