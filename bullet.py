from mycomp import *
from math import sin,cos,pi,atan2
import pygame,player,propreties
from mymap import *
def is_acute_angle(angle:float):
    return (0 <= angle <= pi/2 or pi*3/2 <= angle <= 2*pi)
class Bullet:
    SPEED = propreties.data["bulletspeed"]
    R = 6
    ALL_TIME = 20*40
    AGGRESSIVE_TIME = ALL_TIME - 10
    def __init__(self,position:tuple,angle:float,owner:player.Player):
        self.position = t2c(position)
        self.angle = angle
        self.effect_time = self.ALL_TIME
        self.owner = owner
    def draw(self,screen):
        pygame.draw.circle(screen,(0,0,0),tint(c2t(self.position)),self.R)
    def is_effect(self):
        return self.effect_time != -1
    def touch_player(self,ply:player.Player):
        #rects = ply.getrects()
        tankpoints = ply.getallpoints()
        for i in range(-1,7):
            if abs(self.position - t2c(tankpoints[i])) < self.R:
                return True
            line = player.SegmentLine(tankpoints[i], tankpoints[i+1])
            if 0 <= line.distance(self.position) <= self.R:
                return True
        return False
        """for rect in rects:
            for point in rect.points:
                if abs(self.position - t2c(point)) < self.R:
                    return True
            for i in range(-1,3):
                p1_p2 = atan2(rect.points[i+1][1] - rect.points[i][1],rect.points[i+1][0] - rect.points[i][0])
                p1_bullet = rect2polar(self.position-t2c(rect.points[i]))
                p2_bullet = rect2polar(self.position-t2c(rect.points[i+1]))
                angle1,angle2 = (p1_p2 - p1_bullet[0]) % (2*pi),(p1_p2 + pi - p2_bullet[0]) % (2*pi)
                if is_acute_angle(angle1) and is_acute_angle(angle2) and abs(p1_bullet[1]*sin(angle1)) <= self.R:
                    return True"""
        return False
    def update(self,mymap:Map,players:tuple[player.Player]):
        if self.effect_time == 0:
            self.owner.bullets += 1
            self.effect_time = -1
            return
        if self.effect_time == -1:
            return
        for ply in players:
            if ply.lives <= 0 or (self.effect_time > self.AGGRESSIVE_TIME and ply is self.owner):
                continue
            if self.touch_player(ply):
                ply.lives -= 1
                self.owner.bullets += 1
                self.effect_time = -1
                return
        #计算子弹的新位置
        self.effect_time -= 1
        self.position += complex(self.SPEED*cos(self.angle),self.SPEED*sin(self.angle))
        walls,center = mymap.getWalls(c2t(self.position))
        #判断离子弹最近的所有墙所组成的结构，将墙体结构简化为点与线的组合，交给bounce函数分析
        lines,points = mymap.getLines(walls,center),mymap.getPoints(walls,center)
        self.bounce(points,lines)
    def getCorner(self,center:complex,sign1,sign2):
        return [(center+sign1*HW+sign2*HW,center+sign1*(HW+SQSIZE)+sign2*HW),(center+sign1*HW+sign2*HW,center+sign1*HW+sign2*(HW+SQSIZE))]
    def bounce(self,points:tuple,lines:tuple):
        flag = False
        for line in lines:
            x1,y1 = c2t(line[0])
            x2,y2 = c2t(line[1])
            if x1 == x2:
                #与纵向墙相撞
                if abs(self.position.real-x1) <= self.R and min(y1,y2) <= self.position.imag <= max(y1,y2):
                    self.angle = (pi - self.angle) % (2 * pi)
                    flag = True
            else:
                #与横向墙相撞
                if abs(self.position.imag-y1) <= self.R and min(x1,x2) <= self.position.real <= max(x1,x2):
                    self.angle = (2 * pi - self.angle)
                    flag = True
        #如果未与横纵向墙相撞，分析与墙角(点)相撞的情形
        if not flag:
            #pangle是update函数传入的参数，表示出子弹若与墙角(点)相撞时，其方向应与何对称轴对称
            for point,pangle in points:
                if abs(self.position - point) <= self.R:
                    self.position = point + complex(self.R*cos(pangle)*(2**0.5),self.R*sin(pangle)*(2**0.5))
                    self.angle = (2 * pangle - self.angle + pi) % (2*pi)

