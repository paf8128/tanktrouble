from math import atan2,sin,cos,pi
I = 1j
def c2t(comp:complex):
    return (comp.real,comp.imag)
def rc2t(comp:complex):
    return (comp.imag,comp.real)
def tint(tup:tuple):
    return tuple(map(int,tup))
def t2c(tup:tuple):
    return complex(tup[0],tup[1])
#将直角坐标转化为极坐标(向量)
def rect2polar(comp:complex):
    return atan2(*rc2t(comp)),(comp.real**2+comp.imag**2)**0.5