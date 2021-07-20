import GameOfLife
from Settings import pg, WHITE, BLACK


class Cell(pg.sprite.Sprite):
    def __init__(self, game: GameOfLife, cell_size: int, x: int, y: int, color: (int, int, int) = None,
                 alive: bool = None):
        super().__init__(game.sprites)
        self.image = pg.Surface([cell_size, cell_size])
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * cell_size, y * cell_size)
        self.alive, self.color = None, None

        if color:
            self.revive(color) if alive else self.kill(color)
        else:
            self.revive() if alive else self.kill()

    def kill(self, color=WHITE):
        self.alive = False
        self.image.fill(color)
        self.color = color

    def revive(self, color=BLACK):
        self.alive = True
        self.image.fill(color)
        self.color = color

    def survive(self):
        r, g, b = self.color
        b += 5 if b <= 250 else 0
        r += 5 if r < 100 else 0
        self.color = (r, g, b)
        self.image.fill(self.color)
