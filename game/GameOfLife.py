from Settings import *
from Cell import Cell


class GameOfLife:
    def __init__(self, cell_size: int = CELL_SIZE, fps: int = FPS, gens_per_sec: int = START_GENS_PER_SEC,
                 width: int = WIDTH, height: int = HEIGHT, file: str = None):
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
        self.gens_per_sec = START_GENS_PER_SEC if not MIN_GENS_PER_SEC <= gens_per_sec <= MAX_GENS_PER_SEC \
            else gens_per_sec
        self.width = MIN_WIDTH if width < MIN_WIDTH else width
        self.height = HEIGHT if height == 0 else height if height > MIN_HEIGHT else MIN_HEIGHT
        self.screen = pg.display.set_mode([self.width, self.height], HWSURFACE | DOUBLEBUF | RESIZABLE)
        self.clock = pg.time.Clock()
        self.new_gen_event = pg.USEREVENT + 1
        pg.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))
        self.dead_color = next(DEAD_COLOR)
        self.grid_color = next(GRID_COLOR)
        self.sprites = self.grid_width = self.grid_height = self.margin_x = self.grid_image = self.cells = \
            self.generation = self.font_info = self.font_help = self.grid_lines = None
        self.f1_menu_width = self.f1_line_height = 0
        self.show_route = False
        self.show_menu = True
        self.paused = True
        self.calculate_font_sizes()
        file and self.load_from_file(file)
        self.new(file=file)

    def load_from_file(self, file: str):
        """
        Load grid from the specified file
        :param file: relative path from __main__.py to the file
        """
        try:
            with open(file) as f:
                content = [[True if c in ('1', 'o', 'O') else False if c in ('0', '.', '_') else quit(
                    f"there is an illegal character '{c}' in the '{file}' file") for c in line.strip()] for line in f]
        except FileNotFoundError:
            quit(f"File '{file}' was not found!")

        lengths = [len(row) for row in content]
        max_len = max(lengths)
        for row in content:
            diff = max_len - len(row)
            row.extend([False] * diff) if diff > 0 else None

        content = list(map(list, zip(*content)))  # from [y][x] to [x][y]

        self.cell_size = int(min(self.width / len(content), (self.height - MENU_HEIGHT) / len(content[0])))
        if self.cell_size < MIN_CELL_SIZE:
            quit(f"Cell size is too small: '{self.cell_size}' change min: '{MIN_CELL_SIZE} or modify num of rows/cols!")

        self.grid_width = int(self.width / self.cell_size)
        self.grid_height = int((self.height - MENU_HEIGHT) / self.cell_size)
        # adding cols and rows to center loaded pattern
        [content.insert(0, [False] * len(content[0])) for _ in range((self.grid_width - len(content)) // 2)]
        [[content[x].insert(0, False) for _ in range((self.grid_height - len(content[-1])) // 2)] for x in
         range(len(content))]

        self.generation = 0
        self.sprites = pg.sprite.Group()
        self.cells = [[Cell(self, self.cell_size, x, y, color=BLACK, alive=True)
                       if x < len(content) and y < len(content[0]) and content[x][y]
                       else Cell(self, self.cell_size, x, y, color=WHITE)
                       for y in range(self.grid_height)] for x in range(self.grid_width)]

    def save_to_file(self) -> str:
        """
        Create a file to which the current grid will be saved
        :return: name of the created file
        """
        Path(SAVES).mkdir(parents=True, exist_ok=True)
        filename = SAVES + datetime.now().strftime('%Y-%m-%dT%H-%M-%S-%f')[:-3] + ".txt"
        with open(filename, 'w') as f:
            for y in range(len(self.cells[0])):
                for x in range(len(self.cells)):
                    f.write('1' if self.cells[x][y].alive else '.')
                f.write('\n')
        return filename

    def new(self, action: Action = Action.INIT, file: str = None):
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
        self.grid_image = pg.Surface([self.grid_width * self.cell_size + 1, self.grid_height * self.cell_size + 1])
        self.draw_grid(self.grid_color)
        self.grid_image.fill(WHITE)
        self.screen.fill(WHITE)  # when size changed there might be black stripe

    def create_list(self, action: Action):
        """
        Creates a list of Cell type objects, depending on the action - the old list could be copied
        :param action: DECREASE- when new grid will be smaller, INCREASE - when new grid will be
                        bigger or INIT if there is no need to copy Cell states of the old grid.
        """
        if action is Action.INIT:
            # just create new list of cells with random states
            self.cells = [[Cell(self, self.cell_size, x, y) for y in range(self.grid_height)]
                          for x in range(self.grid_width)]
            self.fill_grid()
        elif action is Action.INCREASE:
            # extend the existing list by copying cells from the old list and adding new dead cells to the rest of
            # the indexes
            self.cells = [[Cell(self, self.cell_size, x, y, color=self.cells[x][y].color, alive=self.cells[x][y].alive)
                           if x < len(self.cells) and y < len(self.cells[0])
                           else Cell(self, self.cell_size, x, y, color=WHITE)
                           for y in range(self.grid_height)] for x in range(self.grid_width)]
        elif action is Action.DECREASE:
            # copy bigger list to the smaller one (so copies only cells which will fit into the new one) - by new lower
            # indexes - grid_width and grid_height
            self.cells = [[Cell(self, self.cell_size, x, y, color=self.cells[x][y].color, alive=self.cells[x][y].alive)
                           for y in range(self.grid_height)] for x in range(self.grid_width)]

    def fill_grid(self, action: Action = Action.RANDOMIZE):
        """
        Sets the entire grid to a single specified / random values
        fill_grid(Action.RANDOMIZE)     - randomize
        fill_grid(Action.CLEAR)         - set all cells dead
        :param action:
        """
        self.generation = 0
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if action is Action.RANDOMIZE:
                    self.cells[x][y].revive() if choice([0, 1]) == 1 else self.cells[x][y].kill()
                elif action is Action.CLEAR:
                    self.cells[x][y].kill()

    def calculate_font_sizes(self):
        text_bottom = 'Generation: XXXXXX  Alive cells: XXXXXX'
        text_help = 't :  switch cell sizes xxx x xxx (xxxxxx)'

        size = MENU_HEIGHT
        while True:
            self.font_info = pg.font.SysFont(FONT, size)
            text_width, text_height = self.font_info.size(text_bottom)
            if text_width < self.width and text_height < MENU_HEIGHT:
                break
            size -= 1

        size = int(self.height * 6 / 8 / 18)
        while True:
            self.font_help = pg.font.SysFont(FONT_MENU, size)
            self.f1_menu_width, self.f1_line_height = self.font_help.size(text_help)
            if self.f1_menu_width < self.width / 3 and self.f1_line_height * 18 < self.height * 6 / 8:
                break
            size -= 1

    def draw_grid(self, color=GREY):
        """
        Draw the additional grid/net
        :param color: color of the drawn lines
        """
        self.grid_lines = pg.Surface([self.grid_width * self.cell_size + 1, self.grid_height * self.cell_size + 1],
                                     SRCALPHA)
        self.grid_lines.fill(WHITE + (0,))
        width, height = self.grid_width * self.cell_size, self.grid_height * self.cell_size

        pg.draw.lines(self.grid_lines, GREY, True, ((0, 0), (width, 0), (width, height), (0, height)))  # border
        if color is None:
            return

        for x in range(self.cell_size, width, self.cell_size):
            pg.draw.line(self.grid_lines, color, (x, 1), (x, height - 1))
        for y in range(self.cell_size, height, self.cell_size):
            pg.draw.line(self.grid_lines, color, (1, y), (width - 1, y))

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

        menu_bg = pg.Surface([self.f1_menu_width, self.f1_line_height * 18], SRCALPHA)
        menu_bg.fill(background)

        dead_colors = {WHITE: 'WHITE',
                       LIGHTEST_GREY: 'LIGHTEST GREY',
                       LIGHTER_GREY: 'LIGHTER GREY',
                       LIGHT_GREY: 'LIGHT GREY'}
        grid_colors = {None: 'hidden',
                       GREY: 'GREY',
                       WHITE: 'WHITE'
                       }

        blit_line(0, f'{TITLE}      FPS:{round(self.clock.get_fps())}')
        blit_line(2, f'F1:  show / hide menu')
        blit_line(3, f'g :  show / hide grid ({grid_colors[self.grid_color]})')
        blit_line(4, f'w :  show / hide route ({"shown" if self.show_route else "hidden"})')
        blit_line(5, f'e :  next color for dead cells')
        blit_line(6, f'      ({dead_colors[self.dead_color]})')
        blit_line(7, f'p :  run / pause ({"paused" if self.paused else "running"})')
        blit_line(8, f's :  save grid to a file')
        blit_line(9, f'r :  randomize grid')
        blit_line(10, f'n :  display next generation')
        blit_line(11,
                  f't :  switch cell sizes {self.grid_width}x{self.grid_height} ({self.grid_width * self.grid_height})')
        blit_line(12, f'z | x :  adjust cell sizes ({self.cell_size})')
        blit_line(13, f', | . :  generations per second ({self.gens_per_sec})')
        blit_line(14, f'LMB :  set cell as alive')
        blit_line(15, f'RMB :  set cell as dead')
        blit_line(16, f'q :  quit')

        self.grid_image.blit(menu_bg, (0, 0))

    def draw(self):
        """
        A function that draws everything on the screen - sprites, grid, help menu and info
        """
        self.sprites.draw(self.grid_image)
        self.grid_image.blit(self.grid_lines, (0, 0))
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
        This function handles all the events related to the keyboard
        :param event: pygame Event
        """
        if event.key == pg.K_p:
            print("'p' pressed! - toggling pause")
            self.paused = not self.paused
        elif event.key == pg.K_q:
            quit("'q' pressed! - quitting the game")
        elif event.key == pg.K_r:
            print("'r' pressed! - randomizing grid")
            self.fill_grid()
        elif event.key == pg.K_w:
            print("'w' pressed! - toggling route view")
            self.show_route = not self.show_route
        elif event.key == pg.K_e:
            print("'e' pressed! - next color for dead cells")
            self.dead_color = next(DEAD_COLOR)
        elif self.paused and event.key == pg.K_n:
            print("'n' pressed! - displaying next generation")
            self.update_generation()
        elif event.key == pg.K_c:
            print("'c' pressed! - clearing grid")
            self.fill_grid(Action.CLEAR)
        elif event.key == pg.K_t:
            print("'t' pressed! - changing cell size")
            self.cell_size = next(CELL_SIZES)
            self.new()
        elif event.key == pg.K_g:
            print("'g' pressed! - toggling grid")
            self.grid_color = next(GRID_COLOR)
            self.draw_grid(self.grid_color)
        elif event.key == pg.K_x:
            self.increase_cell_size()
        elif event.key == pg.K_z:
            self.decrease_cell_size()
        elif event.key == pg.K_F1:
            print("'F1' pressed! - toggling menu view")
            self.show_menu = not self.show_menu
        elif event.key == pg.K_s:
            print(f"'s' pressed ! - saved to file  '{self.save_to_file()}'")
        elif event.unicode == ',':
            self.decrease_gens_per_sec()
        elif event.unicode == '.':
            self.increase_gens_per_sec()

    def handle_mouse_scroll(self, button: int, ctrl: bool = False):
        """
        This function handles all the events related to the mouse scroll
        :param button: scrolling up / down
        :param ctrl: if True then CTRL is also pressed and it should zoom instead of changing gens per sec
        """
        if button == WHEEL_UP:
            self.increase_cell_size() if ctrl else self.increase_gens_per_sec()
        elif button == WHEEL_DOWN:
            self.decrease_cell_size() if ctrl else self.decrease_gens_per_sec()

    def handle_mouse_buttons(self, event: pg.event.Event, button: (bool, bool, bool)):
        """
        This function handles all the events related to the mouse buttons
        :param event: pygame Event
        :param button: tuple of booleans
        """
        col, row = None, None
        try:
            col, row = self.compute_mouse_pos(event.pos)
        except AttributeError:  # when the mouse is pressed down and moved out of the window
            pass

        if col is None:
            return

        state = self.cells[col][row].alive
        if button[LMB] and not state:
            self.cells[col][row].revive()
        elif button[RMB] and state:
            self.cells[col][row].kill()

    def handle_events(self):
        """
        Handle all of the events
        """
        for event in pg.event.get():
            if event.type == self.new_gen_event and not self.paused:
                self.update_generation()
            elif event.type == QUIT:
                quit("App window was closed!")
            elif event.type == VIDEORESIZE:
                width_before, height_before = self.width, self.height
                self.width = MIN_WIDTH if event.w < MIN_WIDTH else event.w
                self.height = MIN_HEIGHT if event.h < MIN_HEIGHT else event.h
                self.screen = pg.display.set_mode((self.width, self.height), HWSURFACE | DOUBLEBUF | RESIZABLE)
                (width_before < self.width or height_before < self.height) and self.new(action=Action.INCREASE)
                (width_before > self.width or height_before > self.grid_height) and self.new(action=Action.DECREASE)
                self.calculate_font_sizes()
            elif event.type == KEYDOWN:
                self.handle_keys(event)
            elif (keys := pg.key.get_pressed()) and (keys[pg.K_LCTRL] or keys[pg.K_RCTRL]):
                if event.type == MOUSEBUTTONDOWN and (event.button == WHEEL_DOWN or event.button == WHEEL_UP):
                    self.handle_mouse_scroll(event.button, ctrl=True)
                    continue
            elif button := pg.mouse.get_pressed(num_buttons=3):
                if event.type == MOUSEBUTTONDOWN and (event.button == WHEEL_DOWN or event.button == WHEEL_UP):
                    self.handle_mouse_scroll(event.button)
                self.handle_mouse_buttons(event, button)

    def increase_gens_per_sec(self):
        if self.gens_per_sec <= (MAX_GENS_PER_SEC - CHANGE_GENS_PER_SEC):
            print('Generations per second increased!')
            self.gens_per_sec += CHANGE_GENS_PER_SEC
            pg.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))

    def decrease_gens_per_sec(self):
        if self.gens_per_sec >= (MIN_GENS_PER_SEC + CHANGE_GENS_PER_SEC):
            print('Generations per second decreased!')
            self.gens_per_sec -= CHANGE_GENS_PER_SEC
            pg.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))

    def increase_cell_size(self):
        if self.cell_size <= (MAX_CELL_SIZE - CHANGE_CELL_SIZE):
            print('Cell size increased!')
            self.cell_size += CHANGE_CELL_SIZE
            self.new(action=Action.DECREASE)

    def decrease_cell_size(self):
        if self.cell_size >= (MIN_CELL_SIZE + CHANGE_CELL_SIZE):
            print('Cell size decreased!')
            self.cell_size -= CHANGE_CELL_SIZE
            self.new(action=Action.INCREASE)

    def run(self):
        """
        Starts the game and loops until the quit state
        """
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(self.fps)
