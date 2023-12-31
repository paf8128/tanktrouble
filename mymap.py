import pygame
from mycomp import *
from random import randint,choice
SQSIZE = 130
WALLWIDTH = 10
HW = WALLWIDTH // 2
#生成随机地图的生成器
def map_generator():
    check = lambda x:0<=x[0]<cols and 0<=x[1]<rows and sqlist[x[0]][x[1]]==0
    cols,rows = yield None
    while cols != 0:
        sqlist = []
        for c in range(cols):
            sqlist.append([0]*rows)
        walls = []
        for c in range(cols+1):
            for r in range(rows+1):
                #-1代表以c,r为节点向右延伸的横向墙，1代表向下延伸的纵向墙
                if c != cols:
                    walls.append((c,r,-1))
                if r != rows:
                    walls.append((c,r,1))
        count = cols*rows - 1
        #随机选择起始位置
        psq = (randint(0,cols-1),randint(0,rows-1))
        #记录路径
        way = [psq]
        sqlist[psq[0]][psq[1]] = 1
        while count > 0:
            #寻找当前位置上下左右四处未到达过的位置
            goals = []
            for delta in (1+0j,-1+0j,I,-I):
                goal = tint(c2t(t2c(psq)+delta))
                if check(goal):
                    goals.append((goal,(max(goal[0],psq[0]),max(goal[1],psq[1]),int((delta**2).real))))
            #如果未找到，退回上一步
            if len(goals) == 0:
                psq = way[-2]
                way.pop()
                continue
            #否则，前进到其中任意位置，同时打破隔在中间的墙
            count -= 1
            psq,wall = choice(goals)
            sqlist[psq[0]][psq[1]] = 1
            walls.remove(wall)
            way.append(psq)
        #再随机打破剩余的一部分墙，使地图更开阔
        for i in range(cols*rows//5):
            wall = choice(walls)
            if wall[0] != 0 and wall[0] != cols and wall[1] != 0 and wall[1] != rows:
                walls.remove(wall)
        cols,rows = yield walls
def make_generator():
    gene = map_generator()
    next(gene)
    return gene
#地图类
class Map:
    def __init__(self,walls:list,surface:pygame.Surface,rows:int,cols:int,x:int,y:int):
        self.surface = surface
        self.walls = walls
        self.rows = rows
        self.cols = cols
        self.startx = x
        self.starty = y
    def draw(self):
        for wall in self.walls:
            if wall[2] == -1:
                pygame.draw.rect(self.surface,(0,0,0),(wall[0]*SQSIZE+self.startx,wall[1]*SQSIZE+self.starty,SQSIZE+WALLWIDTH,WALLWIDTH))
            if wall[2] == 1:
                pygame.draw.rect(self.surface,(0,0,0),(wall[0]*SQSIZE+self.startx,wall[1]*SQSIZE+self.starty,WALLWIDTH,SQSIZE+WALLWIDTH))
    #根据给定点，寻找距离其最近的节点，返回该节点坐标以及其上的所有墙
    def getByPoint(self,point:tuple):
        col = round((point[0] - WALLWIDTH//2 - self.startx)/SQSIZE)
        row = round((point[1] - WALLWIDTH//2 - self.starty)/SQSIZE)
        walls = []
        for c in [(col,row-1,1,-I),(col-1,row,-1,-1),(col,row,1,I),(col,row,-1,1)]:
            if c[:3] in self.walls:
                walls.append(c[3])
        return walls,complex(col*SQSIZE+WALLWIDTH//2+self.startx,row*SQSIZE+WALLWIDTH//2+self.starty)
