from Settings import *
from Cell import Cell


class GameOfLife:
    def __init__(self, cell_size: int = 0, fps: int = 0):
        """
        :param cell_size: Dimensions of the Cell
        :param fps: Framerate cap to limit the speed of the game
        """
        pg.init()
        pg.display.set_icon(pg.image.load(ICON))
        pg.display.set_caption(TITLE)
        pg.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])
        self.width, self.height = WIDTH, HEIGHT
        self.screen = pg.display.set_mode([self.width, self.height], HWSURFACE | DOUBLEBUF | RESIZABLE)
        self.cell_size = CELL_SIZE if cell_size < 8 else cell_size
        self.fps = FPS if fps < 1 else fps
        self.clock = pg.time.Clock()
        self.gens_per_sec = START_GENS_PER_SEC
        self.new_gen_event = pg.USEREVENT + 1
        pg.time.set_timer(self.new_gen_event, int(1000 / START_GENS_PER_SEC))
        self.new()
        self.paused = False
        self.show_route = False
        self.show_grid = True
        self.show_menu = True

    def new(self, action: str = None):
        """
        When it is necessary to recreate the grid
        :param action: 'INCREASED' - when new grid will be smaller, 'DECREASED' - when new grid will be bigger or
         None/else, just passing it to the create_list function
        """
        self.sprites = pg.sprite.Group()
        self.grid_width = int(self.width / self.cell_size)
        self.grid_height = int((self.height - MENU_HEIGHT) / self.cell_size)
        self.margin_x = int((self.width - self.grid_width * self.cell_size) / 2)
        self.grid_image = pg.Surface((self.grid_width * self.cell_size + 1, self.grid_height * self.cell_size + 1))
        self.create_list(action)
        self.calculate_font_sizes()
        self.screen.fill(WHITE)  # when size changed there might be black stripe

    def create_list(self, action: str = None):
        """
        Creates a list of Cell type objects, depending on the action - the old list could be copied
        :param action: INCREASED' - when new grid will be smaller, 'DECREASED' - when new grid will be bigger or None/else
        """
        if action == 'DECREASED':
            # extend the existing list by copying cells from the old list and adding new dead cells to the rest of
            # the indexes
            self.cells = [[Cell(self, self.cell_size, x, y, alive=self.cells[x][y].alive, color=self.cells[x][y].color)
                           if x < len(self.cells) and y < len(self.cells[0])
                           else Cell(self, self.cell_size, x, y, alive=False, color=WHITE)
                           for y in range(self.grid_height)] for x in range(self.grid_width)]

        elif action == 'INCREASED':
            # copy bigger list to the smaller one (so copies only cells which will fit into the new one) - by new lower
            # indexes - grid_width and grid_height
            self.cells = [[Cell(self, self.cell_size, x, y, alive=self.cells[x][y].alive, color=self.cells[x][y].color)
                           for y in range(self.grid_height)] for x in range(self.grid_width)]

        else:
            # just create new list of cells with random states
            self.cells = [[Cell(self, self.cell_size, x, y) for y in range(self.grid_height)]
                          for x in range(self.grid_width)]
            self.fill_grid()

    def fill_grid(self, value: int = None):
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
            self.font = pg.font.SysFont(FONT, int(size))
            text_width, text_height = self.font.size(text_bottom)
            if text_width < self.width and text_height < MENU_HEIGHT:
                break
            size -= 1

        div = 2
        while True:
            self.font_menu = pg.font.SysFont(FONT_MENU, int(self.height / div))
            self.f1_menu_width, self.f1_line_height = self.font_menu.size(text_help)
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
        """
        render = lambda txt: self.font.render(txt, False, color, background)
        self.count_alive_cells()
        text = render(f'Generation: {self.generation}')
        text2 = render(f'Alive cells: {self.alive_cells}')
        pg.draw.rect(self.screen, WHITE, (0, self.height - MENU_HEIGHT + 1, self.width, MENU_HEIGHT))
        self.screen.blits([(text, (0, self.height - MENU_HEIGHT + 1)),
                           (text2, (self.width - text2.get_size()[0], self.height - MENU_HEIGHT + 1))])

    def draw_menu(self, color=BLACK):
        blit_line = lambda pos, text: \
            self.grid_image.blit(self.font_menu.render(text, False, color), (5, self.f1_line_height * pos))

        menu_bg = pg.Surface([self.f1_menu_width, self.f1_line_height * 17], pg.SRCALPHA)
        menu_bg.fill(WHITE + (222,))
        self.grid_image.blit(menu_bg, (0, 0))

        color_names = {WHITE: 'WHITE',
                       LIGHTEST_GREY: 'LIGHTEST GREY',
                       LIGHTER_GREY: 'LIGHTER GREY',
                       LIGHT_GREY: 'LIGHT GREY'}

        blit_line(0, f'{TITLE}      FPS:{int(self.clock.get_fps())}')
        blit_line(2, f'F1:  show / hide menu')
        blit_line(3, f'g :  show / hide grid ({"shown" if self.show_grid else "hidden"})')
        blit_line(4, f'w :  show / hide route ({"shown" if self.show_route else "hidden"})')
        blit_line(5, f'e :  next color for dead cells')
        blit_line(6, f'      ({color_names[DEAD_COLOR]})')
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

    def draw(self):
        """
        A function that draws everything on the screen - sprites, grid and info
        """
        self.sprites.draw(self.grid_image)
        self.show_grid and self.draw_grid()
        self.show_menu and self.draw_menu()
        self.screen.blit(self.grid_image, (self.margin_x, 0))
        self.draw_info()
        pg.display.flip()

    def count_alive_cells(self):
        """
        Sets the number of cells currently alive
        """
        self.alive_cells = sum(sum(1 for cell in x if cell.alive) for x in self.cells)

    def count_cell_neighbors(self, x: int, y: int) -> int:
        """
        Get the number of alive neighbors of a specific cell
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
                        self.cells[x][y].kill(DEAD_COLOR) if self.show_route else self.cells[x][y].kill()

    def update_generation(self):
        """
        Calls function which set the state of every cell in next generation, then increments the generation counter
        """
        self.set_cells_state()
        self.generation += 1

    def compute_mouse_pos(self, pos: (int, int)):
        """
        A function that gets the tuple (col, row) of the clicked cell
        :param pos: Position in px where the mouse was when clicked
        :return: (None, None) if clicked not on the grid otherwise tuple (col, row)
        """
        # only if clicked above menu bar (on the grid image)
        if self.margin_x < pos[0] < (self.grid_width * self.cell_size + self.margin_x):
            if 0 < pos[1] < (self.grid_height * self.cell_size):
                return ((pos[0] - self.margin_x) // self.cell_size), (pos[1] // self.cell_size)
        return None, None

    def handle_keys(self, event):
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
        :param event:
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
            global DEAD_COLOR
            print("'e' pressed! - next color for dead cells")
            DEAD_COLOR = next(COLORS_CYCLE)
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
            self.cell_size += 2 if self.cell_size <= 98 else 0
            self.new(action='INCREASED')
        elif event.key == pg.K_z:
            print("'z' pressed! - cell size decreased")
            self.cell_size -= 2 if self.cell_size >= 10 else 0
            self.new(action='DECREASED')
        elif event.key == pg.K_F1:
            print("'F1' pressed! - toggling menu view")
            self.show_menu = not self.show_menu
        elif event.unicode == ",":
            print("',' pressed! - generations per second decreased")
            self.decrease_gens_per_sec()
        elif event.unicode == ".":
            print("'.' pressed! - generations per second increased")
            self.increase_gens_per_sec()

    def handle_mouse(self, event, button):
        """
        LMB - pressed or held sets cell alive
        RMB - pressed or held sets cell dead
        :param event:
        :param button:
        """
        if button == WHEEL_UP:
            print("'WHEEL_UP'! - generations per second increased")
            self.increase_gens_per_sec()
            return True
        elif button == WHEEL_DOWN:
            print("'WHEEL_DOWN'! - generations per second decreased")
            self.decrease_gens_per_sec()
            return True

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
            if event.type == self.new_gen_event:
                if not self.paused:
                    self.draw()
                    self.update_generation()
            if event.type == QUIT:
                self.quit()
            elif event.type == pg.VIDEORESIZE:
                self.width = 640 if event.w < 640 else event.w
                self.height = 360 if event.h < 360 else event.h
                self.screen = pg.display.set_mode((self.width, self.height), HWSURFACE | DOUBLEBUF | RESIZABLE)
                self.new()
                self.draw()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4 or event.button == 5:
                    self.handle_mouse(event, event.button)
            elif event.type == KEYDOWN:
                self.handle_keys(event)
            elif button := pg.mouse.get_pressed(num_buttons=3):
                if not self.handle_mouse(event, button):
                    continue
            self.draw()

    def increase_gens_per_sec(self):
        self.gens_per_sec += CHANGE_GENS_PER_SEC if self.gens_per_sec <= (MAX_GENS_PER_SEC - CHANGE_GENS_PER_SEC) else 0
        pg.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))

    def decrease_gens_per_sec(self):
        self.gens_per_sec -= CHANGE_GENS_PER_SEC if self.gens_per_sec >= (MIN_GENS_PER_SEC + CHANGE_GENS_PER_SEC) else 0
        pg.time.set_timer(self.new_gen_event, int(1000 / self.gens_per_sec))

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
            self.clock.tick(self.fps)
