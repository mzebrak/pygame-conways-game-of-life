# Conway's Game of Life

My PyGame implementation of Conway's Game of Life.</br>
This implementation involves treating all edges of the grid as stitched together yielding a toroidal array.</br>
Be sure to check all of the features and controls below :smiley:

## Sections

1. [What is the game of life](#what-is-the-game-of-life)
2. [Rules](#rules)
3. [Presentation](#presentation)
4. [Configuration](#configuration)
5. [Running](#running)
6. [Features / Controls](#features--controls)

## What is the game of life

[link to the source [wikipedia.org]](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
> The Game of Life, also known simply as Life, is a cellular automaton devised by the British mathematician John Horton Conway in 1970.
>
>   It is a zero-player game, meaning that its evolution is determined by its initial state, requiring no further input. One interacts with the Game of Life by creating an initial configuration and observing how it evolves. It is Turing complete and can simulate a universal constructor or any other Turing machine.

## Rules

[link to the source [wikipedia.org]](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
> The universe of the Game of Life is an infinite, two-dimensional orthogonal grid of square cells, each of which is in one of two possible states, live or dead, (or populated and unpopulated, respectively). Every cell interacts with its eight neighbours, which are the cells that are horizontally, vertically, or diagonally adjacent. At each step in time, the following transitions occur:
> 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
> 2. Any live cell with two or three live neighbours lives on to the next generation.
> 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
> 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
>
> These rules, which compare the behavior of the automaton to real life, can be condensed into the following:
> 1. Any live cell with two or three live neighbours survives.
> 2. Any dead cell with three live neighbours becomes a live cell.
> 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

## Presentation

![](gifs/pattern_launched.gif)

![](gifs/playing.gif)

## Configuration

It is possible to run a .bat file with appropriate parameters modifying the program settings. If you want to check this
out, just edit the .bat file.

All parameters are optional, but when used, they take priority over the configuration settings in the Settings
class.</br></br>
Example configuration: `@py __main__.py -s 16 --gens_per_sec 10 -W 1280 -H 720 -F "../patterns/spacefiller.txt"`</br>
Here are the parameters that can be set:

| Shortcut | Parameter | Description | Values |
|---|---|---|---|
| `-h` | `--help` | show the help message and exit |  |
| `-s` | `--size` | startup size of each cell `(INT x INT)` | between `MIN_CELL_SIZE` and `MAX_CELL_SIZE` |
| `-f` | `--fps` | set the framerate cap during the game | must be greater or equal `1` |
| `-g` | `--gens` | startup number of generations per sec | between `MIN_GENS_PER_SEC` and `MAX_GENS_PER_SEC` |
| `-W` | `--width` | startup screen width | must be greater than `MIN_WIDTH` |
| `-H` | `--height` | startup screen height | must be greater than `MIN_HEIGHT` |
| `-F` | `--file` | relative path from __main__ to the folder with the file | ex. `-F "../patterns/glider.txt"` |

## Running

1. If you are using <b>Python launcher</b>
    - Install PyGame via CMD using:

            py -m pip install pygame

    - Then simply run the game by launching:

            gameoflife.bat

2. If you are using <b>Python executable</b>
    - Install PyGame via CMD using:

            pip install pygame
            
            or

            python -m pip install pygame

    - Then you need to edit the .bat file. This is what you need to enter:

            @python instead of @py

    - Then simply run the game by launching:

            gameoflife.bat

3. If you want to run this app with your IDE, just run the `__main__.py`

## Features / Controls

> - In addition to changing the generation per second with the keys, you can use the mouse scroll. While holding down the CTRL key, you can also resize the cell with the scroll.
> - When reading from a file, a living cell is marked as '1', 'o' or 'O'. In turn, a dead cell can be written as '0', '.' or '_'.</br>
    <b>Additionally, there is no need to fully complete the rows with dead cells, because they are completed automatically to align with the longest row.</b></br>
    If you want the whole line to be filled with dead cells, just hit enter, but make sure the last line contains a character like ' ', '0', '.' or '_'
> - There is a possibility to change the size of the window with the mouse by stretching the application window and cell alignment will be the same as before.
> - When decreasing the size of a single cell, the number of cells in the grid increases, but the old cell alignment is retained.
> - By increasing the size of a single cell, their number in the grid decreases, however, the new grid includes all cells relative to the top left corner.
> - It is possible to revive / kill cells with the mouse while the game is not paused, but sometimes it may be necessary to reduce the number of generations per second so that the update does not run too fast.
> - Cells that remain in the same place change their color with the number of generations - through purple until they are completely blue.
> - The current settings with the fps counter are displayed in the auxiliary menu available under the F1 button.

<br></br>

| Command | Description | Values / Info [ ] - startup |
|:---:|-----|-----|
| `F1` | show / hide help menu |  |
| `g` | show / hide additional grid | [GREY], WHITE, HIDDEN |
| `w` | show / hide cells route  |  |
| `e` | set the next color for dead cells | WHITE, [LIGHTEST_GREY], LIGHTER_GREY, LIGHT_GREY |
| `p` | run / pause the game |  |
| `s` | save current grid to a file |  |
| `r` | randomize grid |  |
| `n` | display next generation | (use when game is paused) |
| `t` | switch between cell sizes | 8x8, [16x16], 32x32, 64x64 |
| `z` \| `x` </br>OR VIA</br> `<CTRL>` + `<MOUSE WHEEL>` | adjust cell sizes</br> by -+ val of `CHANGE_CELL_SIZE` | range between `MIN_CELL_SIZE` and `MAX_CELL_SIZE` |
| `,` \| `.`</br>OR VIA</br>`<MOUSE WHEEL>` | generations per second</br>-+ val of `CHANGE_GENS_PER_SEC` | range between `MIN_GENS_PER_SEC` and `MAX_GENS_PER_SEC` |
| `<LMB>` | revives the indicated cell | (can be held for quicker setting) |
| `<RMB>` | kills the indicated cell | (can be held for quicker setting) |
| `q` | quit the game |  |
