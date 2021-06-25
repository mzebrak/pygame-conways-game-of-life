import random
import sys

import pygame


class GameOfLife:

    def __init__(self, screen_width=640, screen_height=480, menu_height=50, cell_size=5, dead_color=(255, 255, 255),
                 alive_color=(0, 0, 0), max_fps=20):
        """
        Initialize screen, initialize grid, set game settings, draw first frame

        :param screen_width: Game window width
        :param screen_height: Game window height
        :param menu_height: Height for the menu
        :param cell_size: Dimension of the square
        :param dead_color: RGB tuple determining the color of dead cells and background
        :param alive_color: RGB tuple determining the color of alive cells
        :param max_fps: Framerate cap to limit the speed of the game
        """
        pygame.init()
        favicon = pygame.image.load('favicon.ico')
        pygame.display.set_icon(favicon)
        pygame.display.set_caption('conway\'s game of life')

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.menu_bar_height = menu_height
        self.cell_size = 1 if cell_size < 1 else cell_size
        self.dead_color = dead_color
        self.alive_color = alive_color
        self.max_fps = 1 if max_fps < 1 else max_fps

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.num_of_cols = int(self.screen_width / self.cell_size)
        self.num_of_rows = int((self.screen_height - self.menu_bar_height) / self.cell_size)

        self.grids = [[[0] * self.num_of_rows for _ in range(self.num_of_cols)],
                      [[0] * self.num_of_rows for _ in range(self.num_of_cols)],
                      ]
        self.active_grid = 0
        self.set_grid()

        self.generation = 0
        self.alive_cells = 0

        self.paused = False
        self.exit = False

        self.draw_grid()
        self.display_info()
        pygame.time.Clock().tick(self.max_fps)

    def set_grid(self, value=None):
        """
        Sets the entire grid to a single specified or random value
        set_grid(0)                   - all dead
        set_grid(1)                   - all alive
        set_grid() or set_grid(None)  - randomize

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
        for c in range(self.num_of_cols):
            for r in range(self.num_of_rows):
                if self.grids[self.active_grid][c][r] == 1:
                    self.alive_cells += 1
                    color = self.alive_color
                else:
                    color = self.dead_color
                pygame.draw.rect(self.screen, color,
                                 (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size))
        pygame.display.flip()

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
                c = (col + i + self.num_of_cols) % self.num_of_cols
                r = (row + j + self.num_of_rows) % self.num_of_rows
                num_of_alive_neighbors += self.grids[self.active_grid][c][r]

        num_of_alive_neighbors -= self.grids[self.active_grid][col][row]
        return num_of_alive_neighbors

    def set_cells_state(self):
        """
        Sets the (0/1) state of every cell in the inactive grid depending on the number of neighbors from the active grid
        """
        for c in range(self.num_of_cols):
            for r in range(self.num_of_rows):
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
            font = pygame.font.SysFont("Arial", int(self.menu_bar_height / div))

            text1 = font.render(f'Generation: {self.generation}', True, (0, 0, 0), (255, 255, 255))
            text2 = font.render(f'Alive cells: {self.alive_cells}', True, (0, 0, 0), (255, 255, 255))

            text1_rect = text1.get_rect()
            text2_rect = text2.get_rect()

            div += 1

            if self.screen_width > text1_rect.width + text2_rect.width:
                break

        text1_rect.topleft = (0, self.screen_height - self.menu_bar_height)
        text2_rect.topleft = (self.screen_width - text2_rect.width, self.screen_height - self.menu_bar_height)

        pygame.draw.rect(self.screen, self.dead_color,
                         (0, self.screen_height - self.menu_bar_height, self.screen_width, self.menu_bar_height))
        self.screen.blit(text1, text1_rect)
        self.screen.blit(text2, text2_rect)
        pygame.display.flip()

    def clear_screen(self):
        """
        Fill the entire screen with dead_color
        """
        self.screen.fill(self.dead_color)

    def handle_events(self):
        """
        Handle key presses

        p - toggle start/stop (pause) the game
        r - randomize grid
        n - display next generation
        c - clear grid
        q - quit
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    print("'p' pressed! - toggling pause")
                    self.paused = not self.paused
                elif event.key == pygame.K_q:
                    print("q pressed! - quitting the game")
                    self.exit = True
                elif event.key == pygame.K_r:
                    print("'r' pressed! - randomizing grid")
                    self.generation = 0
                    self.alive_cells = 0
                    self.set_grid()
                    self.draw_grid()
                    self.display_info()
                elif self.paused and event.key == pygame.K_n:
                    print("'n' pressed! - displaying next generation")
                    self.update_generation()
                    self.draw_grid()
                    self.display_info()
                elif self.paused and event.key == pygame.K_c:
                    print("'c' pressed! - clearing active grid")
                    self.generation = 0
                    self.alive_cells = 0
                    self.set_grid(0)
                    self.draw_grid()
                    self.display_info()

    def run(self):
        """
        Starts the game and loops until the quit state
        """
        while True:
            if self.exit:
                return

            self.handle_events()

            if not self.paused:
                self.update_generation()
                self.draw_grid()
                self.display_info()

            pygame.time.Clock().tick(self.max_fps)