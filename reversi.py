import enum
from secrets import choice
import numpy as np
import random
import time

COLOR_BLACK=-1
COLOR_WHITE=1
COLOR_NONE=0
random.seed(0)
#don't change the class name
class AI(object):
    #chessboard_size, color, time_out passed from agent
    def __init__(self, chessboard_size, color, time_out):
        self.chessboard_size = chessboard_size
        #You are white or black
        self.color = color
        self.opponent= -color
        #the max time you should use, your algorithm's run time must not exceed the time limit.
        self.time_out = time_out
        # You need add your decision into your candidate_list. System will get the end of your candidate_list as your decision .
        self.candidate_list = []
        all=[]
        for x in range(self.chessboard_size):
            for y in range(self.chessboard_size):
                all.append((x,y))
    
    def inside(self,pos):
        return 0<=pos[0]<self.chessboard_size and 0<=pos[1]<self.chessboard_size
    
    def flipped(self, chessboard,pos):
        res=0
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                if x!=0 or y!=0:
                    old=pos
                    new=pos
                    cnt=0
                    while(True):
                        new=(new[0]+x,new[1]+y)
                        if not self.inside(new) or self.get(chessboard,new)!=self.opponent:
                            break
                        else:
                            cnt+=1
                    if new!=old and self.inside(new) and self.get(chessboard,new)==self.color:
                        res+=cnt
        return res    
    
    def get(self,chessboard,pos):
        return chessboard[pos[0]][pos[1]]
    
    def minplay(self,board,alpha,beta):
        if self.end(board):
            return self.eval(board)
        res=-1000
        for pos in self.canput(board):
            pre=self.get(board,pos)
            self.put(board,pos,-self.color)
            x=self.maxplay(board,alpha,beta)
            self.put(board,pos,pre)
            beta=min(beta,x)
            res=min(res,x)
            if alpha>=beta:
                return res
        return res
    
    def maxplay(self,board,alpha,beta):
        if self.end(board):
            return self.eval(board)
        res=-1000
        for pos in self.canput(board):
            pre=self.get(board,pos)
            self.put(board,pos,self.color)
            x=self.minplay(board,alpha,beta)
            self.put(board,pos,pre)
            alpha=max(alpha,x)
            res=max(res,x)
            if alpha>=beta:
                return res
        return res
    
    def minimax(self,board,term,alpha,beta,stop):
        if stop==0:
            return self.eval(board)
        res=-1e5 if term==1 else 1e5
        for pos in self.canput(board):
            oldcolor=self.get(board,pos)
            self.put(board,pos,self.color*term)
            x=self.minimax(board,-term,alpha,beta,stop-1)
            self.put(board,pos,oldcolor)
            if term==1:
                alpha=max(alpha,x)
                res=max(res,x)
            else:
                beta=min(beta,x)
                res=min(res,x)
            if alpha>=beta:
                return res
        return res
    
    def totalstep(self,board):
        return len([c for _,c in self.allval(board) if c!=COLOR_NONE])
    
    def put(self,board,pos,color):
        board[pos[0]][pos[1]]=color
                
    def allval(self,board):
        res=[]
        for pos in self.all:
            res.append((pos,self.get(board,pos)))
        return res
                
    def eval(self,board):
        res={1:0,0:0,-1:0}
        for pos in self.all:
            res[self.get(board,pos)]+=1
        return res[-self.color]-res[self.color]
    
    def end(self,board):
        return len(self.canput(board))==0
    
    def canput(self,board):
        res=[]
        for x in range(self.chessboard_size):
            for y in range(self.chessboard_size):
                pos=(x,y)
                if self.get(board,pos)==COLOR_NONE:
                    s=self.flipped(board,pos)
                    if s>0:
                        res.append(pos)
        return res
    # The input is current chessboard.
    def go(self, chessboard):
        self.candidate_list.clear()
        choices=self.canput(chessboard)
        if(self.totalstep(chessboard)<56):
            choices.sort(key=lambda x:-self.flipped(chessboard,x))
        else:
            score={}
            for x in choices:
                pre=self.get(chessboard,x)
                self.put(chessboard,x,self.color)
                score[x]=(self.maxplay(chessboard,-1000,1000))
                self.put(chessboard,x,pre)
            choices.sort(key=lambda x:score[x])
        print(choices)
        self.candidate_list=choices
        # print(self.candidate_list)


if __name__=='__main__':
    size=8
    ai=AI(8,1,5)
    ai2=AI(8,-1,5)
    def show(board):
        for row in board:
            for item in row:
                if item==COLOR_NONE:
                    print('-',end='')
                elif item==COLOR_WHITE:
                    print('@',end='')
                elif item==COLOR_BLACK:
                    print('*',end='')
                else:
                    raise ''
            print('')
    def checkflip(board,pos):
        cnt=0
        color=ai.get(board,pos)
        for dirx in [-1,0,1]:
            for diry in [-1,0,1]:
                if (dirx!=0 or diry!=0):
                    for step in range(1,size):
                        second=(pos[0]+dirx*step,pos[1]+diry*step)
                        if ai.inside(second):
                            if ai.get(board,second)==COLOR_NONE:
                                break
                            elif ai.get(board,second)==color:
                                if step>1:
                                    for t in range(1,step):
                                        board[pos[0]+dirx*t][pos[1]+diry*t]=color
                                        cnt+=1
                                else:
                                    break
                        else:
                            break
        if cnt==0:
            raise 'no flip'
        return board
                                    
    
    
    chessboard=[[0 for _ in range(size)] for _ in range(size)]
    chessboard[3][3]=1
    chessboard[4][4]=1
    chessboard[3][4]=-1
    chessboard[4][3]=-1
    while(True):
        ai.go(chessboard)
        if(len(ai.candidate_list)==0):
            exit()
        ai_choice=ai.candidate_list[-1]
        if chessboard[ai_choice[0]][ai_choice[1]]!=COLOR_NONE:
            raise "duplicated step"
        chessboard[ai_choice[0]][ai_choice[1]]=1
        chessboard=checkflip(chessboard,ai_choice)
        show(chessboard)
        if(False):
            a=int(input('x'))
            b=int(input('y'))
            chessboard[a][b]=-1
            chessboard=checkflip(chessboard,(a,b))
        else:
            ai2.go(chessboard)
            if(len(ai2.candidate_list)==0):
                exit()
            ai2_choice=ai2.candidate_list[-1]
            if chessboard[ai2_choice[0]][ai2_choice[1]]!=COLOR_NONE:
                raise "duplicated step"
            chessboard[ai2_choice[0]][ai2_choice[1]]=-1
            chessboard=checkflip(chessboard,ai2_choice)
        show(chessboard)