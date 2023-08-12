import pygame
import bullet
from mycomp import *
from mymap import *
class Rect:
    #将一个矩形转换成c1<=a1x+b1y<=d1,c2<=a2x+b2y<=d2两不等式的形式
    def __init__(self,points:tuple[tuple,tuple]):
        self.points = points
        if points[0][0] == points[1][0]:
            self.a1,self.b1,self.c1,self.d1 = 1,0,min(points[0][0],points[2][0]),max(points[0][0],points[2][0])
            self.a2,self.b2,self.c2,self.d2 = 0,1,min(points[0][1],points[2][1]),max(points[0][1],points[2][1])
        elif points[0][1] == points[1][1]:
            self.a1,self.b1,self.c1,self.d1 = 0,1,min(points[0][1],points[2][1]),max(points[0][1],points[2][1])
            self.a2,self.b2,self.c2,self.d2 = 1,0,min(points[0][0],points[2][0]),max(points[0][0],points[2][0])
        else:
            self.b1,self.b2,self.a1,self.a2 = 1,1,(points[1][1]-points[0][1])/(points[0][0]-points[1][0]),(points[2][1]-points[1][1])/(points[1][0]-points[2][0])
            cd1,cd2 = (self.a1*points[0][0]+points[0][1],self.a1*points[2][0]+points[2][1]),(self.a2*points[0][0]+points[0][1],self.a2*points[2][0]+points[2][1])
            self.c1,self.d1,self.c2,self.d2 = min(cd1),max(cd1),min(cd2),max(cd2)
    #检测一个点是否在矩形内
    def inRect(self,point:tuple):
        x,y = point
        return (self.c1 <= self.a1*x+self.b1*y <= self.d1) and (self.c2 <= self.a2*x+self.b2*y <= self.d2)
    def __repr__(self):
        return f"{self.c1}<={self.a1}x+{self.b1}y<={self.d1},{self.c2}<={self.a2}x+{self.b2}y<={self.d2}"
class Player:
    #定义坦克各端点与其中心的位置关系
    P1,P2,P3,P4,P5,P6,P7,P8,P9,P10 = tuple(map(rect2polar,(-28+22j,-28-22j,28-22j,28-6j,40-6j,40+6j,28+6j,28+22j,15-6j,15+6j)))
    FORWARD,BACK,LEFT,RIGHT = 1,-1,-1,1
    MOVESPEED,TURNSPEED = 3.5,0.06
    def __init__(self,color:tuple):
        self.color = color
        self.score = 0
        self.lives = -1
        self.position = -10-10j
    def newgame(self,pos:complex,angle:float):
        self.angle = angle
        self.position = pos
        self.bullets = 5
        self.lives = 1
        self.turn_mode,self.move_mode = 0,0
    #通过坦克中心位置与其方向计算出各端点实际位置
    def getpoint(self,pn):
        angle = (pn[0]+self.angle)%(2*pi)
        return c2t(self.position + complex(pn[1]*cos(angle),pn[1]*sin(angle)))
    def getpixel(self,pn):
        angle = (pn[0]+self.angle)%(2*pi)
        return tint(c2t(self.position + complex(pn[1]*cos(angle),pn[1]*sin(angle))))
    def getrects(self):
        return (Rect(tuple(map(self.getpoint,(self.P1,self.P2,self.P3,self.P8)))),Rect(tuple(map(self.getpoint,(self.P4,self.P5,self.P6,self.P7)))))
    def draw(self,screen:pygame.Surface):
        pygame.draw.polygon(screen,self.color,tuple(map(self.getpixel,(self.P1,self.P2,self.P3,self.P4,self.P5,self.P6,self.P7,self.P8))))
        pygame.draw.polygon(screen,(0,0,0),tuple(map(self.getpixel,(self.P1,self.P2,self.P3,self.P4,self.P5,self.P6,self.P7,self.P8))),2)
        pygame.draw.aaline(screen,(0,0,0),self.getpixel(self.P4),self.getpixel(self.P9),2)
        pygame.draw.aaline(screen,(0,0,0),self.getpixel(self.P7),self.getpixel(self.P10),2)
        pygame.draw.circle(screen,(0,0,0),tint(c2t(self.position)),15,1)
    def update(self,mymap:Map):
        if self.turn_mode != 0:
            self.turn(self.turn_mode,mymap)
        if self.move_mode != 0:
            self.move(self.move_mode,mymap)
    def bounce(self,mymap:Map):
        tankrects = self.getrects()
        wallrects = []
        signs,center  = mymap.getByPoint(c2t(self.position))
        for sign in signs:
            wallrects.append(Rect(tuple(map(c2t,(center-sign*HW-sign*I*HW,\
                                                 center-sign*HW+sign*I*HW,\
                                                 center+sign*(SQSIZE+HW)+sign*I*HW,\
                                                 center+sign*(SQSIZE+HW)-sign*I*HW,)))))
            
        for tankpoint in tankrects[0].points+tankrects[1].points:
            for wallrect in wallrects:
                if wallrect.inRect(tankpoint):
                    return True
        for wallrect in wallrects:
            for wallpoint in wallrect.points:
                if tankrects[0].inRect(wallpoint) or tankrects[1].inRect(wallpoint):
                    return True
        return False
    def add_bullet(self):
        if self.bullets > 0:
            self.bullets -= 1
            return bullet.Bullet(c2t(self.position + complex(34*cos(self.angle),34*sin(self.angle))),self.angle,self)
        return None
    def move(self,mode:int,mymap:Map):
        prepos = self.position
        self.position += complex(self.MOVESPEED*cos(self.angle),self.MOVESPEED*sin(self.angle))*mode
        if self.bounce(mymap):
            self.position = prepos
    def turn(self,mode:int,mymap:Map):
        preangle = self.angle
        self.angle += self.TURNSPEED*mode
        self.angle %= 2*pi
        if self.bounce(mymap):
            self.angle = preangle