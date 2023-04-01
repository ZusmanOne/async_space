import time
import asyncio
import curses
import random
from itertools import cycle
from curses_tools import read_controls,draw_frame,get_frame_size


TIME_TIC = 0.1
SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258


with open('animation/rocket_frame_1.txt', 'r') as content:
    spaceship_1=content.read()

with open('animation/rocket_frame_2.txt', 'r') as content:
    spaceship_2=content.read()


async def animate_spaceship(canvas, row, column):
    row,column = row//5, column//5
    row_frame, column_frame = canvas.getmaxyx()
    row_ship, column_ship = get_frame_size(spaceship_1)
    row_limit = row_frame-row_ship
    column_limit = column_frame-column_ship
    for _ in cycle(spaceship_1):
        next_row,next_column,space = read_controls(canvas)
        current_row = row + next_row
        current_column = column + next_column
        if 0 < current_row < row_limit and 0 < current_column < column_limit:
            row = current_row
            column = current_column
        draw_frame(canvas, row, column, spaceship_1)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, spaceship_1, negative=True)
        draw_frame(canvas, row, column, spaceship_2)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, spaceship_2, negative=True)


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


async def blink(canvas, row, column, symbol,offset_tics):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(offset_tics):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    canvas.border()
    canvas.nodelay(True)
    rows_number, columns_number = canvas.getmaxyx()
    current_row = rows_number//3
    current_column = columns_number//5
    coroutines = [blink(canvas, random.randrange(rows_number), random.randrange(columns_number),
                        *random.choices('+*.:'), random.randint(1, 20)) for _ in range(200)]
    coroutines.append(fire(canvas, current_row, current_column))
    coroutines.append(animate_spaceship(canvas, rows_number, columns_number))
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
                coroutines.append(fire(canvas, current_row, current_column))
                #coroutine_fire.send(None)
            if len(coroutines) == 0:
                break
        # try:
        #     coroutine_ship.send(None)
        #     coroutine_fire.send(None)
        #     #canvas.refresh()
        # except StopIteration:
        #     coroutine_fire = fire(canvas, current_row, current_column)
        #     coroutine_fire.send(None)
        canvas.refresh()
        time.sleep(TIME_TIC)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
