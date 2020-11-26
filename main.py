import pygame
from pygame.rect import *
import random
import math
from pygame.math import Vector2
import pygame_menu
from config import *
pygame.init()

window = pygame.display.set_mode((SCREENWIDTH,SCREENHEIGHT))
window_copy = window.copy()
pygame.display.set_caption('Shockwave Defense')

all_sprites_list = pygame.sprite.Group()
players_list = pygame.sprite.Group()
lasers = pygame.sprite.Group()
bullet_list = pygame.sprite.Group()
background = pygame.image.load(BACKGROUND).convert()
missileTrails = []

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
for i in range(9):
    filename = 'sprites/explosions/regularExplosion0{}.png'.format(i)
    img = pygame.image.load(filename).convert()
    img.set_colorkey(black)
    img_lg = pygame.transform.scale(img, (200,200))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (100,100))
    explosion_anim['sm'].append(img_sm)

missile_images = [ENEMY, ENEMY2]

class Player(pygame.sprite.Sprite):
    
    def __init__(self, locx, locy):
        super().__init__()
        self.image = pygame.image.load(PLAYER).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [locx, locy]
        #self.angle = self.get_angle(pygame.mouse.get_pos())
        self.health = 100
        self.health_bar = ProgressBar(100, 100, (SCREENWIDTH - 30,10), green, gray, [self.rect.x, self.rect.y - 15]) #max_bar, progress, size, barColor, borderColor, position
        players_list.add(self)
        all_sprites_list.add(self)

    def get_angle(self, mouse):
        offset = (mouse[1]-self.rect.centery, mouse[0]-self.rect.centerx)
        self.angle = 270-math.degrees(math.atan2(*offset))
        self.tank_copy = pygame.transform.rotozoom(self.image, self.angle, 1)
        self.rect = self.tank_copy.get_rect(center=self.rect.center)

    def draw(self):
        window.blit(self.tank_copy, self.rect)
        
    def damage(self, x):
        if god != True:
            self.health_bar.progress -= x
            self.health -= x

    def addHealth(self, x):
        self.health_bar.progress += x
        self.health += x   

    def update(self):
        self.health_bar.update([15,5])
        turret.updateTurret(pygame.mouse.get_pos())
        turret2.updateTurret(pygame.mouse.get_pos())
        turret3.updateTurret(pygame.mouse.get_pos())

class Enemy(pygame.sprite.Sprite):
    
    def __init__(self, width, height, speed):
        super().__init__()
        self.image = pygame.image.load(ENEMY).convert_alpha()
        self.rect = self.image.get_rect()
        self.speed = speed
        self.trail = Particles(self.rect.center)
        all_sprites_list.add(self)

    def moveRight(self, pixels):
        self.rect.x += pixels
 
    def moveLeft(self, pixels):
        self.rect.x -= pixels
 
    def moveForward(self, speed):
        self.rect.y += self.speed * speed / 20
 
    def moveBackward(self, speed):
        self.rect.y -= self.speed * speed / 20
 
    def changeSpeed(self, speed):
        self.speed = speed  
    
    def update(self): 
        self.image = pygame.image.load(missile_images[random.randint(0,1)]).convert_alpha()

class Laser(pygame.sprite.Sprite):

    def __init__(self, pos, target):
        super().__init__()
        self.target = target
        self.pos = pos
        self.laser = pygame.draw.line(window, red, self.pos, self.target, 0)
        lasers.add(self)
    
    def draw(self, pos, target):
        self.target = target
        self.pos = pos
        self.laser = pygame.draw.line(window, red, self.pos, self.target, 0)

class Turret(pygame.sprite.Sprite):

    def __init__(self, base, target, player):
        self.player = player
        self.base = base
        self.target = target
        self.original_barrel = pygame.image.load(TURRET).convert_alpha()
        self.barrel = self.original_barrel.copy()
        self.rect = self.barrel.get_rect(center=base.rect.center)
        self.angle = self.get_angle(target)
        if player != 1:
            self.enemy_laser = Laser(self.rect.center, self.target)

    def get_angle(self, mouse):
        offset = (mouse[1]-self.rect.centery, mouse[0]-self.rect.centerx)
        self.angle = 270-math.degrees(math.atan2(*offset))
        self.barrel = pygame.transform.rotozoom(self.original_barrel, self.angle, 1)
        self.rect = self.barrel.get_rect(center=self.rect.center)

    def draw(self):
        if self.player == 1 and laser_sight:
            self.laserx, self.lasery = pygame.mouse.get_pos()
            laser = pygame.draw.line(window, red, (self.rect.centerx, self.rect.centery), (self.laserx,self.lasery), 3)
        if self.player != 1:
            self.enemy_laser.draw(self.rect.center, self.target)
        window.blit(self.barrel, self.rect)


    def addAmmo(self, x):
        self.ammo += x

    def shoot(self):
        bullet = Bullet(self.player)
        bullet.upgrade()
        bullet.rect.center = self.rect.center
        target_x, target_y = self.target
        Bullet.bulletMove(bullet, target_x, target_y, self.rect.centerx, self.rect.centery)

    def updateTurret(self, target):
        self.target = target
        self.image_center = self.rect.center
        self.rect.center= self.base.rect.center
        self.get_angle(self.target)
        self.draw()

    def damage(self, x):
        self.health -= x

    def addHealth(self, x):
        self.health += x   

class Bullet(pygame.sprite.Sprite):

    def __init__(self, player):
        #pygame.mixer.Sound.play(shoot_sound)
        global bulletValue
        self.player = player
        super().__init__()
        bullet_list.add(self)
        all_sprites_list.add(self)
        self.image = pygame.image.load(BULLET).convert_alpha()
        self.bulletSpeed = bulletValue * 5
        self.rect = self.image.get_rect()
        self.change_y = 0
        self.change_x = 0
        self.bounces = 0
        self.save_x = 0
        self.save_y = 0

    def bulletMove (self, cursor_pos_x, cursor_pos_y, player_pos_x, player_pos_y):

        block_vec_x = (cursor_pos_x - player_pos_x)
        block_vec_y = (cursor_pos_y - player_pos_y)
        #vec_length = (block_vec_x**2 + block_vec_y**2)**0.5
        vec_length = 1/4*math.sqrt(block_vec_x ** 2 + block_vec_y ** 2)
        block_vec_y = (block_vec_y / vec_length) * self.bulletSpeed
        block_vec_x = (block_vec_x / vec_length) * self.bulletSpeed
        self.change_y += block_vec_y
        self.change_x += block_vec_x

    def update(self):
        self.rect.centery += self.change_y
        self.rect.centerx += self.change_x

    def upgrade(self):
        global bulletValue, upgrade
        if upgrade == True:
            #bulletValue += 1
            print("Weapon Upgrade")
            upgrade = False

class Explosion(pygame.sprite.Sprite):

    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.center = center
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 60
        all_sprites_list.add(self)
        # if size == 'lg':
        #     pygame.mixer.Sound.play(explosion_sound2)
        # else:
        #     pygame.mixer.Sound.play(explosion_sound)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = self.center

class ProgressBar():

    def __init__(self, max_bar, progress, size, barColor, borderColor, position):
        self.max_bar = max_bar
        self.progress = progress
        self.power = self.progress / self.max_bar
        self.barColor = barColor
        self.borderColor = borderColor
        self.position = position
        self.x , self.y = self.position
        self.size = size

    def draw(self):
        pygame.draw.rect(window, self.borderColor, (*self.position, *self.size), 1)
        innerPos  = (self.position[0]+3, self.position[1]+3)
        innerSize = ((self.size[0]-6) * self.power, self.size[1]-6)
        pygame.draw.rect(window, self.barColor, (*innerPos, *innerSize))

    def update(self, tankPos):
        self.power = self.progress / self.max_bar
        self.position = tankPos
        self.draw()

class Explosion(pygame.sprite.Sprite):

    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.center = center
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 60
        all_sprites_list.add(self)
        # if size == 'lg':
        #     pygame.mixer.Sound.play(explosion_sound2)
        # else:
        #     pygame.mixer.Sound.play(explosion_sound)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = self.center

class Particles():

    def __init__(self, position):
        self.mx, self.my = position
        self.particles = []
        self.particles.append([[self.mx, self.my], [random.randint(0, 20) / 10 - 1, -2], random.randint(4, 6)])
        missileTrails.append(self)
        
    def update(self, position):
        self.particles.append([position, [random.randint(0, 20) / 10 - 1, -5], random.randint(4, 6)])
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.1
            particle[1][1] += 0.1
            pygame.draw.circle(window, (255, 255, 255), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
            if particle[2] <= 0:
                self.particles.remove(particle)


player = Player(300, 500)
player2 = Player(460, 550)
player3 = Player(150, 550)
turret = Turret(player, pygame.mouse.get_pos(), 1)
turret2 = Turret(player2, pygame.mouse.get_pos(), 1)
turret3 = Turret(player3, pygame.mouse.get_pos(), 1)
special_ability = ProgressBar(120, specialAmmo, (100,10), purple, gray, [15, SCREENHEIGHT - 15])

missiles = pygame.sprite.Group()
amount = 0
addDifficulty = 1
level = 0
score = 0
#burstShot = False
def createEnemies():
    global missiles,amount,upgrade, level, addDifficulty
    if not missiles:
        level += 1
        amount += 2 * addDifficulty
        # if amount % 15 == 0:
        #     upgrade = True
        #     #burstShot = True
        # else:
        #     #burstShot = False
        #     upgrade = False
        for x in range(amount):
            enemyTank = Enemy(20,30, random.randint(50,75))
            enemyTank.rect.x = random.randint(50,SCREENWIDTH - 50)
            enemyTank.rect.y = -200
            all_sprites_list.add(enemyTank)
            missiles.add(enemyTank)

clock = pygame.time.Clock()

#Game Run ----------------------
def set_difficulty(value, difficulty):
    global addDifficulty
    print(difficulty)
    if (difficulty == 1):
        addDifficulty = 1
    elif (difficulty == 2):
        addDifficulty = 2
    elif (difficulty == 3):
        addDifficulty = 3

font_name = "font/Chunq.ttf"
def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def set_god(value, mode):
    global god
    if (mode == 1):
        god = False
    elif (mode == 2):
        god = True

def set_mode(value, mode):
    #global infinite
    if (mode == 1):
        infinite = False
    elif (mode == 2):
        infinite = False
    elif (mode == 3):
        infinite = True

def pauseGame():
    ending = True
    while ending:
        global score
        s = pygame.Surface((SCREENWIDTH,SCREENWIDTH))
        s.set_alpha(10)
        s.fill(black)
        window.blit(s, (0,0))
        draw_text(window, "PAUSED", 50, SCREENWIDTH / 2, SCREENHEIGHT / 3, blue)
        draw_text(window, "Press [SPACE] to unpause", 25, SCREENWIDTH / 2, (SCREENHEIGHT / 3) + 250, white)
        draw_text(window, "Press [ESC] to quit", 15, 100, 30, white)
        pygame.display.flip()
        for event in pygame.event.get():
                key = pygame.key.get_pressed()
                if key[pygame.K_ESCAPE]:
                    ending = False
                if key[pygame.K_SPACE]:
                    startGame()
        pygame.display.update()
        clock.tick(60)
    pygame.quit()

def endGame(outcome):
    ending = True
    while ending:
        global score
        s = pygame.Surface((SCREENWIDTH,SCREENWIDTH))
        s.set_alpha(5)
        s.fill(black)
        window.blit(s, (0,0))
        if outcome == 0:
            draw_text(window, "MISSION FAILED", 50, SCREENWIDTH / 2, SCREENHEIGHT / 3, red)
        else:
            draw_text(window, "MISSION ACCOMPLISHED", 50, SCREENWIDTH / 2, SCREENHEIGHT / 3, blue_green)
        
        draw_text(window, "High Score: " + str(score), 25, SCREENWIDTH / 2, (SCREENHEIGHT / 3) + 150, sky_blue)
        draw_text(window, "Press [SPACE] to replay", 25, SCREENWIDTH / 2, (SCREENHEIGHT / 3) + 250, white)
        draw_text(window, "Press [ESC] to quit", 15, 175, 30, white)
        pygame.display.flip()
        for event in pygame.event.get():
                key = pygame.key.get_pressed()
                if key[pygame.K_ESCAPE]:
                    ending = False
                if key[pygame.K_SPACE]:
                    main()
        pygame.display.update()
        clock.tick(60)
    pygame.quit()

mx, my = pygame.mouse.get_pos()
p = Particles([mx,my])
def startGame():
    global score, addDifficulty, specialAmmo
    #global burstShot
    
    running = True
    shooting = False
    specialAmmo = 0
    ability = 'NOT-READY'
    special = False
    while running:
        createEnemies()
        window.blit(background, (0, 0))
        for event in pygame.event.get():
            key = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                running = False
            if key[pygame.K_ESCAPE]:
                pauseGame()
            if specialAmmo == 120:
                ability = 'READY [Press E]'
                key = pygame.key.get_pressed()
                if key[pygame.K_e]:
                    special = True
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):  
                    shooting = True
                    
                elif (event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                    shooting = False
            else:
                ability = 'NOT-READY'
            if event.type == pygame.MOUSEBUTTONDOWN:
                turret.shoot() #PLAYER SHOOTS ------------------------------------------
                turret2.shoot()
                turret3.shoot()

        if (special and specialAmmo != 0):
            specialAmmo -= 10
            turret.shoot()
            special_ability.progress = 0
            turret2.shoot()
            turret3.shoot()
        else:
            special = False

        #logic --------------------------
        for missile in missiles:
            missile.moveForward(speed)
            if missile.rect.y > SCREENHEIGHT - 100:
                player.damage(5)
                exp = Explosion(missile.rect.center, 'sm')
                missile.rect.y = -200
                if player.health <= 0:
                    print("Dead")
                    running=False
                missile.changeSpeed(random.randint(50,75))
            
        for bullet in bullet_list:
            enemy_hit_list = pygame.sprite.spritecollide(bullet, missiles, True)
            if enemy_hit_list:
                print("Enemy Killed")
                exp = Explosion(bullet.rect.center, 'sm')
                score += 100
                if specialAmmo < 120 and special == False:
                    specialAmmo += 5
                    special_ability.progress += 5
                bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)
            if bullet.rect.y < -10 or bullet.rect.y > SCREENHEIGHT:
                bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)

        cursor = pygame.image.load(CURSOR)
        pygame.mouse.set_visible(False)  # hide the cursor
        coordx, coordy = pygame.mouse.get_pos()
        #write this in the loop
        window.blit(cursor, (coordx - 10, coordy - 15))
        special_ability.update([15, SCREENHEIGHT - 15])
        all_sprites_list.update()
        all_sprites_list.draw(window)
        player.update()
        player2.update()
        player3.update()
        for trail in missileTrails:
            trail.update()
        draw_text(window, str("Health: " + str(player.health)), 16, SCREENWIDTH / 2, 25, green)
        draw_text(window, str("Missiles left: " + str(len(missiles))), 16, 100, 25, red)
        #draw_text(window, str("Special Ability: " + ability), 18, 75, SCREENHEIGHT - 50, purple)
        draw_text(window, str("Level: " + str(level)), 16, (SCREENWIDTH - 75), 25, white)
        draw_text(window, str("Score: " + str(score)), 16, SCREENWIDTH / 2, 50, sky_blue)
        pygame.display.update()
        clock.tick(60)

    endGame(0)

def main():
    menu = pygame_menu.Menu(SCREENHEIGHT, SCREENWIDTH, 'Shockwave Defense', theme=pygame_menu.themes.THEME_DARK)
    menu.add_button('Play', startGame)
    #menu.add_text_input('Name :', default='Joe Fignit')
    menu.add_selector('Difficulty:', [('Normal', 1), ('Easy', 2),('Hard', 3)], onchange=set_difficulty)
    menu.add_selector('God Mode:', [('Off', 1), ('On', 2)], onchange=set_god)
    menu.add_button('Quit', pygame_menu.events.EXIT)
    clock.tick(10)
    menu.mainloop(window)

if __name__ == "__main__":
    main()
