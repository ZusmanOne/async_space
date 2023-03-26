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


with open('animation/rocket_frame_1.txt','r') as content:
    spaceship_1=content.read()

with open('animation/rocket_frame_2.txt','r') as content:
    spaceship_2=content.read()


async def animate_spaceship(canvas,row,column):
    for _ in cycle(spaceship_1):
        row_direct,column_direct,space = read_controls(canvas)
        row += row_direct
        column += column_direct
        draw_frame(canvas, row, column, spaceship_1)
        await asyncio.sleep(0)
        # # стираем предыдущий кадр, прежде чем рисовать новый
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
    canvas.nodelay(True)
    rows_number, columns_number = canvas.getmaxyx()
    current_row = rows_number//3
    cuurent_column = columns_number//5
    coroutines_stars = [blink(canvas, random.randint(1, 9), random.randint(1, 180),
                        *random.choices('+*.:')) for _ in range(100)]
    coroutine_fire = fire(canvas, current_row, cuurent_column)
    coroutine_ship = animate_spaceship(canvas,current_row,cuurent_column)
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
            coroutine_fire = fire(canvas, current_row, cuurent_column)
            coroutine_fire.send(None)
            canvas.refresh()
        time.sleep(TIME_TIC)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
    curses.curs_set(False)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
