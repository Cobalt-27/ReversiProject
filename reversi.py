import enum
from secrets import choice
import numpy as np
import random
import time

from pandas import reset_option

COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
random.seed(0)
# don't change the class name


class AI(object):
    # chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        v=1
        self.chessboard_size = chessboard_size
        # You are white or black
        self.color = color
        self.opponent = -color
        # the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need add your decision into your candidate_list. System will get the end of your candidate_list as your decision .
        self.candidate_list = []

        self.wcond = [
            0, 20, 45, 54
        ]
        # count, move, pos
        self.weights = [
            (2, 2, 1),  # 0+
            (3, 2, 1),  # 20+
            (10, 1, 2),  # 45+
            (20, 0, 0),  # 55+
        ]
        self.all = []
        for x in range(self.chessboard_size):
            for y in range(self.chessboard_size):
                self.all.append((x, y))
        self.maskcore = [
            [-100, -10, -20, -20],
            [-10, 20, 20, 20],
            [-20, 20, 1, 1, ],
            [-20, 20, 1, 1],
        ]
        self.genmat()
        # show(self.mask)
        # print(self.mask)

    def setseed(self, seed):
        m0 = seed[0]
        m1 = seed[1]
        m2 = seed[2]
        m3 = seed[3]
        m4 = seed[4]
        self.maskcore = [
            [m0, m1, m2, m2],
            [m1, m3, m3, m3],
            [m2, m3, m4, m4, ],
            [m2, m3, m4, m4],
        ]
        self.mask=self.genmat(self.maskcore)

    def next(self, board, pos, color):
        res = [list(row) for row in board]
        cnt = 0
        res[pos[0]][pos[1]]=color
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
                                            # show(res)
                                            # show(board)
                                            # exit(f'flip error {pos} {(pos[0]+dirx * t,pos[1]+diry*t)} {color}')
                                            # print()
                                            raise Exception(
                                                f'flip error {pos} {(pos[0]+dirx * t,pos[1]+diry*t)}')
                                        # else:
                                        #     print('ok')
                                        #     show(res)
                                        res[pos[0]+dirx *
                                            t][pos[1]+diry*t] = color
                                        cnt += 1
                                break
                        else:
                            break
        if cnt == 0:
            raise Exception(f'no flip in {pos}')
        return res

    def genmat(self,core):
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
            res.append(core[cx][cy])
        return res

    def timeout(self):
        return time.time()-self.start >= self.time_out-0.3

    def getweight(self, board):
        s = self.steps(board)
        for i in range(1, len(self.wcond)+1):
            if self.wcond[-i] <= s:
                return self.weights[-i]

    def inside(self, pos):
        return 0 <= pos[0] < self.chessboard_size and 0 <= pos[1] < self.chessboard_size

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

    def get(self, chessboard, pos):
        return chessboard[pos[0]][pos[1]]

    def minimax(self, board, term, alpha, beta, stop):
        me=self.color*term
        cp=self.canput(board, me)
        if self.timeout():
            return 0
        if stop == 0 or self.timeout() or len(cp)==0:
            return self.eval(board)
        # res = -1e5 if term == 1 else 1e5
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
                return alpha if term==1 else beta
        return alpha if term==1 else beta

    def steps(self, board):
        cnt = 0
        for pos in self.all:
            if self.get(board, pos) != COLOR_NONE:
                cnt += 1
        return cnt

    def count_score(self, board):  # ~10
        res = 0
        for pos in self.all:
            if self.get(board, pos) == self.color:
                res -= 1
            elif self.get(board, pos) == -self.color:
                res += 1
        return res

    def move_score(self, board):  # ~10
        res = 0
        for pos in self.canput(board,self.color):
            if self.get(board, pos) == self.color:
                res += self.mask[pos[0]][pos[1]]
            elif self.get(board, pos) == -self.color:
                res -= self.mask[pos[0]][pos[1]]
        return res

    def pos_score(self, board):  # ~10
        res = 0
        for pos in self.all:
            if self.get(board, pos) == self.color:
                res += self.mask[pos[0]][pos[1]]
            elif self.get(board, pos) == -self.color:
                res -= self.mask[pos[0]][pos[1]]
        return res

    def eval(self, board):
        w = self.getweight(board)
        return self.count_score(board)*w[0]+self.move_score(board)*w[1]+self.pos_score(board)*w[2]

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
            if self.timeout():
                break
            for x in choices:
                s = self.minimax(self.next(chessboard,x,self.color), -1, -1e6, 1e6, stop)
                if self.timeout():
                    break
                score[x]=s
        choices.sort(key=lambda x: score[x])
        print(choices)
        print(score)
        self.candidate_list = choices
        # print(self.candidate_list)

def show(board):
    # for y in range(8):
    #     print(y,end='')
    # print('')
    for i,row in enumerate(board):
        print(i,end='')
        for item in row:
            if item == COLOR_NONE:
                print('-', end='')
            elif item == COLOR_WHITE:
                print('@', end='')
            elif item == COLOR_BLACK:
                print('*', end='')
            else:
                print(item,end='')
        print('')
    print('')
if __name__ == '__main__':
    size = 8
    ai = AI(8, 1, 5)
    ai2 = AI(8, -1, 5)
    def checkflip(board, pos):
        cnt = 0
        color = ai.get(board, pos)
        for dirx in [-1, 0, 1]:
            for diry in [-1, 0, 1]:
                if (dirx != 0 or diry != 0):
                    for step in range(1, size):
                        second = (pos[0]+dirx*step, pos[1]+diry*step)
                        if ai.inside(second):
                            if ai.get(board, second) == COLOR_NONE:
                                break
                            elif ai.get(board, second) == color:
                                if step > 1:
                                    for t in range(1, step):
                                        board[pos[0]+dirx *
                                              t][pos[1]+diry*t] = color
                                        cnt += 1
                                else:
                                    break
                        else:
                            break
        if cnt == 0:
            raise 'no flip'
        return board

    chessboard = [[0 for _ in range(size)] for _ in range(size)]
    chessboard[3][3] = 1
    chessboard[4][4] = 1
    chessboard[3][4] = -1
    chessboard[4][3] = -1
    while(True):
        ai.go(chessboard)
        if(len(ai.candidate_list) == 0):
            exit()
        ai_choice = ai.candidate_list[-1]

        if chessboard[ai_choice[0]][ai_choice[1]] != COLOR_NONE:
            raise "duplicated step"
        chessboard[ai_choice[0]][ai_choice[1]] = 1
        chessboard = checkflip(chessboard, ai_choice)
        show(chessboard)
        ai2.go(chessboard)
        if(len(ai2.candidate_list) == 0):
            exit()
        ai2_choice = ai2.candidate_list[-1]
        # ai2_choice = (int(input('x')), int(input('y')))
        if chessboard[ai2_choice[0]][ai2_choice[1]] != COLOR_NONE:
            raise "duplicated step"
        chessboard[ai2_choice[0]][ai2_choice[1]] = -1
        chessboard = checkflip(chessboard, ai2_choice)
        show(chessboard)
