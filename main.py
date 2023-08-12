from mymap import *
from mycomp import *
from random import randint,random
import json
import bullet,player
pygame.init()
font = pygame.font.Font("propreties/simkai.ttf",SQSIZE - 40)
timer = pygame.time.Clock()
with open("propreties/propreties.json") as f:
    data = json.load(f)
waittime = 0
gene = make_generator()
width,height = data["maxcols"]*SQSIZE+WALLWIDTH,(data["maxrows"]+1)*SQSIZE+WALLWIDTH
screen = pygame.display.set_mode((width,height))
p1 = player.Player((255,0,0))
p2 = player.Player((0,255,0))
players = (p1,p2)
keepgoing = True
pause = False
effect_bullets = []
while keepgoing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            keepgoing = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = not pause
            elif event.key == pygame.K_s:
                p1.turn_mode = player.Player.LEFT
            elif event.key == pygame.K_f:
                p1.turn_mode = player.Player.RIGHT
            elif event.key == pygame.K_e:
                p1.move_mode = player.Player.FORWARD
            elif event.key == pygame.K_d:
                p1.move_mode = player.Player.BACK
            elif event.key == pygame.K_q:
                if newb := p1.add_bullet():
                    effect_bullets.append(newb)
            elif event.key == pygame.K_LEFT:
                p2.turn_mode = player.Player.LEFT
            elif event.key == pygame.K_RIGHT:
                p2.turn_mode = player.Player.RIGHT
            elif event.key == pygame.K_UP:
                p2.move_mode = player.Player.FORWARD
            elif event.key == pygame.K_DOWN:
                p2.move_mode = player.Player.BACK
            elif event.key == pygame.K_m:
                if newb := p2.add_bullet():
                    effect_bullets.append(newb)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s:
                p1.turn_mode = 0
            elif event.key == pygame.K_f:
                p1.turn_mode = 0
            elif event.key == pygame.K_e:
                p1.move_mode = 0
            elif event.key == pygame.K_d:
                p1.move_mode = 0
            elif event.key == pygame.K_LEFT:
                p2.turn_mode = 0
            elif event.key == pygame.K_RIGHT:
                p2.turn_mode = 0
            elif event.key == pygame.K_UP:
                p2.move_mode = 0
            elif event.key == pygame.K_DOWN:
                p2.move_mode = 0
    screen.fill((255,255,255))
    alive_players = []
    for ply in players:
        if ply.lives > 0:
            alive_players.append(ply)
            ply.update(game_map)
            ply.draw(screen)
    for b in effect_bullets.copy():
        if b.is_effect():
            b.update(game_map,(p1,p2))
            b.draw(screen)
        else:
            effect_bullets.remove(b)
    if len(alive_players) <= 1 and waittime == -1:
        waittime = 40*3
    if waittime > 0:
        waittime -= 1
    if waittime == 0:
        waittime = -1
        if len(alive_players) == 1:
            alive_players[0].score += 1
        effect_bullets.clear()
        cols = randint(data["mincols"],data["maxcols"])
        rows = randint(data["minrows"],data["maxrows"])
        startx = (data["maxcols"] - cols)*SQSIZE//2
        starty = (data["maxrows"] - rows)*SQSIZE//2
        walls = gene.send((cols,rows))
        game_map = Map(walls,screen,cols,rows,startx,starty)
        p1.newgame(complex(randint(0,cols-1)*SQSIZE+70+startx,randint(0,rows-1)*SQSIZE+70+starty),random()*2*pi)
        p2.newgame(complex(randint(0,cols-1)*SQSIZE+70+startx,randint(0,rows-1)*SQSIZE+70+starty),random()*2*pi)
    screen.blit(font.render(f"红方:{players[0].score}",True,(255,0,0)),(width//8,height-SQSIZE+20))
    screen.blit(font.render(f"绿方:{players[1].score}",True,(0,255,0)),(width*5//8,height-SQSIZE+20))
    game_map.draw()
    timer.tick(40)
    pygame.display.update()
pygame.quit()