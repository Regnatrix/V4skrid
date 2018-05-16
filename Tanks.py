#Sandra Dögg Kristmundsdóttir
#7.4.18

import pygame
import random
import math
GRAD = math.pi / 180  # 2 * pi / 360


class Config ( object ):
    fullscreen = False
    width = 800
    height = 600
    bigmapwidth = 1024
    bigmapheight = 800
    fps = 60
    xtiles = 15
    ytiles = 15
    title = "Esc: quit"
    scrollstepx = 3
    scrollstepy = 3
    cornerpoint = [ 0, 0 ]
    radarmapwidth = 200
    radarmapheight = 150


class Text ( pygame.sprite.Sprite ):
    number = 0
    book = {}

    def __init__(self, pos, msg):
        self.number = Text.number
        Text.number += 1
        Text.book[ self.number ] = self
        pygame.sprite.Sprite.__init__ ( self, self.groups )
        self.pos = [ 0.0, 0.0 ]
        self.pos[ 0 ] = pos[ 0 ]
        self.pos[ 1 ] = pos[ 1 ]
        self.msg = msg
        self.changemsg ( msg )

    def update(self, seconds):
        pass

    def changemsg(self, msg):
        self.msg = msg
        self.image = write ( self.msg )
        self.rect = self.image.get_rect ()
        self.rect.centerx = self.pos[ 0 ]
        self.rect.centery = self.pos[ 1 ]


class Bullet ( pygame.sprite.Sprite ):
    side = 7
    vel = 180
    mass = 50
    maxlifetime = 10.0
    book = {}
    number = 0

    def __init__(self, boss):
        pygame.sprite.Sprite.__init__ ( self, self.groups )
        self.boss = boss
        self.number = Bullet.number
        Bullet.number += 1
        Bullet.book[ self.number ] = self
        self.dx = 0
        self.dy = 0
        self.angle = 0
        self.tracer = False
        self.lifetime = 0.0
        self.color = self.boss.color
        self.calculate_heading ()
        self.dx += self.boss.dx
        self.dy += self.boss.dy
        self.pos = self.boss.pos[ : ]
        self.calculate_origin ()
        self.update ()

    def calculate_heading(self):
        self.radius = Bullet.side
        self.angle += self.boss.turretAngle
        self.mass = Bullet.mass
        self.vel = Bullet.vel
        image = pygame.Surface ( (Bullet.side * 2, Bullet.side) )
        image.fill ( (128, 128, 128) )
        pygame.draw.rect ( image, self.color, (0, 0, int ( Bullet.side * 1.5 ), Bullet.side) )
        pygame.draw.circle ( image, self.color, (int ( self.side * 1.5 ), self.side // 2), self.side // 2 )
        pygame.draw.circle ( image, (0, 0, 0), (int ( Bullet.side * 1.5 ), Bullet.side // 2), 2 )
        image.set_colorkey ( (128, 128, 128) )
        self.image0 = image.convert_alpha ()
        self.image = pygame.transform.rotate ( self.image0, self.angle )
        self.rect = self.image.get_rect ()
        self.dx = math.cos ( degrees_to_radians ( self.boss.turretAngle ) ) * self.vel
        self.dy = math.sin ( degrees_to_radians ( -self.boss.turretAngle ) ) * self.vel

    def calculate_origin(self):
        self.pos[ 0 ] += math.cos ( degrees_to_radians ( self.boss.turretAngle ) ) * (Tank.side - 20)
        self.pos[ 1 ] += math.sin ( degrees_to_radians ( -self.boss.turretAngle ) ) * (Tank.side - 20)

    def kill(self):
        del Bullet.book[ self.number ]
        pygame.sprite.Sprite.kill ( self )

    def update(self, seconds=0.0):

        self.lifetime += seconds
        if self.lifetime > Bullet.maxlifetime:
            self.kill ()

        self.pos[ 0 ] += self.dx * seconds
        self.pos[ 1 ] += self.dy * seconds

        if self.pos[ 0 ] < 0:
            self.kill ()
        elif self.pos[ 0 ] > Config.bigmapwidth:
            self.kill ()
        if self.pos[ 1 ] < 0:
            self.kill ()
        elif self.pos[ 1 ] > Config.bigmapheight:
            self.kill ()
        self.rect.centerx = round ( self.pos[ 0 ] - Config.cornerpoint[ 0 ], 0 )
        self.rect.centery = round ( self.pos[ 1 ] - Config.cornerpoint[ 1 ], 0 )


class Tracer ( Bullet ):
    side = 15
    vel = 200
    mass = 10
    color = (200, 0, 100)
    maxlifetime = 10.0

    def __init__(self, boss, turret=False):
        self.turret = turret
        Bullet.__init__ ( self, boss )
        self.tracer = True

    def calculate_heading(self):
        self.angle = 0
        self.angle += self.boss.tankAngle
        if self.turret:
            self.angle = self.boss.turretAngle
        self.mass = Tracer.mass
        self.vel = Tracer.vel
        image = pygame.Surface ( (Tracer.side, Tracer.side // 4) )
        image.fill ( self.boss.color )
        pygame.draw.rect ( image, (0, 0, 0), (Tracer.side * .75, 0, Tracer.side, Tracer.side // 4) )
        image.set_colorkey ( (128, 128, 128) )
        self.image0 = image.convert_alpha ()
        self.image = pygame.transform.rotate ( self.image0, self.angle )
        self.rect = self.image.get_rect ()
        if self.turret:
            self.dx = math.cos ( degrees_to_radians ( self.boss.turretAngle ) ) * self.vel
            self.dy = math.sin ( degrees_to_radians ( -self.boss.turretAngle ) ) * self.vel
        else:
            self.dx = math.cos ( degrees_to_radians ( self.boss.tankAngle ) ) * self.vel
            self.dy = math.sin ( degrees_to_radians ( -self.boss.tankAngle ) ) * self.vel

    def calculate_origin(self):
        if self.turret:
            self.pos[ 0 ] += math.cos ( degrees_to_radians ( -90 + self.boss.turretAngle ) ) * 15
            self.pos[ 1 ] += math.sin ( degrees_to_radians ( 90 - self.boss.turretAngle ) ) * 15
        else:
            self.pos[ 0 ] += math.cos ( degrees_to_radians ( 30 + self.boss.tankAngle ) ) * (Tank.side / 2)
            self.pos[ 1 ] += math.sin ( degrees_to_radians ( -30 - self.boss.tankAngle ) ) * (Tank.side / 2)



class Radarmap ( pygame.sprite.Sprite ):

    def __init__(self):
        pygame.sprite.Sprite.__init__ ( self, self.groups )
        self.image = pygame.Surface ( (Config.radarmapwidth, Config.radarmapheight) )
        self.paintmap ()
        self.rect = self.image.get_rect ()
        self.rect.topleft = (Config.width - Config.radarmapwidth, 0)
        self.factorx = Config.radarmapwidth * 1.0 / Config.bigmapwidth
        self.factory = Config.radarmapheight * 1.0 / Config.bigmapheight

    def paintmap(self):
        self.image.fill ( (0, 0, 0) )
        pygame.draw.rect ( self.image, (150, 0, 0), (0, 0, Config.radarmapwidth, Config.radarmapheight), 1 )

    def update(self, seconds):
        self.paintmap ()
        pygame.draw.rect ( self.image, (255, 255, 255), (round ( Config.cornerpoint[ 0 ] * self.factorx, 0 ),
                                                         round ( Config.cornerpoint[ 1 ] * self.factory, 0 ),
                                                         round ( Config.width * self.factorx, 0 ),
                                                         round ( Config.height * self.factory, 0 )), 1 )
        for tanknumber in Tank.book:
            pos = Tank.book[ tanknumber ].pos
            color = Tank.book[ tanknumber ].color
            pygame.draw.circle ( self.image, color, (int ( pos[ 0 ] * self.factorx ),
                                                     int ( pos[ 1 ] * self.factory )), 4 )
        for bulletnumber in Bullet.book:
            if Bullet.book[ bulletnumber ].tracer:
                dotlength = 2
            else:
                dotlength = 4
            pos = Bullet.book[ bulletnumber ].pos
            color = Bullet.book[ bulletnumber ].color
            pygame.draw.rect ( self.image, color, (int ( pos[ 0 ] * self.factorx ),
                                                   int ( pos[ 1 ] * self.factory ),
                                                   dotlength, dotlength) )


class Tank ( pygame.sprite.Sprite ):
    side = 100
    recoiltime = 0.75
    mgrecoiltime = 0.2
    turretTurnSpeed = 50
    tankTurnSpeed = 80
    movespeed = 80
    # maxrotate = 360
    book = {}
    number = 0
    # keys for tank control, expand if you need more tanks
    #          player1,        player2    etc
    firekey = (pygame.K_f, pygame.K_LEFT)
    mgfirekey = (pygame.K_g, pygame.K_DOWN)
    mg2firekey = (pygame.K_h, pygame.K_RIGHT)
    turretLeftkey = (pygame.K_v, pygame.K_KP4)
    turretRightkey = (pygame.K_b, pygame.K_KP6)
    forwardkey = (pygame.K_w, pygame.K_KP5)
    backwardkey = (pygame.K_s, pygame.K_KP2)
    tankLeftkey = (pygame.K_a, pygame.K_KP1)
    tankRightkey = (pygame.K_d, pygame.K_KP3)
    color = ((200, 200, 0), (100, 100, 255))


    def __init__(self, startpos=(150, 150), angle=0):
        self.number = Tank.number
        Tank.number += 1
        Tank.book[ self.number ] = self
        pygame.sprite.Sprite.__init__ ( self, self.groups )
        self.pos = [ startpos[ 0 ], startpos[ 1 ] ]
        self.dx = 0
        self.dy = 0
        self.ammo = 30
        self.mgammo = 500
        self.color = Tank.color[ self.number ]
        self.turretAngle = angle
        self.tankAngle = angle
        self.msg = "tank%i: x:%i y:%i facing: turret:%i tank:%i" % (
        self.number, self.pos[ 0 ], self.pos[ 1 ], self.turretAngle, self.tankAngle)
        self.firekey = Tank.firekey[ self.number ]
        self.mgfirekey = Tank.mgfirekey[ self.number ]
        self.mg2firekey = Tank.mg2firekey[ self.number ]
        self.turretLeftkey = Tank.turretLeftkey[ self.number ]
        self.turretRightkey = Tank.turretRightkey[ self.number ]
        self.forwardkey = Tank.forwardkey[ self.number ]
        self.backwardkey = Tank.backwardkey[ self.number ]
        self.tankLeftkey = Tank.tankLeftkey[ self.number ]
        self.tankRightkey = Tank.tankRightkey[ self.number ]
        image = pygame.Surface ( (Tank.side, Tank.side) )
        image.fill ( (128, 128, 128) )
        if self.side > 10:
            pygame.draw.rect ( image, self.color, (5, 5, self.side - 10, self.side - 10) )
            pygame.draw.rect ( image, (90, 90, 90), (0, 0, self.side // 6, self.side) )
            pygame.draw.rect ( image, (90, 90, 90),
                               (self.side - self.side // 6, 0, self.side, self.side) )
            pygame.draw.rect ( image, (255, 0, 0), (self.side // 6 + 5, 10, 10, 5) )
        pygame.draw.circle ( image, (255, 0, 0), (self.side // 2, self.side // 2), self.side // 3,
                             2 )
        image = pygame.transform.rotate ( image, -90 )
        self.image0 = image.convert_alpha ()
        self.image = image.convert_alpha ()
        self.rect = self.image0.get_rect ()
        self.firestatus = 0.0
        self.mgfirestatus = 0.0
        self.mg2firestatus = 0.0
        self.turndirection = 0
        self.tankturndirection = 0
        self.movespeed = Tank.movespeed
        self.turretTurnSpeed = Tank.turretTurnSpeed
        self.tankTurnSpeed = Tank.tankTurnSpeed
        Turret ( self )

    def update(self, seconds):
        if self.firestatus > 0:
            self.firestatus -= seconds
            if self.firestatus < 0:
                self.firestatus = 0
        if self.mgfirestatus > 0:
            self.mgfirestatus -= seconds
            if self.mgfirestatus < 0:
                self.mgfirestatus = 0
        if self.mg2firestatus > 0:
            self.mg2firestatus -= seconds
            if self.mg2firestatus < 0:
                self.mg2firestatus = 0


        pressedkeys = pygame.key.get_pressed ()

        self.turndirection = 0
        if pressedkeys[ self.turretLeftkey ]:
            self.turndirection += 1
        if pressedkeys[ self.turretRightkey ]:
            self.turndirection -= 1

        self.tankturndirection = 0
        if pressedkeys[ self.tankLeftkey ]:
            self.tankturndirection += 1
        if pressedkeys[ self.tankRightkey ]:
            self.tankturndirection -= 1

        # ---------------- rotate tank ---------------
        self.tankAngle += self.tankturndirection * self.tankTurnSpeed * seconds

        oldcenter = self.rect.center
        oldrect = self.image.get_rect ()
        self.image = pygame.transform.rotate ( self.image0, self.tankAngle )
        self.rect = self.image.get_rect ()
        self.rect.center = oldcenter

        self.turretAngle += self.tankturndirection * self.tankTurnSpeed * seconds + self.turndirection * self.turretTurnSpeed * seconds  # time-based turning

        if (self.firestatus == 0) and (self.ammo > 0):
            if pressedkeys[ self.firekey ]:
                self.firestatus = Tank.recoiltime
                Bullet ( self )
                self.ammo -= 1

        if (self.mgfirestatus == 0) and (self.mgammo > 0):
            if pressedkeys[ self.mgfirekey ]:
                self.mgfirestatus = Tank.mgrecoiltime
                Tracer ( self, False )
                self.mgammo -= 1
        # -------- fire turret mg ---------------
        if (self.mg2firestatus == 0) and (self.mgammo > 0):
            if pressedkeys[ self.mg2firekey ]:
                self.mg2firestatus = Tank.mgrecoiltime
                Tracer ( self, True )
                self.mgammo -= 1
        # ---------- movement ------------
        self.dx = 0
        self.dy = 0
        self.forward = 0
        if pressedkeys[ self.forwardkey ]:
            self.forward += 1
        if pressedkeys[ self.backwardkey ]:
            self.forward -= 1
        if self.forward == 1:
            self.dx = math.cos ( degrees_to_radians ( self.tankAngle ) ) * self.movespeed
            self.dy = -math.sin ( degrees_to_radians ( self.tankAngle ) ) * self.movespeed
        if self.forward == -1:
            self.dx = -math.cos ( degrees_to_radians ( self.tankAngle ) ) * self.movespeed
            self.dy = math.sin ( degrees_to_radians ( self.tankAngle ) ) * self.movespeed

        self.pos[ 0 ] += self.dx * seconds
        self.pos[ 1 ] += self.dy * seconds
        if self.pos[ 0 ] + self.side / 2 >= Config.bigmapwidth:
            self.pos[ 0 ] = Config.bigmawidth - self.side / 2
            self.dx = 0
        elif self.pos[ 0 ] - self.side / 2 <= 0:
            self.pos[ 0 ] = 0 + self.side / 2
            self.dx = 0
        if self.pos[ 1 ] + self.side / 2 >= Config.bigmapheight:
            self.pos[ 1 ] = Config.bigmapheight - self.side / 2
            self.dy = 0
        elif self.pos[ 1 ] - self.side / 2 <= 0:
            self.pos[ 1 ] = 0 + self.side / 2
            self.dy = 0

        self.rect.centerx = round ( self.pos[ 0 ] - Config.cornerpoint[ 0 ], 0 )  # x
        self.rect.centery = round ( self.pos[ 1 ] - Config.cornerpoint[ 1 ], 0 )  # y
        # self.msg =  "tank%i: x:%i y:%i facing: turret:%i tank:%i"  % (self.number, self.pos[0], self.pos[1], self.turretAngle, self.tankAngle )

    def aim_at_player(self, targetnumber=0):
        deltax = Tank.book[ targetnumber ].pos[ 0 ] - self.pos[ 0 ]
        deltay = Tank.book[ targetnumber ].pos[ 1 ] - self.pos[ 1 ]
        angle = math.atan2 ( -deltax, -deltay ) / math.pi * 180.0

        diff = (angle - self.turretAngle - 90) % 360
        diff -= 180
        if abs ( diff ) < 2:
            self.turndirection = 0
        elif diff > 0:
            self.turndirection = 1
        else:
            self.turndirection = -1


class Turret ( pygame.sprite.Sprite ):
    """turret on top of tank"""

    def __init__(self, boss):
        pygame.sprite.Sprite.__init__ ( self, self.groups )
        self.boss = boss
        self.side = self.boss.side
        self.images = {}
        self.images[ 0 ] = self.draw_cannon ( 0 )
        self.images[ 1 ] = self.draw_cannon ( 1 )
        self.images[ 2 ] = self.draw_cannon ( 2 )
        self.images[ 3 ] = self.draw_cannon ( 3 )
        self.images[ 4 ] = self.draw_cannon ( 4 )
        self.images[ 5 ] = self.draw_cannon ( 5 )
        self.images[ 6 ] = self.draw_cannon ( 6 )
        self.images[ 7 ] = self.draw_cannon ( 7 )
        self.images[ 8 ] = self.draw_cannon ( 8 )
        self.images[ 9 ] = self.draw_cannon ( 4 )
        self.images[ 10 ] = self.draw_cannon ( 0 )

    def update(self, seconds):
        if self.boss.firestatus > 0:
            self.image = self.images[ int ( self.boss.firestatus // (Tank.recoiltime / 10.0) ) ]
        else:
            self.image = self.images[ 0 ]

        oldrect = self.image.get_rect ()
        self.image = pygame.transform.rotate ( self.image, self.boss.turretAngle )
        self.rect = self.image.get_rect ()
        self.rect = self.image.get_rect ()
        self.rect.center = self.boss.rect.center

    def draw_cannon(self, offset):
        image = pygame.Surface ( (self.boss.side * 2, self.boss.side * 2) )
        image.fill ( (128, 128, 128) )
        pygame.draw.circle ( image, (255, 0, 0), (self.side, self.side), 22, 0 )
        pygame.draw.circle ( image, (0, 255, 0), (self.side, self.side), 18, 0 )
        pygame.draw.rect ( image, (255, 0, 0), (self.side - 10, self.side + 10, 15, 2) )
        pygame.draw.rect ( image, (0, 255, 0),
                           (self.side - 20 - offset, self.side - 5, self.side - offset, 10) )
        pygame.draw.rect ( image, (255, 0, 0), (self.side - 20 - offset, self.side - 5, self.side - offset, 10),
                           1 )
        image.set_colorkey ( (128, 128, 128) )
        return image






def radians_to_degrees(radians):
    return (radians / math.pi) * 180.0


def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)


def write(msg="pygame is cool"):
    myfont = pygame.font.SysFont ( "None", 28 )
    mytext = myfont.render ( msg, True, (255, 255, 255) )
    mytext = mytext.convert_alpha ()
    return mytext



def main():

    pygame.init ()
    screen = pygame.display.set_mode ( (Config.width, Config.height) )
    bigmap = pygame.Surface ( (Config.bigmapwidth, Config.bigmapheight) )

    bigmap.fill ( (128, 128, 128) )
    for x in range ( 0, Config.bigmapwidth, Config.bigmapwidth // Config.xtiles ):
        pygame.draw.line ( bigmap, (64, 64, 64), (x, 0), (x, Config.bigmapheight) )
    for y in range ( 0, Config.bigmapheight, Config.bigmapheight // Config.ytiles ):
        pygame.draw.line ( bigmap, (64, 64, 64), (0, y), (Config.bigmapwidth, y) )
    pygame.draw.rect ( bigmap, (255, 0, 0), (0, 0, Config.bigmapwidth, Config.bigmapheight), 25 )  #

    pygame.draw.line ( bigmap, (200, 0, 0), (Config.bigmapwidth / 2, 0), (Config.bigmapwidth / 2, Config.bigmapheight),
                       1 )
    pygame.draw.line ( bigmap, (200, 0, 0), (0, Config.bigmapheight / 2), (Config.bigmapwidth, Config.bigmapheight / 2),
                       1 )
    bigmap = bigmap.convert ()

    background = pygame.Surface ( (screen.get_size ()) )
    backgroundrect = background.get_rect ()
    background = bigmap.subsurface ( (Config.cornerpoint[ 0 ],
                                      Config.cornerpoint[ 1 ],
                                      Config.width,
                                      Config.height) )

    background = background.convert ()
    screen.blit ( background, (0, 0) )
    clock = pygame.time.Clock ()
    FPS = Config.fps
    playtime = 0

    tankgroup = pygame.sprite.Group ()
    bulletgroup = pygame.sprite.Group ()
    allgroup = pygame.sprite.LayeredUpdates ()

    Tank._layer = 4
    Bullet._layer = 7
    Tracer._layer = 5
    Turret._layer = 6
    Text._layer = 3
    Radarmap._layer = 3


    Tank.groups = tankgroup, allgroup
    Turret.groups = allgroup
    Bullet.groups = bulletgroup, allgroup
    Text.groups = allgroup
    Radarmap.groups = allgroup

    player1 = Tank ( (150, 250), 90 )
    player2 = Tank ( (450, 250), 90 )
    Radarmap ()

    status3 = Text ( (155, 25), "ijkl keys to scroll the map," )
    status3 = Text ( (155, 45), "tank1: wasd, vb, fgh" )
    status4 = Text ( (155, 65), "2: keypad(5123,46), orvatakkar skjota" )
    mainloop = True
    while mainloop:
        milliseconds = clock.tick ( Config.fps )
        seconds = milliseconds / 1000.0
        playtime += seconds

        for event in pygame.event.get ():
            if event.type == pygame.QUIT:
                mainloop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed ()[ 0 ]:

                    player1.pos[ 0 ] = pygame.mouse.get_pos ()[ 0 ] + Config.cornerpoint[ 0 ]
                    player1.pos[ 1 ] = pygame.mouse.get_pos ()[ 1 ] + Config.cornerpoint[ 1 ]


        scrollx = 0
        scrolly = 0
        pressedkeys = pygame.key.get_pressed ()

        if pressedkeys[ pygame.K_j ]:
            scrollx -= Config.scrollstepx
        if pressedkeys[ pygame.K_l ]:
            scrollx += Config.scrollstepx
        if pressedkeys[ pygame.K_i ]:
            scrolly -= Config.scrollstepy
        if pressedkeys[ pygame.K_k ]:
            scrolly += Config.scrollstepy

        Config.cornerpoint[ 0 ] += scrollx
        Config.cornerpoint[ 1 ] += scrolly

        if Config.cornerpoint[ 0 ] < 0:
            Config.cornerpoint[ 0 ] = 0
            scrollx = 0
        elif Config.cornerpoint[ 0 ] > Config.bigmapwidth - Config.width:
            Config.cornerpoint[ 0 ] = Config.bigmapwidth - Config.width
            scrollx = 0
        if Config.cornerpoint[ 1 ] < 0:
            Config.cornerpoint[ 1 ] = 0
            scrolly = 0
        elif Config.cornerpoint[ 1 ] > Config.bigmapheight - Config.height:
            Config.cornerpoint[ 1 ] = Config.bigmapheight - Config.height
            scrolly = 0

        pygame.display.set_caption ( "%s FPS: %.2f playtime: %.1f " % (Config.title, clock.get_fps (), playtime) )
        # screen.blit(background, (0,0))
        if scrollx == 0 and scrolly == 0:
            allgroup.clear ( screen, background )
        else:
            background = bigmap.subsurface ( (Config.cornerpoint[ 0 ],
                                              Config.cornerpoint[ 1 ],
                                              Config.width,
                                              Config.height) )
            screen.blit ( background, (0, 0) )
        allgroup.update ( seconds )
        allgroup.draw ( screen )
        pygame.display.flip ()
    return 0


if __name__ == '__main__':
    main ()