import pygame
pygame.mixer.init()

# Set up screen and screen title --------------------------------------------------------
SCREENWIDTH=600
SCREENHEIGHT=600

# Miscellaneous variables -------------
speed = 1
upgrade = False
bulletValue = 1
laser_sight = False
god = False
specialAmmo = 0
#sprites locations-------------------------------------------------
PLAYER = "sprites/player/player.png"
ENEMY = "sprites/player/missile0.png"
ENEMY2 = "sprites/player/missile1.png"
TURRET = "sprites/player/turret.png"
BACKGROUND = "sprites/level/background.png"
BULLET = "sprites/other/bullet.png"
CURSOR = "sprites/other/cursor.png"

# Usable colors ------------------------------------------------
white = ((255,255,255))
blue = ((0,0,255))
green = ((0,255,0))
red = ((255,0,0))
black = ((0,0,0))
orange = ((255,100,10))
yellow = ((255,255,0))
blue_green = ((0,255,170))
marroon = ((115,0,0))
lime = ((180,255,100))
pink = ((255,100,180))
purple = ((240,0,255))
gray = ((127,127,127))
magenta = ((255,0,230))
brown = ((100,40,0))
forest_green = ((0,50,0))
navy_blue = ((0,0,100))
rust = ((210,150,75))
dandilion_yellow = ((255,200,0))
highlighter = ((255,255,100))
sky_blue = ((0,255,255))
light_gray = ((200,200,200))
dark_gray = ((50,50,50))
tan = ((230,220,170))
coffee_brown =((200,190,140))
moon_glow = ((235,245,255))
