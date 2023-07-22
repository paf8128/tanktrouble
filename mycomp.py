I = 1j
def c2t(comp:complex):
    return (comp.real,comp.imag)
def rc2t(comp:complex):
    return (comp.imag,comp.real)
def tint(tup:tuple):
    return tuple(map(int,tup))
def t2c(tup:tuple):
    return complex(tup[0],tup[1])