from mymap import *
import json,bullet
pygame.init()
timer = pygame.time.Clock()
with open("propreties/propreties.json") as f:
    data = json.load(f)
cols = randint(data["mincols"],data["maxcols"])
rows = randint(data["minrows"],data["maxrows"])
X = (data["maxcols"] - cols)*SQSIZE//2
Y = (data["maxrows"] - rows)*SQSIZE//2
gene = make_generator()
walls = gene.send((cols,rows))
s = pygame.display.set_mode((data["maxcols"]*SQSIZE+WALLWIDTH,(data["maxrows"]+1)*SQSIZE+WALLWIDTH))
m = Map(walls,s,cols,rows,X,Y)
b = bullet.Bullet((30+X,30+Y),1)
keepgoing = True
pause = False
while keepgoing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            keepgoing = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = not pause
    if pause:
        continue
    s.fill((255,255,255))
    m.draw()
    b.update(m)
    b.draw(s)
    timer.tick(30)
    pygame.display.update()
pygame.quit()