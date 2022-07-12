# import numpy as np
import random
import time


COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
random.seed(0)
# don't change the class name


class AI(object):
    # chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        v = 1
        self.chessboard_size = chessboard_size
        # You are white or black
        self.color = color
        self.opponent = -color
        # the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need add your decision into your candidate_list. System will get the end of your candidate_list as your decision .
        self.candidate_list = []

        self.wcond = [
            0, 20, 45, 55
        ]
        # count, move, pos, deadpos,safe
        self.weights = [
            (0, 1, 2, 1, 1),  # 0+
            (0, 2, 2, 1, 1),  # 20+
            (1, 2, 2, 1, 1),  # 45+
            (1, 0, 0, 0, 0),  # 55+
        ]
        self.all = []
        for x in range(self.chessboard_size):
            for y in range(self.chessboard_size):
                self.all.append((x, y))
        self.pos_mask_core = [
            [-30, 1, -2, -2],
            [1, 0, 0, 0],
            [-2, 0, 0, 0, ],
            [-2, 0, 0, 0],
        ]
        self.move_mask_core = [
            [0, 5, 0, 0],
            [5, 4, 4, 4],
            [0, 4, 1, 1, ],
            [0, 4, 1, 1],
        ]
        self.posmask = self.genmat(self.pos_mask_core)
        self.movemask = self.genmat(self.move_mask_core)

    def setweights(self, w, c):
        self.weights = w
        self.wcond = c

    def next(self, board, pos, color):
        res = [list(row) for row in board]
        cnt = 0
        res[pos[0]][pos[1]] = color
        for dirx in [-1, 0, 1]:
            for diry in [-1, 0, 1]:
                if (dirx != 0 or diry != 0):
                    for step in range(1, 8):
                        second = (pos[0]+dirx*step, pos[1]+diry*step)
                        if self.inside(second):
                            if self.get(res, second) == COLOR_NONE:
                                break
                            elif self.get(res, second) == color:
                                if step > 1:
                                    for t in range(1, step):
                                        if res[pos[0]+dirx * t][pos[1]+diry*t] == color or res[pos[0]+dirx * t][pos[1]+diry*t] == COLOR_NONE:
                                            raise Exception(
                                                f'flip error {pos} {(pos[0]+dirx * t,pos[1]+diry*t)}')
                                        res[pos[0]+dirx *
                                            t][pos[1]+diry*t] = color
                                        cnt += 1
                                break
                        else:
                            break
        if cnt == 0:
            raise Exception(f'no flip in {pos}')
        return res

    def genmat(self, core):
        res = [[] for _ in range(8)]
        for x, y in self.all:
            if x < 4:
                cx = x
            else:
                cx = 7-x
            if y < 4:
                cy = y
            else:
                cy = 7-y
            res[x].append(core[cx][cy])
        return res

    def timeout(self):
        return time.time()-self.start >= self.time_out-0.3

    def getweight(self, board):
        s = self.steps(board)
        for i in range(1, len(self.wcond)+1):
            if self.wcond[-i] <= s:
                return self.weights[-i]

    def inside(self, pos):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def flipped(self, chessboard, pos, color):
        res = 0
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                if x != 0 or y != 0:
                    old = pos
                    new = pos
                    cnt = 0
                    while(True):
                        new = (new[0]+x, new[1]+y)
                        if not self.inside(new) or self.get(chessboard, new) != -color:
                            break
                        else:
                            cnt += 1
                    if new != old and self.inside(new) and self.get(chessboard, new) == color:
                        res += cnt
        return res

    def put(self, board, pos, color):
        board[pos[0]][pos[1]] = color

    def get(self, board, pos):
        return board[pos[0]][pos[1]]

    def minimax(self, board, term, alpha, beta, stop):
        me = self.color*term
        cp = self.canput(board, me)
        if self.timeout():
            return 0
        if stop == 0 or self.timeout() or len(cp) == 0:
            return self.util(board, me)
        # res = -1e5 if term == 1 else 1e5
        scores = {}
        for pos in cp:
            scores[pos] = self.util(self.next(board, pos, me), me)
        cp.sort(key=lambda x: scores[x])
        for pos in cp:
            nextboard = self.next(board, pos, me)
            x = self.minimax(nextboard, -term, alpha, beta, stop-1)
            if self.timeout():
                return 0
            if term == 1:
                alpha = max(alpha, x)
                # res = max(res, x)
            else:
                beta = min(beta, x)
                # res = min(res, x)
            if alpha >= beta:
                return alpha if term == 1 else beta
        return alpha if term == 1 else beta

    def steps(self, board):
        cnt = 0
        for pos in self.all:
            if self.get(board, pos) != COLOR_NONE:
                cnt += 1
        return cnt

    def deadpos_score(self, board, color):
        cnt = 0
        for x in range(8):
            val = color*sum(board[x])
            if val > 6:
                cnt -= 10
            if val < 6:
                cnt += 10
        for y in range(8):
            val = color*sum(board[x][y] for x in range(8))
            if val > 6:
                cnt -= 10
            if val < 6:
                cnt += 10
        return cnt

    def safe_score(self, board, color):
        rival = -color
        safe = set(x for x in self.all if self.get(board,x) == color)
        for pos in self.canput(board, rival):
            afterput = self.next(board, pos, rival)
            safe = set(x for x in safe if self.get(afterput, x) == color)
        return len(safe)

    def count_score(self, board, color):  # ~10
        res = 0
        for pos in self.all:
            if self.get(board, pos) == color:
                res -= 1
            elif self.get(board, pos) == -color:
                res += 1
        return res

    def move_score(self, board, color):  # ~10
        res = 0
        for pos in self.canput(board, color):
            # if self.get(board, pos) == color:
            res += self.get(self.movemask, pos)
            # elif self.get(board, pos) == -color:
            #     res -= self.get(self.movemask, pos)
        return res

    def pos_score(self, board, color):  # ~10
        res = 0
        for pos in self.all:
            if self.get(board, pos) == color:
                res += self.get(self.posmask, pos)
            elif self.get(board, pos) == -color:
                res -= self.get(self.posmask, pos)
        return res

    def util(self, board, color):
        w = self.getweight(board)
        if color == self.color:
            sign = 1
        else:
            sign = -1
        val = self.count_score(
            board, color)*w[0]+self.move_score(board, color)*w[1]+self.pos_score(board, color)*w[2]+self.deadpos_score(board, color)*w[3]+self.safe_score(board, color)*w[4]
        return val*sign

    def canput(self, board, color):
        res = []
        for pos in self.all:
            if self.get(board, pos) == COLOR_NONE:
                s = self.flipped(board, pos, color)
                if s > 0:
                    res.append(pos)
        return res
    # The input is current chessboard.

    def go(self, chessboard):
        self.start = time.time()
        self.candidate_list.clear()
        choices = self.canput(chessboard, self.color)
        score = {}
        for stop in range(2, 20):
            temp = {}
            finish = True
            if self.timeout():
                break
            for x in choices:
                s = self.minimax(
                    self.next(chessboard, x, self.color), -1, -1e6, 1e6, stop)
                if self.timeout():
                    finish = False
                    break
                temp[x] = s
            if finish:
                score = temp
        choices.sort(key=lambda x: score[x])
        print(choices)
        print(score)
        self.candidate_list = choices
        # print(self.candidate_list)


def show(board):
    # for y in range(8):
    #     print(y,end='')
    # print('')
    for i, row in enumerate(board):
        print(i, end='')
        for item in row:
            if item == COLOR_NONE:
                print('-', end='')
            elif item == COLOR_WHITE:
                print('@', end='')
            elif item == COLOR_BLACK:
                print('*', end='')
            else:
                print(item, end='')
        print('')
    print('')


def play(size, ai0: AI, ai1: AI, w0=None, c0=None, w1=None, c1=None):
    if w0 is not None:
        ai0.setweights(w0, c0)
    if w1 is not None:
        ai1.setweights(w1, c1)
    chessboard = [[0 for _ in range(size)] for _ in range(size)]
    chessboard[3][3] = 1
    chessboard[4][4] = 1
    chessboard[3][4] = -1
    chessboard[4][3] = -1
    stoptag = 0
    while(True):
        ai0.go(chessboard)
        if(len(ai0.candidate_list) == 0):
            if stoptag == 1:
                break
            else:
                stoptag = 1
        stoptag = 0
        ai0_choice = ai0.candidate_list[-1]

        if chessboard[ai0_choice[0]][ai0_choice[1]] != COLOR_NONE:
            raise "duplicated step"
        chessboard[ai0_choice[0]][ai0_choice[1]] = 1
        chessboard = ai0.next(chessboard, ai0_choice, ai0.color)
        show(chessboard)
        ai1.go(chessboard)
        if(len(ai1.candidate_list) == 0):
            if stoptag == 1:
                break
            else:
                stoptag = 1
        stoptag = 0
        ai1_choice = ai1.candidate_list[-1]
        if chessboard[ai1_choice[0]][ai1_choice[1]] != COLOR_NONE:
            raise "duplicated step"
        chessboard[ai1_choice[0]][ai1_choice[1]] = -1
        chessboard = ai1.next(chessboard, ai1_choice, ai1.color)
        show(chessboard)
    return ai0.count_score(chessboard, ai0.color)


if __name__ == '__main__':
    size = 8
    ai = AI(8, 1, 5)
    ai2 = AI(8, -1, 5)
    play(size, ai, ai2)
