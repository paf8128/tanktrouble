import pygame
import bullet
import propreties
import numpy
from mycomp import *
from mymap import *
def is_acute_angle(angle:float):
    return (0 <= angle <= pi/2 or pi*3/2 <= angle <= 2*pi)
def between(a, b, c):
    return (a <= b <= c) or (c <= b <= a) or (a==c and abs(b-a) <= 1e-3)
class SegmentLine:
    def __init__(self,p1:tuple[int,int],p2:tuple[int,int]):
        self.p1 = p1
        self.p2 = p2
    def if_cross(self,other):
        x1,y1,x2,y2 = self.p1[0], self.p1[1], self.p2[0], self.p2[1]
        x3,y3,x4,y4 = other.p1[0], other.p1[1], other.p2[0], other.p2[1]
        s = numpy.linalg.det(numpy.array(((y1-y2,x1-x2),(y3-y4,x3-x4))))
        if s == 0:
            return False
        #相交
        c1 = numpy.linalg.det(numpy.array(((x2,x1), (y2,y1))))
        c2 = numpy.linalg.det(numpy.array(((x4,x3), (y4,y3))))
        x = numpy.linalg.det(numpy.array(((c1,x1-x2), (c2,x3-x4))))/s
        y = numpy.linalg.det(numpy.array(((c1,y1-y2), (c2,y3-y4))))/s
        if between(x1,x,x2) and between(x3,x,x4) and between(y1,y,y2) and between(y3,y,y4):
            return True
        else:
            return False
    def distance(self,otherp:complex):
        p1_p2 = atan2(self.p2[1]-self.p1[1], self.p2[0]-self.p1[0])
        p1_p3 = rect2polar(otherp-t2c(self.p1))
        p2_p3 = rect2polar(otherp-t2c(self.p2))
        angle1,angle2 = (p1_p2 - p1_p3[0]) % (2*pi),(p1_p2 + pi - p2_p3[0]) % (2*pi)
        if is_acute_angle(angle1) and is_acute_angle(angle2):
            return p1_p3[1]*sin(angle1)
        else:
            return -1

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
    P1,P2,P3,P4,P5,P6,P7,P8,P9,P10 = tuple(map(rect2polar,(-28+20j,-28-20j,28-20j,28-5j,40-5j,40+5j,28+5j,28+20j,15-5j,15+5j)))
    FORWARD,BACK,LEFT,RIGHT = 1,-1,-1,1
    MOVESPEED,TURNSPEED = propreties.data["playermovespeed"],propreties.data["playerturnspeed"]
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
    def getallpoints(self):
        return tuple(map(self.getpoint,(self.P8 ,self.P1, self.P2, self.P3, self.P4, self.P5, self.P6, self.P7)))
    def getrects(self):
        return (Rect(tuple(map(self.getpoint,(self.P1,self.P2,self.P3,self.P8)))),Rect(tuple(map(self.getpoint,(self.P4,self.P5,self.P6,self.P7)))))
    def draw(self,screen:pygame.Surface):
        pygame.draw.polygon(screen,self.color,tuple(map(self.getpixel,(self.P1,self.P2,self.P3,self.P4,self.P5,self.P6,self.P7,self.P8))))
        pygame.draw.polygon(screen,(0,0,0),tuple(map(self.getpixel,(self.P1,self.P2,self.P3,self.P4,self.P5,self.P6,self.P7,self.P8))),2)
        pygame.draw.aaline(screen,(0,0,0),self.getpixel(self.P4),self.getpixel(self.P9),2)
        pygame.draw.aaline(screen,(0,0,0),self.getpixel(self.P7),self.getpixel(self.P10),2)
        pygame.draw.circle(screen,(0,0,0),tint(c2t(self.position)),15,2)
    def update(self,mymap:Map):
        if self.lives <= 0:
            return
        if self.turn_mode != 0:
            self.turn(self.turn_mode,mymap)
        if self.move_mode != 0:
            self.move(self.move_mode,mymap)
    def bounce(self,mymap:Map):
        allpoints = (self.P8 ,self.P1, self.P2, self.P3, self.P4, self.P5, self.P6, self.P7)
        walllines = [SegmentLine(c2t(wall[0]),c2t(wall[1])) for wall in mymap.getLines(*mymap.getWalls(c2t(self.position)))]
        for i in range(-1,7):
            tankline = SegmentLine(self.getpoint(allpoints[i]), self.getpoint(allpoints[i + 1]))
            for wallline in walllines:
                if tankline.if_cross(wallline):
                    return 1
        return 0
        """tankrects = self.getrects()
        wallrects = []
        signs,center  = mymap.getWalls(c2t(self.position))
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
        return False"""
    def add_bullet(self):
        if self.lives <= 0:
            return
        if self.bullets > 0:
            self.bullets -= 1
            return bullet.Bullet(c2t(self.position + complex(34*cos(self.angle),34*sin(self.angle))),self.angle,self)
        return None
    def move(self,mode:int,mymap:Map):
        prepos = self.position
        preangle = self.angle
        self.position += complex(self.MOVESPEED*cos(self.angle),self.MOVESPEED*sin(self.angle))*mode
        result = self.bounce(mymap)
        if result != 0:
            for da in (0.05,-0.05,0.1,-0.1):
                self.angle = (preangle+da)%(2*pi)
                if self.bounce(mymap) == 0:
                    break
            else:
                self.position = prepos
                self.angle = preangle
            """if result == 1:
                self.position = prepos
            else:
                tp,wl = result
                p1_p2 = complex(wl.p2[0]-wl.p1[0],wl.p2[1]-wl.p1[1])
                ep = p1_p2/abs(p1_p2)
                p1_p3 = rect2polar(self.position-t2c(wl.p1))
                angle = (atan2(*rc2t(p1_p2)) - p1_p3[0]) % (2*pi)
                dist = p1_p3[1]*sin(angle)
                disp = p1_p3[1]*cos(angle)*ep+complex(wl.p1[0],wl.p1[1])
                delta2 = tp[1]**2-dist**2
                if delta2 < 0:
                    self.position = prepos
                    return
                newp = disp+(delta2**0.5+1)*ep
                angle2 = (atan2(*rc2t(newp-self.position))-(tp[0]+self.angle))%(2*pi)
                if not is_acute_angle(angle2):
                    newp = disp-(delta2**0.5-1)*ep
                self.angle = (atan2(*rc2t(newp-self.position))-tp[0])%(2*pi)
                if self.bounce(mymap) != 0:
                    self.position = prepos
                    self.angle = preangle"""

            
    def turn(self,mode:int,mymap:Map):
        preangle = self.angle
        prepos = self.position
        self.angle += self.TURNSPEED*mode
        self.angle %= 2*pi
        if self.bounce(mymap):
            for c in (2*I,-2*I,2,-2):
                self.position = prepos+c
                if self.bounce(mymap) == 0:
                    break
            else:
                self.position = prepos
                self.angle = preangle