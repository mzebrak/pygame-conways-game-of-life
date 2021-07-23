import pygame.time

from Settings import *
from Cell import Cell


class GameOfLife:
    def __init__(self, cell_size: int = CELL_SIZE, fps: int = FPS, gens_per_sec: int = START_GENS_PER_SEC,
                 width: int = WIDTH, height: int = HEIGHT, file_path: str = None):
        """
        :param cell_size: Length of the side of a square cell (px)
        :param fps: Framerate cap
        :param gens_per_sec: Limit the number of generations per second
        :param width: Screen width (has to be greater than MIN_WIDTH if set by constructor /when creating an instance or
        passing argument through cmd/ or it would be the value of WIDTH set in Settings
        :param height: Screen height - (has to be greater than MIN_HEIGHT if set by constructor /when creating an
        instance or passing argument through cmd/ or it would be the value of HEIGHT set in Settings
        """
        pg.init()
        pg.display.set_icon(pg.image.load(ICON))
        pg.display.set_caption(TITLE)
        pg.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])
        self.cell_size = CELL_SIZE if not MIN_CELL_SIZE <= cell_size <= MAX_CELL_SIZE else cell_size
        self.fps = FPS if fps < 1 else fps
        self.gens_per_sec = START_GENS_PER_SEC if not MIN_GENS_PER_SEC <= gens_per_sec <= MAX_GENS_PER_SEC else gens_per_sec
        self.width = MIN_WIDTH if width < MIN_WIDTH else width
        self.height = HEIGHT if height == 0 else height if height > MIN_HEIGHT else MIN_HEIGHT
        self.screen = pg.display.set_mode([self.width, self.height], HWSURFACE | DOUBLEBUF | RESIZABLE)
        self.clock = pg.time.Clock()
        self.new_gen_event = pg.USEREVENT + 1
        pg.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))
        self.dead_color = next(COLORS_CYCLE)
        self.sprites = self.grid_width = self.grid_height = self.margin_x = self.grid_image = self.cells = \
            self.generation = self.font_info = self.font_help = self.f1_menu_width = self.f1_line_height = None
        self.show_route = False
        self.show_grid = True
        self.show_menu = True
        self.paused = True
        file_path and self.load_from_file(file_path)
        self.new(file=file_path)

    def load_from_file(self, file: str):
        """
        Load grid from the specified file
        :param file: relative path to the file
        """
        try:
            with open(file) as f:
                content = [[int(c) for c in line.strip()] for line in f]
        except FileNotFoundError:
            print(f'File \'{file}\' was not found!')
            quit()

        lengths = [len(row) for row in content]
        max_len = max(lengths)
        for row in content:
            diff = max_len-len(row)
            row.extend([0] * diff) if diff > 0 else 0

        content = list(map(list, zip(*content)))
        self.generation = 0
        self.sprites = pg.sprite.Group()
        self.cell_size = int(min(self.width / len(content), (self.height - MENU_HEIGHT) / len(content[0])))
        if self.cell_size < MIN_CELL_SIZE:
            print(f'Cell size is too small: \'{self.cell_size}\'. Change minimum value or modify number of rows/cols!')
            quit()

        self.grid_width = int(self.width / self.cell_size)
        self.grid_height = int((self.height - MENU_HEIGHT) / self.cell_size)
        # adding cols and rows to center loaded pattern
        [content.insert(0, [0] * len(content[0])) for _ in range((self.grid_width - len(content)) // 2)]
        [[content[x].insert(0, 0) for _ in range((self.grid_height - len(content[-1])) // 2)] for x in
         range(len(content))]

        self.cells = [[Cell(self, self.cell_size, x, y, color=BLACK, alive=True)
                       if x < len(content) and y < len(content[0]) and content[x][y]
                       else Cell(self, self.cell_size, x, y, color=WHITE)
                       for y in range(self.grid_height)] for x in range(self.grid_width)]

    def new(self, action: str = None, file: str = None):
        """
        Called when it is necessary to recreate the grid
        :param action: This parameter is just passed to the create_list function
        :param file: path to the pattern file or None
        """
        if not file:
            self.sprites = pg.sprite.Group()
            self.grid_width = int(self.width / self.cell_size)
            self.grid_height = int((self.height - MENU_HEIGHT) / self.cell_size)
            self.create_list(action)
        self.margin_x = int((self.width - self.grid_width * self.cell_size) / 2)
        self.grid_image = pg.Surface((self.grid_width * self.cell_size + 1, self.grid_height * self.cell_size + 1))
        self.calculate_font_sizes()
        self.screen.fill(WHITE)  # when size changed there might be black stripe

    def create_list(self, action: str = None):
        """
        Creates a list of Cell type objects, depending on the action - the old list could be copied
        :param action: 'DECREASE'- when new grid will be smaller, 'INCREASE' - when new grid will be
        bigger or None/else if there si no need to copy Cell states of the old grid.
        """
        if action == 'INCREASE':
            # extend the existing list by copying cells from the old list and adding new dead cells to the rest of
            # the indexes
            self.cells = [[Cell(self, self.cell_size, x, y, color=self.cells[x][y].color, alive=self.cells[x][y].alive)
                           if x < len(self.cells) and y < len(self.cells[0])
                           else Cell(self, self.cell_size, x, y, color=WHITE)
                           for y in range(self.grid_height)] for x in range(self.grid_width)]
        elif action == 'DECREASE':
            # copy bigger list to the smaller one (so copies only cells which will fit into the new one) - by new lower
            # indexes - grid_width and grid_height
            self.cells = [[Cell(self, self.cell_size, x, y, color=self.cells[x][y].color, alive=self.cells[x][y].alive)
                           for y in range(self.grid_height)] for x in range(self.grid_width)]
        else:
            # just create new list of cells with random states
            self.cells = [[Cell(self, self.cell_size, x, y) for y in range(self.grid_height)]
                          for x in range(self.grid_width)]
            self.fill_grid()

    def fill_grid(self, value: int = None):
        """
        Sets the entire grid to a single specified / random values
        fill_grid(0)                   - all dead
        fill_grid(1)                   - all alive
        fill_grid() or fill_grid(None)  - randomize
        :param value:  Value to set the cell to (0 or 1)
        """
        self.generation = 0
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if value is None:
                    self.cells[x][y].revive() if choice([0, 1]) == 1 else self.cells[x][y].kill()
                elif value == 0:
                    self.cells[x][y].kill()
                elif value == 1:
                    self.cells[x][y].revive()

    def calculate_font_sizes(self):
        text_bottom = 'Generation: XXXXXX  Alive cells: XXXXXX'
        text_help = 't :  switch cell sizes xxx x xxx (xxxxxx)'

        size = MENU_HEIGHT
        while True:
            self.font_info = pg.font.SysFont(FONT, int(size))
            text_width, text_height = self.font_info.size(text_bottom)
            if text_width < self.width and text_height < MENU_HEIGHT:
                break
            size -= 1

        div = 2
        while True:
            self.font_help = pg.font.SysFont(FONT_MENU, int(self.height / div))
            self.f1_menu_width, self.f1_line_height = self.font_help.size(text_help)
            if self.f1_menu_width < self.width / 3 and self.f1_line_height * 17 < self.height * 5 / 8:
                break
            div += 1

    def draw_grid(self):
        """
        Draw the additional grid/net
        """
        width, height = self.grid_width * self.cell_size, self.grid_height * self.cell_size
        for x in range(0, width, self.cell_size):
            pg.draw.line(self.grid_image, GREY, (x, 0), (x, height))
        for y in range(0, height, self.cell_size):
            pg.draw.line(self.grid_image, GREY, (0, y), (width, y))

    def draw_info(self, color=BLACK, background=WHITE):
        """
        Displaying information about generation and alive cells
        :param color: color of the drawn text
        :param background: color of the drawn background
        """
        render = lambda txt: self.font_info.render(txt, False, color, background)

        text = render(f'Generation: {self.generation}')
        text2 = render(f'Alive cells: {self.count_alive_cells()}')
        pg.draw.rect(self.screen, WHITE, (0, self.height - MENU_HEIGHT + 1, self.width, MENU_HEIGHT))
        self.screen.blits([(text, (0, self.height - MENU_HEIGHT + 1)),
                           (text2, (self.width - text2.get_size()[0], self.height - MENU_HEIGHT + 1))])

    def draw_menu(self, color=BLACK, background=WHITE + (222,)):
        """
        A function that draws the menu available under the f1 button
        :param color:  color of the drawn text
        :param background: color of the drawn background
        """
        blit_line = lambda pos, text: \
            menu_bg.blit(self.font_help.render(text, False, color), (5, self.f1_line_height * pos))

        menu_bg = pg.Surface([self.f1_menu_width, self.f1_line_height * 17], pg.SRCALPHA)
        menu_bg.fill(background)

        color_names = {WHITE: 'WHITE',
                       LIGHTEST_GREY: 'LIGHTEST GREY',
                       LIGHTER_GREY: 'LIGHTER GREY',
                       LIGHT_GREY: 'LIGHT GREY'}

        blit_line(0, f'{TITLE}      FPS:{round(self.clock.get_fps())}')
        blit_line(2, f'F1:  show / hide menu')
        blit_line(3, f'g :  show / hide grid ({"shown" if self.show_grid else "hidden"})')
        blit_line(4, f'w :  show / hide route ({"shown" if self.show_route else "hidden"})')
        blit_line(5, f'e :  next color for dead cells')
        blit_line(6, f'      ({color_names[self.dead_color]})')
        blit_line(7, f'p :  run / pause ({"paused" if self.paused else "running"})')
        blit_line(8, f'r :  randomize grid')
        blit_line(9, f'n :  display next generation')
        blit_line(10,
                  f't :  switch cell sizes {self.grid_width}x{self.grid_height} ({self.grid_width * self.grid_height})')
        blit_line(11, f'z | x :  adjust cell sizes ({self.cell_size})')
        blit_line(12, f', | . :  generations per second ({self.gens_per_sec})')
        blit_line(13, f'LMB :  set cell as alive')
        blit_line(14, f'RMB :  set cell as dead')
        blit_line(15, f'q :  quit')

        self.grid_image.blit(menu_bg, (0, 0))

    def draw(self):
        """
        A function that draws everything on the screen - sprites, grid, help menu and info
        """
        self.sprites.draw(self.grid_image)
        self.show_grid and self.draw_grid()
        self.show_menu and self.draw_menu()
        self.screen.blit(self.grid_image, (self.margin_x, 0))
        self.draw_info()
        pg.display.flip()

    def count_alive_cells(self) -> int:
        """
        Returns the number of cells currently alive
        """
        return sum(sum(1 for cell in x if cell.alive) for x in self.cells)

    def count_cell_neighbors(self, x: int, y: int) -> int:
        """
        Get the number of alive neighbors of the specific cell
        :param x: The index of the specific cell
        :param y: The index of the specific cell
        :return: The number of alive neighbors of that cell
        """
        prev_x = x - 1
        prev_y = y - 1
        next_x = (x + 1) % self.grid_width
        next_y = (y + 1) % self.grid_height
        return self.cells[prev_x][prev_y].alive + self.cells[prev_x][y].alive + self.cells[prev_x][next_y].alive + \
               self.cells[x][prev_y].alive + self.cells[x][next_y].alive + \
               self.cells[next_x][prev_y].alive + self.cells[next_x][y].alive + self.cells[next_x][next_y].alive

    def set_cells_state(self):
        """
        Sets the state of every cell depending on the number of neighbors
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

        # revive / kill cell depending on the boolean in temp list
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if temp[x][y]:
                    self.cells[x][y].survive() if self.cells[x][y].alive else self.cells[x][y].revive(BLACK)
                else:
                    if self.cells[x][y].alive:
                        self.cells[x][y].kill(self.dead_color) if self.show_route else self.cells[x][y].kill()

    def update_generation(self):
        """
        Calls function which set the state of every cell in next generation, then increments the generation counter
        """
        self.set_cells_state()
        self.generation += 1

    def compute_mouse_pos(self, pos: (int, int)) -> (int, int):
        """
        A function that calculates the tuple (col, row) of the clicked cell depending on the mouse position
        :param pos: Position in px where the mouse was when clicked
        :return: (None, None) if clicked not on the grid otherwise tuple (col, row)
        """
        # only if clicked above menu bar (on the grid image)
        if self.margin_x < pos[0] < (self.grid_width * self.cell_size + self.margin_x):
            if 0 < pos[1] < (self.grid_height * self.cell_size):
                return ((pos[0] - self.margin_x) // self.cell_size), (pos[1] // self.cell_size)
        return None, None

    def handle_keys(self, event: pg.event.Event):
        """
        g - toggle on/off grid
        p - toggle start/stop (pause) the game
        w - toggle route view
        e - next color for dead cells
        t - switch between cell sizes
        z - decrease cell size
        x - increase cell size
        n - display next generation
        r - randomize grid
        c - clear grid
        q - quit
        :param event: pygame Event
        """
        if event.key == pg.K_p:
            print("'p' pressed! - toggling pause")
            self.paused = not self.paused
        elif event.key == pg.K_q:
            print("'q' pressed! - quitting the game")
            self.quit()
        elif event.key == pg.K_r:
            print("'r' pressed! - randomizing grid")
            self.fill_grid()
        elif event.key == pg.K_w:
            print("'w' pressed! - toggling route view")
            self.show_route = not self.show_route
        elif event.key == pg.K_e:
            print("'e' pressed! - next color for dead cells")
            self.dead_color = next(COLORS_CYCLE)
        elif self.paused and event.key == pg.K_n:
            print("'n' pressed! - displaying next generation")
            self.update_generation()
        elif event.key == pg.K_c:
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
            self.increase_cell_size()
        elif event.key == pg.K_z:
            print("'z' pressed! - cell size decreased")
            self.decrease_cell_size()
        elif event.key == pg.K_F1:
            print("'F1' pressed! - toggling menu view")
            self.show_menu = not self.show_menu
        elif event.unicode == ",":
            print("',' pressed! - generations per second decreased")
            self.decrease_gens_per_sec()
        elif event.unicode == ".":
            print("'.' pressed! - generations per second increased")
            self.increase_gens_per_sec()

    def handle_mouse_scroll(self, button: int, zoom: bool = False):
        if button == WHEEL_UP:
            if zoom:
                print("'CTRL' and 'WHEEL_UP'! -cell size increased")
                self.increase_cell_size()
            else:
                print("'WHEEL_UP'! - generations per second increased")
                self.increase_gens_per_sec()
        elif button == WHEEL_DOWN:
            if zoom:
                print("'CTRL' and 'WHEEL_DOWN'! -cell size decreased")
                self.decrease_cell_size()
            else:
                print("'WHEEL_DOWN'! - generations per second decreased")
                self.decrease_gens_per_sec()

    def handle_mouse_buttons(self, event: pg.event.Event, button: (bool, bool, bool)) -> bool:
        """
        LMB - pressed or held sets cell alive
        RMB - pressed or held sets cell dead
        :param event: pygame Event
        :param button: tuple of booleans
        """
        col, row = None, None
        try:
            col, row = self.compute_mouse_pos(event.pos)
        except AttributeError:  # when the mouse is pressed down and moved out of the window
            pass

        if col is None:
            return False

        state = self.cells[col][row].alive
        if button[LMB] and not state:
            self.cells[col][row].revive()
        elif button[RMB] and state:
            self.cells[col][row].kill()
        else:
            return False
        return True

    def handle_events(self):
        """
        Handle all of the events
        """
        for event in pg.event.get():
            if event.type == self.new_gen_event and not self.paused:
                self.update_generation()
            elif event.type == QUIT:
                self.quit()
            elif event.type == VIDEORESIZE:
                width_before, height_before = self.width, self.height
                self.width = MIN_WIDTH if event.w < MIN_WIDTH else event.w
                self.height = MIN_HEIGHT if event.h < MIN_HEIGHT else event.h
                self.screen = pg.display.set_mode((self.width, self.height), HWSURFACE | DOUBLEBUF | RESIZABLE)
                (width_before < self.width or height_before < self.height) and self.new(action="INCREASE")
                (width_before > self.width or height_before > self.grid_height) and self.new(action="DECREASE")
            elif event.type == KEYDOWN:
                self.handle_keys(event)
            elif (keys := pg.key.get_pressed()) and (keys[pg.K_LCTRL] or keys[pg.K_RCTRL]):
                if event.type == MOUSEBUTTONDOWN and (event.button == WHEEL_DOWN or event.button == WHEEL_UP):
                    self.handle_mouse_scroll(event.button, zoom=True)
                    continue
            elif button := pg.mouse.get_pressed(num_buttons=3):
                if event.type == MOUSEBUTTONDOWN and (event.button == WHEEL_DOWN or event.button == WHEEL_UP):
                    self.handle_mouse_scroll(event.button)
                if not self.handle_mouse_buttons(event, button):
                    continue

    def increase_gens_per_sec(self):
        self.gens_per_sec += CHANGE_GENS_PER_SEC if self.gens_per_sec <= (MAX_GENS_PER_SEC - CHANGE_GENS_PER_SEC) else 0
        pg.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))

    def decrease_gens_per_sec(self):
        self.gens_per_sec -= CHANGE_GENS_PER_SEC if self.gens_per_sec >= (MIN_GENS_PER_SEC + CHANGE_GENS_PER_SEC) else 0
        pg.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))

    def increase_cell_size(self):
        self.cell_size += CHANGE_CELL_SIZE if self.cell_size <= (MAX_CELL_SIZE - CHANGE_CELL_SIZE) else 0
        self.new(action='DECREASE')

    def decrease_cell_size(self):
        self.cell_size -= CHANGE_CELL_SIZE if self.cell_size >= (MIN_CELL_SIZE + CHANGE_CELL_SIZE) else 0
        self.new(action='INCREASE')

    @staticmethod
    def quit():
        pg.quit()
        exit()

    def run(self):
        """
        Starts the game and loops until the quit state
        """
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(self.fps)
