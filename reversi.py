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
        self.chessboard_size = chessboard_size
        self.color = color
        self.opponent = -color
        self.time_out = time_out
        self.greedy=False
        self.candidate_list = []

        self.epoch = [
            0, 25, 45, 60
        ]
        # count, pos, crowd, move
        # self.weights = [
        #     [2, 1, 1,0],  # 0+
        #     [2, 2, 2,1],  # 20+
        #     [2, 2, 3,1],  # 40+
        #     [1, 0, 0,0],  # 55+
        # ]
        self.weights=[
            [3,3,2,0,0],  # 0+
            [3, 4, 2,1,0],  # 20+
            [3, 1, 2,2,0],  # 40+
            [1,0,0,0,0]
        ]
        
        # self.weights = [
        #     [1, 3,2,0,1],  # 0+
        #     [1, 4,2,1,1],  # 20+
        #     [1,1,1,2,1],  # 40+
        #     [2, 1,1,-1,0],  # 55+
        # ]
        
        # zhu,zhen
        # self.weights = [
        #     [4,3,0,2,1],  # 0+
        #     [3, 2, 1,1,2],  # 20+
        #     [1, 1, 1,2,2],  # 40+
        #     [2, 1, 1,-1,1],  # 55+
        # ]
        self.all = []
        for x in range(8):
            for y in range(8):
                self.all.append((x, y))
        # self.pos_core = [
        #     [-100, 20, -20, 2],
        #     [20, 8, -19, -5],
        #     [-20, -19, -4, 8 ],
        #     [2,-5 , 8, 3],
        # ]
        self.pos_core = [
            [-100, 20, -5, -5],
            [20, -2, -1, -1],
            [-5, -1, -1, -3, ],
            [-5, -3, -1, -1],
        ]
        """
        -117.0 15.0 -7.0 -40.0 -19.0 -4.0 2.0 -5.0 5.0 13.0 | 5.2 2.8 -0.1 3.5() 1.7 2.3 0.4 0.8 ()1.1 0.8 -1.8 0.9 ()2.3 2.0 2.2 -4.2
        -162.0,-7.0,4.0,-16.0,-18.0,-26.0,4.0,-9.0,-3.0,19.0,3.4,7.7,-1.9,4.5,2.6,2.9,0.5,-0.6,1.5,-2.8,-1.4,0.4,-5.1,4.9,1.4,2.9,5.3,0.9,-1.5,1.5,
        """
        self.posmask = self.genmat(self.pos_core)
        self.move_core = [
            [0, 2, 1, 1],
            [2, 2, 2, 2],
            [1, 2, 1, 1, ],
            [1, 2, 1, 1],
        ]
        self.movemask = self.genmat(self.move_core)
        
        # print('pos mask:')
        # print(self.posmask)

    def from_list(self, w):
        w=list(w)
        w.append(0)
        self.pos_core = [
            [w[0], w[1], w[3], w[4]],
            [w[1], w[2], w[5], w[5]],
            [w[3], w[4], w[5], w[6]],
            [w[6], w[7], w[8], w[9]],
        ]
        w = w[10:]
        self.posmask=self.genmat(self.pos_core)
        for i, row in enumerate(self.weights):
            for j, _ in enumerate(row):
                self.weights[i][j] = w[0]
                w = w[1:]
    
    def to_list(self):
        res=[]
        # show(self.posmask)
        # print(self.weights)
        # self.epoch = w
        # print('epoch', self.epoch)
        # print('weights', self.weights)

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
                                            raise Exception(f'wrong flip')
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
        return time.time()-self.start >= self.time_out-0.2

    def getweight(self, board):
        s = self.steps(board)
        for i in range(1, len(self.epoch)+1):
            if self.epoch[-i] <= s:
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
            return self.eval(board, me)
        # random.shuffle(cp)
        for pos in cp:
            nextboard = self.next(board, pos, me)
            x = self.minimax(nextboard, -term, alpha, beta, stop-1)
            if self.timeout():
                return 0
            if term == 1:
                alpha = max(alpha, x)
            else:
                beta = min(beta, x)
            if alpha >= beta:
                return alpha if term == 1 else beta
        return alpha if term == 1 else beta

    def steps(self, board):
        return len([pos for pos in self.all if self.get(board, pos) != COLOR_NONE])

    def crowd_score(self, board, color):
        cnt = 0
        for x in range(8):
            if board[x][0]!=color and board[x][7]!=color:
                continue
            for y in range(8):
                if board[x][y]==color:
                    cnt+=1
        for y in range(8):
            if board[0][y]!=color and board[7][y]!=color:
                continue
            for x in range(8):
                if board[x][y]==color:
                    cnt+=1
        cnt//=2
        return cnt
    
    def move_score(self, board, color):  # ~10
        res = 0
        for pos in self.canput(board, -color):
            res -= self.get(self.movemask, pos)
        return res

    def count_score(self, board, color):  # ~10
        res = 0
        for pos in self.all:
            if self.get(board, pos) == color:
                res -= 1
            elif self.get(board, pos) == -color:
                res += 1
        if res<-15:
            res*=2
        if res<=25:
            res*=2
        return res
    
    def frontier_score(self,board,color):
        dirx=[0,0,1,-1]
        diry=[1,-1,0,0]
        cnt=0
        for pos in self.all:
            if self.get(board,pos)==color:
                for i in range(4):
                    t=(pos[0]+dirx[i],pos[1]+diry[i])
                    if self.inside(t):
                        if self.get(board,t)==COLOR_NONE:
                            cnt+=1
                            break
        return cnt
    
    def count_difference(self,board,color):
        res = 0
        for pos in self.all:
            if self.get(board, pos) == color:
                res -= 1
            elif self.get(board, pos) == -color:
                res += 1
        return res

    def pos_score(self, board, color):  # ~10
        res = 0
        for pos in self.all:
            if self.get(board, pos) == color:
                res += self.get(self.posmask, pos)
            elif self.get(board, pos) == -color:
                res -= self.get(self.posmask, pos)
        return res

    def eval(self, board, color):
        # if len(self.canput(board,color))==0 and len(self.canput(board,-color))==0:
        #     s=self.count_score(board,color)
        #     if s>0:
        #         return 1e5
        #     if s==0:
        #         return 1e4
        #     return -1e5
        w = self.getweight(board)
        if color == self.color:
            sign = 1
        else:
            sign = -1
        val=0
        if w[0]!=0:
            val+=self.count_score(board, color)*w[0]
        if w[1]!=0:
            val+=self.pos_score(board, color)*w[1]
        if w[2]!=0:
            val+=self.crowd_score(board, color)*w[2]
        if w[3]!=0:
            val+=self.move_score(board,color)*w[3]
        if w[4]!=0:
            val+=self.frontier_score(board,color)*w[4]
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
        #2,4,9
        slist=[0,2,4,9,12,16]
        if self.greedy:
            slist=[0]
        for stop in slist:
            if self.timeout():
                break
            temp={}
            finish=True
            for x in choices:
                nextboard=self.next(chessboard, x, self.color)
                s = self.minimax(
                    nextboard, -1, -1e6, 1e6, stop)
                if self.timeout():
                    finish=False
                    break
                temp[x]=s
                # +self.move_score(nextboard,self.color)
            if finish:
                # print(stop)
                score=temp
        # print(choices)
        # print(score)
        choices.sort(key=lambda x: score[x])
        self.candidate_list = choices


def show(board):
    # return
    for i, row in enumerate(board):
        # print(i, end='')
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


def play(w0=None, w1=None):
    random.seed(time.time())
    ai0 = AI(8, 1,1e5)
    ai1 = AI(8, -1, 1e5)
    ai0.greedy=True
    ai1.greedy=True
    if w0 is not None:
        ai0.from_list(w0)
    if w1 is not None:
        ai1.from_list(w1)
    chessboard = [[0 for _ in range(8)] for _ in range(8)]
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
        else:
            stoptag = 0
            ai0_choice = ai0.candidate_list[-1]
            if chessboard[ai0_choice[0]][ai0_choice[1]] != COLOR_NONE:
                raise "duplicated step"
            chessboard = ai0.next(chessboard, ai0_choice, ai0.color)
            # show(chessboard)
        ai1.go(chessboard)
        if(len(ai1.candidate_list) == 0):
            if stoptag == 1:
                break
            else:
                stoptag = 1
        else:
            stoptag = 0
            ai1_choice = ai1.candidate_list[-1]
            if chessboard[ai1_choice[0]][ai1_choice[1]] != COLOR_NONE:
                raise "duplicated step"
            chessboard = ai1.next(chessboard, ai1_choice, ai1.color)
            # show(chessboard)
    return ai0.count_difference(chessboard, ai0.color)


if __name__ == '__main__':
    pass
    # w=[-100, 20, 10, -5, 1, -1, -5, 1, -1, -1, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1, 0, 0, 0]
    # while True:
    print(play())