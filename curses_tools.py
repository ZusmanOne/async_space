import curses
import time
import asyncio
from itertools import cycle

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple with controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False
    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1


        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1


        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1


        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1


        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True


    return rows_direction, columns_direction, space_pressed


with open('animation/rocket_frame_1.txt','r') as content:
    spaceship_1=content.read()

with open('animation/rocket_frame_2.txt','r') as content:
    spaceship_2=content.read()


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def animate_spaceship(canvas,start_row,start_column):

    for _ in cycle(spaceship_1):
        row, column, space1 = read_controls(canvas)
        start_row += row
        start_column += column
        draw_frame(canvas, start_row, start_column, spaceship_1)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, spaceship_1, negative=True)
        draw_frame(canvas, start_row, start_column, spaceship_2)
        await asyncio.sleep(0)
        draw_frame(canvas, start_row, start_column, spaceship_2, negative=True)


def draw(canvas):
    canvas.nodelay(True)
    initial_row, initial_column = canvas.getmaxyx()
    row, column = initial_row//3,initial_column//5
    coroutine_ship = animate_spaceship(canvas, row, column)
    for _ in cycle(spaceship_1):
        coroutine_ship.send(None)
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)







