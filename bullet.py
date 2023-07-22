from mycomp import *
from math import sin,cos,pi,atan2
import pygame
from mymap import *
HW = WALLWIDTH // 2
class Bullet:
    SPEED = 4
    R = 5
    def __init__(self,position:tuple,angle:float):
        self.position = t2c(position)
        self.angle = angle
    def draw(self,screen):
        pygame.draw.circle(screen,(0,0,0),tint(c2t(self.position)),self.R)
    def update(self,map:Map):
        self.position += complex(self.SPEED*cos(self.angle),self.SPEED*sin(self.angle))
        walls,center = map.getByPoint(c2t(self.position))
        if len(walls) == 0:
            ...
        elif len(walls) == 1:
            sign = walls[0]
            sangle = atan2(*rc2t(sign+0j))
            self.bounce(((center-sign*HW+sign*I*HW,sangle+pi*3/4),(center-sign*HW-sign*I*HW,sangle-pi*3/4)),\
                        (center-sign*HW+sign*I*HW,center+sign*(HW+SQSIZE)+sign*I*HW),\
                        (center-sign*HW-sign*I*HW,center+sign*(HW+SQSIZE)-sign*I*HW),\
                        (center-sign*HW+sign*I*HW,center-sign*HW-sign*I*HW))
        elif len(walls) == 2:
            sign1,sign2 = walls
            if sign1+sign2 == 0:
                self.bounce((),\
                            (center+sign1*I*HW+sign1*(HW+SQSIZE),center+sign1*I*HW-sign1*(HW+SQSIZE)),\
                            (center+sign2*I*HW+sign2*(HW+SQSIZE),center+sign2*I*HW-sign2*(HW+SQSIZE)))
            else:
                self.bounce(((center-sign1*HW-sign2*HW,atan2(*rc2t(sign1+sign2))+pi),),\
                            (center-sign1*HW-sign2*HW,center+sign1*(HW+SQSIZE)-sign2*HW),\
                            (center-sign1*HW-sign2*HW,center-sign1*HW+sign2*(HW+SQSIZE)),\
                            *self.getCorner(center,sign1,sign2))
        elif len(walls) == 3:
            sign = list({1,-1,I,-I}-set(walls))[0]
            self.bounce((),\
                        (center+sign*HW+sign*I*(HW+SQSIZE),center+sign*HW-sign*I*(HW+SQSIZE)),\
                        *self.getCorner(center,sign*I,-sign),\
                        *self.getCorner(center,-sign,-I*sign))
        else:
            lines = []
            for c in (1,-1,I,-I):
                lines.extend(self.getCorner(center,c,c*I))
            self.bounce((),lines)
    def getCorner(self,center:complex,sign1,sign2):
        return (center+sign1*HW+sign2*HW,center+sign1*(HW+SQSIZE)+sign2*HW),(center+sign1*HW+sign2*HW,center+sign1*HW+sign2*(HW+SQSIZE))
    def bounce(self,points:tuple,*lines:tuple):
        flag = False
        for line in lines:
            x1,y1 = c2t(line[0])
            x2,y2 = c2t(line[1])
            if x1 == x2:
                if abs(self.position.real-x1) <= self.R and min(y1,y2) <= self.position.imag <= max(y1,y2):
                    self.angle = (pi - self.angle) % (2 * pi)
                    flag = True
            else:
                if abs(self.position.imag-y1) <= self.R and min(x1,x2) <= self.position.real <= max(x1,x2):
                    self.angle = (2 * pi - self.angle)
                    flag = True
        if not flag:
            for point,pangle in points:
                if abs(self.position - point) <= self.R:
                    self.position = point + complex(self.R*cos(pangle),self.R*sin(pangle))
                    self.angle = (2 * pangle - self.angle + pi) % (2*pi)

