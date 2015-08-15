# program for Spaceship
# got (most) all simplegui statements converted to pygame commands
#rev 10(?): 6 Aug 2015; 0756; got the rock spawner working
#           TODO the right/left arrow keys and the up key (thrust) do not
#           seem to work simultaneously
#Rev 11: 6 Aug 2015, 1425 got the missiles firing from nose of the ship and 
#           missile velocity greater than velocity of the ship
#           TODO parameterize the missile velocity to something like 1.25 or 
#           1.5 velocity of the ship
#Rev 12:  6 Aug 2015, 1527  Fixed the problem with three keys down 
#           simultaneoulsy - 
#           NOTE: have to use the 'q' key (lower case) to fire missiles - not 
#           the space bar as apparently some keyboards will not accept three 
#           keys in near vacinity down together
#Rev 13: 6 Aug 2015, 1833 Got the collision detection working for ship and rocks
#           and rocks and missiles
#rev 14: 7 Aug 2015, 1436 got the rock and missile cull routines working
#rev 15: 8 Aug 2015, 1858 got the explosion working
# TODO make sure the code works for more than one hit/explosion simultaneously
import pygame, sys
from pygame.locals import *

import math
import random

#TODO refresh myself on why doing this
pygame.mixer.pre_init()
pygame.init()

# Define some colors as global constants
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)

# globals for user interface
WIDTH = 800
HEIGHT = 600
FPS = 30
score = 0
lives = 3
timer_debris_fld = 0
rotate_cclockwise = False
rotate_clockwise = False
msl_tgr = False
rock = []  # initialize rock list
msl = []   # initialize missile list
cyclectr = 0 # counter for game loop cycles
# this .set_mode has to come before loading images with '.convert()'
# **NOTE I had to stip off the .convert method from .image.load due to non-transparent
# artifacts being intoduced that degraded the image display
#TODO educate self on why convert did not work as expected
screen = pygame.display.set_mode([WIDTH, HEIGHT])

# load the sound files
b_sound = pygame.mixer.Sound('soundtrack.wav')
t_sound = pygame.mixer.Sound('thrust.wav')
e_sound = pygame.mixer.Sound('explosion.wav')
m_sound = pygame.mixer.Sound('missile.wav')
b_sound.play(-1)  # start the background sound
class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = pygame.image.load("debris2_blue.png")
debris_image = pygame.transform.scale(debris_image, (WIDTH, HEIGHT))    # scale up
#  to fit the entire screen
debris_info = ImageInfo([400, 300], [800, 600])  # reset image center and size for
#  the scaled image
# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = pygame.image.load("nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = pygame.image.load("splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = pygame.image.load("double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = pygame.image.load("shot3.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = pygame.image.load("asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = pygame.image.load("explosion_alpha.png")

ship_image.set_colorkey(WHITE)  # make background areas of image transparent

# sound assets purchased from sounddogs.com, please do not redistribute
#soundtrack = pygame.mixer.Sound("soundtrack.mp3")
missile_sound = pygame.mixer.Sound("missile.wav")
#TODO may have to use Sound.set_volume method
#missile_sound.set_volume(.5)
#TODO have to convert all sound files to .wav
#ship_thrust_sound = pygame.mixer.Sound("thrust.mp3")
#explosion_sound = pygame.mixer.Sound("explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0.5
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        # this variables will be updated as result of rotating the image
        self.csize = self.image_size  # initialize to original image rect size
        
    def draw(self,canvas):
        #self.pos[0] = int(self.pos[0])
        #self.pos[1] = int(self.pos[1])
        self.radius = int(self.radius)
        #print('self.pos (draw rtn): ', self.pos)
       
        if not self.thrust:
            ship_image.set_clip(pygame.Rect(0, 0, 90, 90))
            t_sound.stop()
        else:
            ship_image.set_clip(pygame.Rect(90, 0, 90, 90))
            t_sound.play(-1)
            
        ship_image_cur = ship_image.subsurface(ship_image.get_clip())
        ship_image_now = pygame.transform.rotozoom(ship_image_cur, self.angle, 1)
        #print('self.angle: ', self.angle)
        ship_image_now_r = ship_image_now.get_rect()
        #print(' ship_image_now_rect[0], [1], [2], [3]: ', ship_image_now_r[0], ship_image_now_r[1],
        #      ship_image_now_r[2], ship_image_now_r[3])
        #print('self.pos[0], [1]: ', self.pos[0], self.pos[1])
        
        # update the current size of the image for missile handler
        self.csize = [ship_image_now_r[2], ship_image_now_r[3]]
        
        delta_x = ship_image_now_r[2] // 2
        delta_y = ship_image_now_r[3] // 2             
        canvas.blit(ship_image_now, (int(self.pos[0]) - delta_x, int(self.pos[1]) - delta_y,
                                     ship_image_now_r[2], ship_image_now_r[3]))
        
    def get_angle(self):
        return self.angle
    
    def get_csize(self):
        return self.csize
    
    def get_pos(self):
        return self.pos
    
    def get_radius(self):
            return self.radius    
    
    def update(self):
        # position update
        self.pos[0] = self.pos[0] + self.vel[0]
        self.pos[1] = self.pos[1] + self.vel[1]
        
        # check / adjust for boundry conditions
        if self.pos[0] < 0:
            self.pos[0] = WIDTH
        if self.pos[0] > WIDTH:
            self.pos[0] = 0
        if self.pos[1] < 0:
            self.pos[1] = HEIGHT
        if self.pos[1] > HEIGHT:
            self.pos[1] = 0        
        
        #print('self.pos (center): ', self.pos)
        # friction update
        FRIC = .025
        self.vel[0] = (self.vel[0] * (1 - FRIC))
        self.vel[1] = (self.vel[1] * (1 - FRIC))
        #print('self.vel: ', self.vel)
        
        # thrust update
        # convert self.angle to radians for this calc
        angle_rad = (self.angle * 3.14159) / 180
        forward = [math.cos(angle_rad), -math.sin(angle_rad)]
        #print('self.angle: ', self.angle)
        if self.thrust:
            self.vel[0] = self.vel[0] + forward[0] * .1
            self.vel[1] = self.vel[1] + forward[1] * .1
            #print('self.vel ', self.vel, ' forward: ', forward)
        #print('rotate_cclockwise: ', rotate_cclockwise)
        if rotate_cclockwise:
            self.angle = self.angle + self.angle_vel
            #print('self.angle (counterclockwise): ', self.angle)
        if rotate_clockwise:
            self.angle = self.angle - self.angle_vel
            #print('self.angle (clockwise): ', self.angle)
    
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        #TODO put appropriate pygame sound functions/methods in here
        #if sound:
            #sound.rewind()
            #sound.play()
   
    def set_radius(self, rad):
        self.radius = rad
    
    
    def get_pos(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
   
    def draw(self, canvas):
        #self.pos[0] = int(self.pos[0])
        #self.pos[1] = int(self.pos[1])
        self.radius = int(self.radius)        
        #pygame.draw.circle(canvas, RED, self.pos, self.radius, 0)
        #canvas.blit(self.image, (self.pos, self.image_size))
        # the following transform is needed to make the rocks rotate, and for the long missile to have the proper orientation in flight
        image_now = pygame.transform.rotozoom(self.image, self.angle, 1)
        nimage = image_now.get_rect()
        dlx = nimage[2] // 2
        dly = nimage[3] // 2
        canvas.blit(image_now, (self.pos[0] - dlx, self.pos[1] - dly,
                    nimage[2], nimage[3]))        
    def update(self):
        global  msl_tgr
        # for an asteroid, there will be an ang_vel (degrees/frame cycle)
        # for a missile, ang_vel will be zero
        self.angle = self.angle + self.angle_vel
        self.pos[0] = self.pos[0] + self.vel[0]
        self.pos[1] = self.pos[1] + self.vel[1]
       
           
def draw(canvas):
    global timer_debris_fld

    # animiate background
    timer_debris_fld += 1
    wtime = (timer_debris_fld / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    #print('time: ', timer_debris_fld, ' wtime: ', wtime, ' center: ', center, ' size: ', size)
    canvas.blit(nebula_image, (0, 0, WIDTH, HEIGHT))

    dx = int(wtime)
    dy = int(HEIGHT / 2 - 300)
    
    canvas.blit(debris_image, (dx, dy, WIDTH, HEIGHT))
    dx1 = int(wtime - 800)
    #print('timer_debris_fld: ', timer_debris_fld, ' wtime: ', wtime, ' dx: ', dx, ' dx1: ', dx1)
    canvas.blit(debris_image, (dx1, dy, WIDTH, HEIGHT))
    # draw ship and sprites
    #TODO how do these objects get created ??
    #  It looks like they get initialized in the 'main' function; need to 
    #  recheck, but I think it might run this way
    #my_ship.draw(canvas)
    #a_rock.draw(canvas)
    #a_missile.draw(canvas)
    if len(msl) > 0:
        for item in range(len(msl)):
            #print('length of msl list: ', len(msl))
            msl[item].draw(canvas)
            #print('after msl update')    
    
    # update ship and sprites
    my_ship.update()
    #a_rock.update()
    #a_missile.update()
    #print('cp1 msl_tgr: ', msl_tgr)
    
    if len(msl) > 0:
        for item in range(len(msl)):
            #print('length of msl list: ', len(msl))
            msl[item].update()
            #print('after msl update')
        
    if len(rock) > 0:
        for i in range(len(rock)):
            rock[i].draw(canvas)
            rock[i].update()          
    
    my_ship.draw(canvas)



# timer handler that spawns a rock    
cposr = [0, 0]
velr = [0, 0]
rock = []
def rock_spawner():
    x = random.randint(0, WIDTH)
    cposr[0] = x
    y = random.randint(0, HEIGHT)
    cposr[1] = y
    #print('x: ', x, ' y: ', y)
    velr[0] = (random.randint(-1, 1))
    velr[1] = (random.randint(-1, 1))
    ang_vel = (random.random() - .5) * 10
    
    # what if want to make different sizes
    wh = random.randint(25, 90)
    #print('wh: ', wh)
    scaled_image = pygame.transform.scale(asteroid_image, (wh, wh))
    rock.append(Sprite([cposr[0], cposr[1]], [velr[0], velr[1]], 0, ang_vel, scaled_image, asteroid_info))
    lnth = len(rock)
    #print('lnth: ', lnth)
    rock[lnth-1].set_radius(int(wh/2))    


# routine to show explosion
def do_expl(iex, cex):
    x = iex * 128
    explosion_image.set_clip(pygame.Rect(x, 0, 128, 128))
    ex_image = explosion_image.subsurface(explosion_image.get_clip())
    screen.blit(ex_image, (cex[0]-64, cex[1]-64, 128, 128))
    
    
posnn = [0,0]    
def missile_fire(posn, angle):
    angle_rad = (angle * 3.14159) / 180
    velvector = [math.cos(angle_rad), -math.sin(angle_rad)]  
    # adjust firing position from center of ship to nose of ship
    posnn[0] = int(velvector[0] * 22.5 + posn[0])
    posnn[1] = int(velvector[1] * 22.5 + posn[1])    
    
    #TODO parameterize velvector constant to something like 1.25 the ship velocity
    msl.append(Sprite([posnn[0], posnn[1]], [velvector[0]*7, velvector[1]*7], angle, 0,  missile_image, missile_info))
    #print('msl.append: ', msl)
    #print('length of missile list: ', len(msl))

# The use of the main function is described in Chapter 9.
#def main():
""" Main function for the game. """    

# Set the width and height of the screen [width,height]
#size = [700, 500]


pygame.display.set_caption("Asteroids")

#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()
print('initial cyclectr value: ', cyclectr)
#TODO have to come up with something to replace this timer;
#  maybe something involving pygame.time.set_timer ??
#  variable 'timer' is getting incremented in 'draw' function, apparently
#  every frame
#timer = simplegui.create_timer(1000.0, rock_spawner)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, 0, asteroid_image, asteroid_info)
a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1,1], 0, 0, missile_image, missile_info, m_sound)    
next_launch = 0
next_rspawn = 0
iex = 24
# -------- Main Program Loop -----------
while not done:
    prog_time = pygame.time.get_ticks()  # get program timer for this cycle
    
    # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop
            
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                rotate_cclockwise = True
                rotate_clockwise = False
            if event.key == K_RIGHT:
                rotate_cclockwise = False
                rotate_clockwise = True
            if event.key == K_UP:
                my_ship.thrust = True
            if event.key == K_q:
                #TODO probably need to move this to the update method and keep
                # firing as long as the flag is True; right now it fires only
                # once per key down it appears
                #a_missile.angle = my_ship.get_angle()
                #a_missile.pos = my_ship.get_pos()
            #print('ship size and angle: ', a_missile.pos, a_missile.angle)
                msl_tgr = True
                #missile_fire(a_missile.pos, a_missile.angle)
                
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_LEFT:
                rotate_cclockwise = False
            if event.key == K_RIGHT:
                rotate_clockwise = False
            if event.key == K_UP:
                my_ship.thrust = False
            if event.key == K_q:
                msl_tgr = False
            
    # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT
    #check and spawn missile
    if msl_tgr:
        a_missile.angle = my_ship.get_angle()
        a_missile.pos = my_ship.get_pos()

        # slow down firing rate to about every 200 ms
        if next_launch <= prog_time:
            missile_fire(a_missile.pos, a_missile.angle)
            next_launch = prog_time + 200
    

    #check and spawn rock
    if next_rspawn <= prog_time:
        next_rspawn = next_rspawn + 1000
        rock_spawner()
 
    # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
    #check for collision between spaceship and rocks
    srad = my_ship.get_radius()
    scen = my_ship.get_pos()
    #print('srad and scen: ', srad, scen)
    
    for i in range(len(rock)):
        rrad = rock[i].get_radius()
        rcen = rock[i].get_pos()
        #print('rock: ', i, ' rad and cen: ', rrad, rcen)
        dst = dist(scen, rcen)
        #print('rock: ', i, 'dst: ', dst)
        comborad = rrad + srad
        seperation = dst - comborad
        #print('comborad: ', comborad, 'dist: ', dst, 'sep: ', seperation)
        if seperation < 0:
            print('rock[]: ', i, 'CRASH')
    
    # check for collision between rocks and missiles
    mrad = 3
    rmv_rock_lst = []
    rmv_msl_lst = []
    for i in range(len(rock)):
        rrad = rock[i].get_radius() * .8 # make 'hit' radius a bit smaller than image size
        rcen = rock[i].get_pos()
        for j in range(len(msl)):
            mcen = msl[j].get_pos()
            dst = dist(rcen, mcen)
            comborad = rrad + mrad
            sep = dst - comborad
            if sep < 0:
                #print('rock[i]: ', i, 'missile[]: ', j, 'HIT')
                rmv_rock_lst.append(i)
                rmv_msl_lst.append(j)
                iex = 0  # set counter for explosion
                cexp = rcen
    # remove hit rocks and missiles
    #remove any duplicates in the lists
    a = set(rmv_rock_lst)
    b = set(rmv_msl_lst)
    
    #print('rmv_rock_lst: ', rmv_rock_lst, 'a: ', a)
    #print('rmv_msl_lst: ', rmv_msl_lst, 'a: ', b)
    for i in range(len(rock)-1, -1, -1):
        #print('nr of rocks: ', len(rock), 'len of rmv_rock_list: ', len(rmv_rock_lst))
        for j in a:

            #print('rmv_rock_list: ', rmv_rock_lst)
            if i == j:
                #print('i and j for rocks: ', i, j)
                del rock[i]
    
    for i in range(len(msl)-1, -1, -1):
        for j in b:
            if i == j:
                del msl[i]
        
    # cull the missile list   
    for i in range(len(msl)-1, -1, -1):
        rcen = msl[i].get_pos()
        xout = rcen[0] < 0 or rcen[0] > WIDTH
        yout = rcen[1] < 0 or rcen[1] > HEIGHT
        if xout or yout:
            del msl[i]
            
    # cull the rock list
    for i in range(len(rock)-1, -1, -1):
        rcen = rock[i].get_pos()
        xout = rcen[0] < 0 or rcen[0] > WIDTH
        yout = rcen[1] < 0 or rcen[1] > HEIGHT
        if xout or yout:
            del rock[i]    
    #print('len rock and msl list: ', len(rock), len(msl))
    # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT

    

    # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
    
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    # TODO (recheck this) I think this needs to come out, as we are 
    #  putting up a background image
    #screen.fill(GREEN)
    
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    #my_ship.angle = my_ship.angle + .5
    #print('my ship angle: ', my_ship.angle)
    draw(screen)
    # Go ahead and update the screen with what we've drawn.
    if iex < 24:
        do_expl(iex, cexp)
        iex = iex + 1
    
    pygame.display.update()

    # Limit to 20 frames per second
    clock.tick(FPS)
    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
#sys.exit()
#quit()

#if __name__ == "__main__":
#    main()
