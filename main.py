import time
import asyncio
import curses
import random
from itertools import cycle

TIME_TIC = 0.1
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

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

async def animate_spaceship(canvas):
    row, column = (1, 30)
    for _ in cycle(spaceship_1):
        draw_frame(canvas, row, column, spaceship_1)
        #canvas.refresh()
        await asyncio.sleep(0)
        # # стираем предыдущий кадр, прежде чем рисовать новый
        draw_frame(canvas, row, column, spaceship_1, negative=True)
        #canvas.refresh()
        # #await asyncio.sleep(0)
        draw_frame(canvas, row, column, spaceship_2)

        await asyncio.sleep(0)
        draw_frame(canvas, row, column, spaceship_2, negative=True)
        # canvas.refresh()
        #await asyncio.sleep(0)

async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol):
    while True:
        for _ in range(random.randint(1, 20)):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)

        for _ in range(random.randint(1, 50)):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)


        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


def draw(canvas):
    rows_number, columns_number = canvas.getmaxyx()
    print('qqqqqqqqqqqqqqqqqqq')
    print(rows_number,columns_number)
    coroutines_stars = [blink(canvas, random.randint(1, 9), random.randint(1, 180),
                        *random.choices('+*.:')) for _ in range(100)]
    coroutine_fire = fire(canvas, 10, 20)
    coroutine_ship = animate_spaceship(canvas)
    while True:

        for coroutine in coroutines_stars.copy():
            try:
                coroutine.send(None)
                canvas.border()
                canvas.refresh()

            except StopIteration:
                coroutines_stars.remove(coroutine)
            if len(coroutines_stars) == 0:
                break

        try:
            coroutine_ship.send(None)
            coroutine_fire.send(None)
            canvas.refresh()
        except StopIteration:
            coroutine_fire = fire(canvas, 10, 20)
            coroutine_fire.send(None)
            canvas.refresh()

        time.sleep(TIME_TIC)




# def draw(canvas):
#     coroutine_fire = fire(canvas, 5, 20)
#     while True:
#         try:
#             coroutine_fire.send(None)
#             canvas.refresh()
#         except StopIteration:
#             break
#         time.sleep(1)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
