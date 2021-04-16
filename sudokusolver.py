from __future__ import annotations
from random import randint as rand
import random
from typing import List
import pygame
import time



class _Cell:
    numbers: List[int]
    is_selected: bool
    is_locked: bool

    def __init__(self, val: int)-> None:
        self.numbers = [0]
        if val != 0:
            self.numbers.append(val)
        self.is_selected = False

    def __len__(self):
        return len(self.numbers)

    def add_num(self, val: int)-> None:
        if val in self.numbers:
            self.delete_num(val)
        else:
            self.numbers.append(val)

    def delete_num(self, val: int)-> None:
        self.numbers.remove(val)

    def delete_all_but_one(self, val: int)-> None:
        arr = self.numbers.copy()
        arr.remove(val)
        for item in arr:
            self.numbers.remove(item)

    def copy(self):
        new_cell = _Cell(0)
        new_cell.delete_num(0)
        for i in self.numbers:
            new_cell.add_num(i)
        new_cell.is_selected = self.is_selected
        return new_cell


ROW = [1, 2, 3, 4, 5, 6, 7, 8, 9]
COL = [1, 2, 3, 4, 5, 6, 7, 8, 9]
BOX = [1, 2, 3, 4, 5, 6, 7, 8, 9]


class Board:

    counter: int
    board: List[List[_Cell]]
    board2: List[List[int]]
    _changed_cell = (int, int)
    _prev_cell = (int, int)
    _board_list = [List[List[List]]]
    _cell_list = List
    _clue_counter: int

    def __init__(self, arr):
        self._clue_counter = 0
        self._cell_list = []
        self.board = []
        self.board2 = []
        self.counter = 0
        self._changed_cell = (0, 0)
        self._prev_cell = (0, 0)
        self._cell_list = []
        # for i in range(0, 9):
        #     row = []
        #     row2 = []
        #     for j in range(0, 9):
        #         cell = _Cell(arr[i][j])
        #         row.append(cell)
        #         row2.append(arr[i][j])
        #     self.board.append(row)
        #     self.board2.append(row2)

        for i in range(0, 9):
            row = []
            row2 = []
            for j in range(0, 9):
                cell = _Cell(0)
                cell.is_locked = False
                row.append(cell)
                row2.append(0)
            self.board.append(row)
            self.board2.append(row2)

        self.generate_grid()


    def __getitem__(self, item):
        return self.board[item]

    def __setitem__(self, key, value):
        self.board[key] = value

    def __str__(self)-> str:
        pr = ''

        for i in range(0, 9):
            for j in range(0, 9):
                pr += ' ' + str(self[i][j].numbers[1]) + ' '
            pr += '\n'
        return pr

    def _add_num(self, row, col, num):
        self.board[row][col].add_num(num)

    def _delete_num(self, row, col, num):
        self.board[row][col].delete_num(num)

    def _delete_all_but_one(self, row, col, num):
        self.board[row][col].delete_all_but_one(num)

    def _is_partial(self, row: int, col: int)-> bool:
        if self._check_row(row) and self._check_col(col) and \
                    self._check_box(row, col):
            return True
        return False

    def _is_partial_2(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if not self._is_partial(i, j):
                    return False
        return True

    def _check_row(self, row):
        check = ROW.copy()
        for val in self[row]:
            try:
                if len(val.numbers) == 2:
                    check.remove(val.numbers[1])
            except ValueError:
                return False
        return True

    def _check_col(self, col):
        check = COL.copy()
        for i in range(0, 9):
            val = self[i][col]
            try:
                if len(val.numbers) == 2:
                    check.remove(val.numbers[1])
            except ValueError:
                return False
        return True

    def _check_box(self, row, col):
        bounds = get_box(row, col)
        check = BOX.copy()
        for i in range(bounds[0][0], bounds[0][1] + 1):
            for j in range(bounds[1][0], bounds[1][1] + 1):
                val = self[i][j]
                try:
                    if len(val.numbers) == 2:
                        check.remove(val.numbers[1])
                except ValueError:
                    return False
        return True



    def _backtrack(self):
        if self.is_solved():
            #print(self)
            return True
        a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        random.shuffle(a)
        for val in a:
            r, c = self._find_next_cell()
            self[r][c].add_num(val)
            if self._is_partial(r, c):
                if self._backtrack():
                    return True
            self[r][c].delete_all_but_one(0)
        return False



    def _backtrack3(self, num):
        if self.is_solved():
            return True
        if num == 81:
            return True
        #  a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        r = num // 9
        c = num % 9
        while len(self[r][c]) != 1:
            num += 1
            r = num // 9
            c = num % 9
        for val in ROW:
            self[r][c].add_num(val)
            self._clue_counter += 1
            if self._is_partial(r, c):
                if self._backtrack3(num + 1):
                    return True
            self[r][c].numbers.pop(1)
            self._clue_counter -= 1
        return False

    def _generator_helper(self, num):
        if self.is_solved():
            return True
        if num == 81:
            return True
        a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        random.shuffle(a)
        r = num // 9
        c = num % 9
        while len(self[r][c]) != 1:
            num += 1
            r = num // 9
            c = num % 9
        for val in a:
            self[r][c].add_num(val)
            if self._is_partial(r, c):
                if self._generator_helper(num + 1):
                    return True
            self[r][c].delete_all_but_one(0)
        return False


    def _backtrack2(self):
        if self.counter > 1:
            return False
        if not self._is_partial(self._changed_cell[0], self._changed_cell[1]):
            return False
        if self.is_solved():
            self.counter += 1
            if self.counter > 1:
                print('ambiguous')
                return False
            return True
        s = self._first()
        while s is not None:
            self._backtrack2()
            s = self._next()

    def _first(self):
        if self._all_cells_filled():
            return None
        r, c = self._find_next_cell()
        self._add_num(r, c, 1)
        self._prev_cell = self._changed_cell
        self._cell_list.append(self._prev_cell)
        self._changed_cell = r, c
        return True

    def _next(self):
        r, c = self._changed_cell
        #print(r, c, self[r][c].numbers, '\n')
        if self[r][c].numbers[1] == 9:
            self._delete_all_but_one(r, c, 0)
            self._changed_cell = self._cell_list.pop()
            return None
        self[r][c].numbers[1] += 1
        return True

    def _all_cells_filled(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if len(self[i][j].numbers) == 1:
                    return False
        return True

    def solve(self):
        print('solve 1')
        self._prep_for_backtrack()
        return self._backtrack3(0)

    def _num_solutions(self):
        self.counter = 0
        self._backtrack2()
        return self.counter

    def generate_grid(self):


        self._generator_helper(0)

        self.generate_puzzle(45)


    def generate_puzzle(self, num):
        self._clue_counter = 81 - num
        count = 0
        val = 0
        nums = []
        r2, c2 = 0, 0

        while count < num:
            # print('running')
            r, c = rand(0, 8), rand(0, 8)
            while len(self[r][c]) == 1:
                r, c = rand(0, 8), rand(0, 8)
            val = self[r][c].numbers[1]
            self._delete_all_but_one(r, c, 0)
            count += 1
            self.counter = 0
        #     self._backtrack2()
        #     if self.counter > 1:
        #         self._add_num(r, c, val)
        #         count -= 1
        for r in range(0, 9):
            for c in range(0, 9):
                if len(self[r][c]) == 2:
                    self[r][c].is_locked = True



    def _find_next_cell(self)->(int, int):
        for i in range(0, 9):
            for j in range(0, 9):
                if len(self[i][j].numbers) == 1:
                    return i, j

    def _prep_for_backtrack(self):
        for i in range(0, 9):
            for j in range(0, 9):
                if len(self.board[i][j].numbers) > 2:
                    self.board[i][j].delete_all_but_one(0)

    def is_solved(self):
        if self._clue_counter == 81:
            row = False
            col = False
            box = False
            for i in range(0, 9):
                row = self._check_row(i)
                col = self._check_col(i)
                if row == False:
                    return False
                if col == False:
                    return False

            for i in range(0, 9, 3):
                for j in range(0, 9, 3):
                    box = self._check_box(i, j)
                    if not box:
                        return False

            for i in range(0, 9):
                for j in range(0, 9):
                    if len(self.board[i][j].numbers) == 1:
                        return False
            return True
        return False


def increment_cell(row: int, col: int):
    col += 1
    if col > 8:
        row += 1
        col = 0
    return row, col

def decrement_cell(row, col):
    col -= 1
    if col < 0:
        row -= 1
        col = 8
    return row, col

def get_box(row, col):
    if 0 <= row <= 2:
        if 0 <= col <= 2:
            return [0, 2], [0, 2]
        elif 3 <= col <= 5:
            return [0, 2], [3, 5]
        else:
            return [0, 2], [6, 8]
    elif 3 <= row <= 5:
        if 0 <= col <= 2:
            return [3, 5], [0, 2]
        elif 3 <= col <= 5:
            return [3, 5], [3, 5]
        else:
            return [3, 5], [6, 8]
    else:
        if 0 <= col <= 2:
            return [6, 8], [0, 2]
        elif 3 <= col <= 5:
            return [6, 8], [3, 5]
        else:
            return [6, 8], [6, 8]


a = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
     [6, 0, 0, 1, 9, 5, 0, 0, 0],
     [0, 9, 8, 0, 0, 0, 0, 6, 0],
     [8, 0, 0, 0, 6, 0, 0, 0, 3],
     [4, 0, 0, 8, 0, 3, 0, 0, 1],
     [7, 0, 0, 0, 2, 0, 0, 0, 6],
     [0, 6, 0, 0, 0, 0, 2, 8, 0],
     [0, 0, 0, 4, 1, 9, 0, 0, 5],
     [0, 0, 0, 0, 8, 0, 0, 7, 9]]


def copy(arr):
    final = []
    for i in range(0, 9):
        mid = []
        for j in range(0, 9):
            mid.append(arr[i][j])
        final.append(mid)
    return final


def get_offset(num: int)-> (int, int):
    x = 0
    y = 0
    if num == 1:
        y = 15
        x = 15
    elif num == 2:
        y = 15
        x = 30
    elif num == 3:
        y = 15
        x = 45
    elif num == 4:
        y = 30
        x = 15
    elif num == 5:
        y = 30
        x = 30
    elif num == 6:
        y = 30
        x = 45
    elif num == 7:
        y = 45
        x = 15
    elif num == 8:
        y = 45
        x = 30
    elif num == 9:
        y = 45
        x = 45
    return x, y

# b = Board(a)
# print(b.solve())
# print(b)

def handle_click(pos)-> (int, int):
    return pos[0] // 50, pos[1] // 50


if __name__ == '__main__':

    BIGTEXT_CENTER = (30, 30)
    BIGTEXT_SIZE = 25
    SMALL_TEXT_CENTER = (15, 15)
    SMALLTEXTSIZE = 12

    LIGHT_BLUE = (176, 216, 230)

    a = [[1, 5, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0]]

    b = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
         [6, 0, 0, 1, 9, 5, 0, 0, 0],
         [0, 9, 8, 0, 0, 0, 0, 6, 0],
         [8, 0, 0, 0, 6, 0, 0, 0, 3],
         [4, 0, 0, 8, 0, 3, 0, 0, 1],
         [7, 0, 0, 0, 2, 0, 0, 0, 6],
         [0, 6, 0, 0, 0, 0, 2, 8, 0],
         [0, 0, 0, 4, 1, 9, 0, 0, 5],
         [0, 0, 0, 0, 8, 0, 0, 7, 9]]

    gameboard = Board(b)

    pygame.init()
    gameDisplay = pygame.display.set_mode((800, 460))
    gameDisplay.fill((255, 255, 255))
    pygame.display.set_caption('Sudoku')
    clock = pygame.time.Clock()

    def text_objects(text, font, colour):
        textSurface = font.render(text, True, (0, 0, 0), colour)
        return textSurface, textSurface.get_rect()

    def draw_buttons():
        pygame.draw.rect(gameDisplay, (0, 0, 0), [590, 100, 100, 40], 5)
        TextSurf, TextRect = text_objects("solve", pygame.font.SysFont('arial', 20, True), (255, 255, 255))

        TextRect.center = (640, 115)
        gameDisplay.blit(TextSurf, TextRect)
        pygame.draw.rect(gameDisplay, (0, 0, 0), [590, 250, 100, 60], 5)
        TextSurf, TextRect = text_objects("visual solve",
                                          pygame.font.SysFont('arial', 20, True),
                                          (255, 255, 255))

        TextRect.center = (640, 115)
        gameDisplay.blit(TextSurf, TextRect)
        pygame.draw.rect(gameDisplay, (0, 0, 0), [590, 160, 100, 60], 5)
        TextSurf, TextRect = text_objects("Generate",
                                          pygame.font.SysFont('arial', 20,
                                                              True),
                                          (255, 255, 255))

        TextRect.center = (640, 265)
        gameDisplay.blit(TextSurf, TextRect)


    def draw_rect(x, y):
        pygame.draw.rect(gameDisplay, (0, 0, 0), [x, y, 50, 50], 1)


    def draw_boundaries():
        for i in range(0, 9):
            for j in range(0, 9):
                draw_rect(i * 50 + 5, j * 50 + 5)
                # pygame.draw.rect(gameDisplay, (0, 0, 0), [i * 50 + 5, j * 50 + 5, 50, 50], 1)

    draw_boundaries()

    def draw_border():
        for i in range(0, 3):
            for j in range(0, 3):
                pygame.draw.rect(gameDisplay, (0, 0, 0),
                                 [i * 150 + 5, j * 150 + 5, 150, 150], 5)
        pygame.display.update()

    draw_border()


    def text_objects(text, font, colour):
        textSurface = font.render(text, True, (0, 0, 0), colour)
        return textSurface, textSurface.get_rect()

    # gameboard[0][0].delete_all_but_one(0)
    # print(gameboard[0][0].numbers)
    # for i in range(1, 10):
    #     gameboard[0][0].add_num(i)
    # print(gameboard[0][0].numbers)

    def draw_nums(val: List, colour, i, j):
        center = (j * 50, i * 50)
        if len(val) == 2:
            num = str(val[1])
            largeText = pygame.font.SysFont('arial', 36)
            if gameboard[i][j].is_locked:
                largeText = pygame.font.SysFont('arial', 36, True)
            TextSurf, TextRect = text_objects(num, largeText, colour)
            TextRect.center = (center[0] + 30, center[1] + 30)
            gameDisplay.blit(TextSurf, TextRect)
        elif len(val) > 2:
            for k in val[1:]:
                num = str(k)
                offset = get_offset(k)
                largeText = pygame.font.SysFont('arial',
                                             SMALLTEXTSIZE)
                TextSurf, TextRect = text_objects(num, largeText, colour)
                TextRect.center = (center[0] + offset[0], center[1] + offset[1])
                gameDisplay.blit(TextSurf, TextRect)

    def draw_board():
        bold = False
        for i in range(0, 9):
            for j in range(0, 9):
                val = gameboard[i][j].numbers
                color = (0,0, 0)
                if gameboard[i][j].is_locked:
                    color = (255 , 255, 255)
                    bold = True
                else:
                    color = (255, 255, 255)
                    bold = False
                draw_nums(val, color, i, j)
        draw_buttons()

    def fill_selected_cells():
        for i in range(0, 9):
            for j in range(0, 9):
                if gameboard[i][j].is_selected == True:
                    gameboard[i][j].is_selected = False
                pygame.draw.rect(gameDisplay, (255, 255, 255),
                                 [i * 150 + 5, j * 150 + 5, 150, 150])

    def update_cells(x, y):
        colour = (255, 255, 255)
        if gameboard[y][x].is_selected:
            colour = LIGHT_BLUE
        pygame.draw.rect(gameDisplay, colour,
                         [x * 50 + 5, y * 50 + 5, 50, 50])
        pygame.draw.rect(gameDisplay, (0, 0, 0),
                         [x * 50 + 5, y * 50 + 5, 50, 50], 1)

        draw_nums(gameboard[y][x].numbers, colour, y, x)
        draw_border()
        pygame.display.update()

    draw_board()

    def visual_solve():
        if gameboard.is_solved():
            #print(self)
            return True
        a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        #random.shuffle(a)
        for val in a:
                r, c = gameboard._find_next_cell()
                gameboard[r][c].add_num(val)
                update_cells(c, r)
                pygame.display.update()
                update_cells(c, r)

                if gameboard._is_partial(r, c):
                    if gameboard._backtrack():
                        return True
                gameboard[r][c].numbers.pop()
                update_cells(c, r)
        return False

    def visual_solve2(num):
        pygame.display.update()
        if gameboard.is_solved():
            return True
        if num == 81:
            return True
        a = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        r = num // 9
        c = num % 9
        while len(gameboard[r][c]) != 1:
            num += 1
            r = num // 9
            c = num % 9
        update_cells(c, r)
        #pygame.display.update()
        for val in a:
            time.sleep(0.01)
            gameboard[r][c].add_num(val)
            update_cells(c, r)
            pygame.display.update()
            update_cells(c, r)
            if gameboard._is_partial(r, c):
                if visual_solve2(num + 1):
                    return True
            gameboard[r][c].numbers.pop()
            time.sleep(0.01)
            update_cells(c, r)
            pygame.display.update()
        return False



    # TextSurf, TextRect = text_objects('1', largeText)
    # TextRect.center = ((15), (15))
    # gameDisplay.blit(TextSurf, TextRect)
    pygame.display.update()

    gameRunning = True
    x, y = 0, 0
    selected_cell = 0, 0
    counterr = 0
    while gameRunning:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                print("GAME QUITED")
                pygame.quit()
                gameRunning = False
                quit()
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = handle_click(event.pos)
                gameboard[selected_cell[0]][selected_cell[1]].is_selected = False
                update_cells(selected_cell[1], selected_cell[0])
                print(x, y)
                if 0 <= x <= 8 and 0 <= y <= 8:
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].is_selected = False
                    else:
                        gameboard[y][x].is_selected = True
                        selected_cell = y, x
                    update_cells(x, y)
                if 590 <= event.pos[0] <= 690 and 100 <= event.pos[1] <= 140:
                    gameboard.solve()
                    fill_selected_cells()
                    draw_boundaries()
                    draw_border()
                    draw_board()
                    pygame.display.update()
                elif 590 <= event.pos[0] <= 690 and 250 <= event.pos[1] <= 310:
                    visual_solve2(0)
                    fill_selected_cells()
                    draw_boundaries()
                    draw_border()
                    draw_board()
                    pygame.display.update()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    visual_solve2(0)
                    #gameboard.solve()
                    #print(gameboard._num_solutions())
                    fill_selected_cells()
                    draw_boundaries()
                    draw_border()
                    draw_board()
                    pygame.display.update()
                    counterr += 1
                elif event.key == pygame.K_l:
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].is_locked = True
                elif event.key == pygame.K_1 or event.key == pygame.K_KP1\
                        and gameboard[y][x].is_locked == False:
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(1)
                        update_cells(x, y)
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2 \
                        and gameboard[y][x].is_locked == False:
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(2)
                        update_cells(x, y)
                elif event.key == pygame.K_3 or event.key == pygame.K_KP3 \
                        and gameboard[y][x].is_locked == False :
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(3)
                        update_cells(x, y)
                elif event.key == pygame.K_4 or event.key == pygame.K_KP4 \
                        and gameboard[y][x].is_locked == False :
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(4)
                        update_cells(x, y)
                elif event.key == pygame.K_5 or event.key == pygame.K_KP5 \
                        and gameboard[y][x].is_locked == False :
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(5)
                        update_cells(x, y)
                elif event.key == pygame.K_6 or event.key == pygame.K_KP6 \
                        and gameboard[y][x].is_locked == False :
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(6)
                        update_cells(x, y)
                elif event.key == pygame.K_7 or event.key == pygame.K_KP7 \
                        and gameboard[y][x].is_locked == False:
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(7)
                        update_cells(x, y)
                elif event.key == pygame.K_8 or event.key == pygame.K_KP8 \
                        and gameboard[y][x].is_locked == False :
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(8)
                        update_cells(x, y)
                elif event.key == pygame.K_9 or event.key == pygame.K_KP9 \
                        and gameboard[y][x].is_locked == False:
                    if gameboard[y][x].is_selected:
                        gameboard[y][x].add_num(9)
                        update_cells(x, y)
                elif event.key == pygame.K_UP:
                    gameboard[y][x].is_selected = False
                    update_cells(x, y)
                    y -= 1
                    if y < 0:
                        y = 8
                    gameboard[y][x].is_selected = True
                    update_cells(x, y)

                elif event.key == pygame.K_DOWN:
                    gameboard[y][x].is_selected = False
                    update_cells(x, y)
                    y += 1
                    if y > 8:
                        y = 0
                    gameboard[y][x].is_selected = True
                    update_cells(x, y)
                elif event.key == pygame.K_LEFT:
                    gameboard[y][x].is_selected = False
                    update_cells(x, y)
                    x -= 1
                    if x < 0:
                        x = 8
                    gameboard[y][x].is_selected = True
                    update_cells(x, y)
                elif event.key == pygame.K_RIGHT:
                    gameboard[y][x].is_selected = False
                    update_cells(x, y)
                    x += 1
                    if x > 8:
                        x = 0
                    gameboard[y][x].is_selected = True
                    update_cells(x, y)



