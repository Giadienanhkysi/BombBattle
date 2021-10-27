# from settings import*
import pygame
from blocks import Block
from settings import Calculate
ASSETS = {  
    'goal_opening': [
        pygame.image.load('assets/goal_opening/goal_opening_{}.png'.format(i)) for i in range(1, 6)
    ],    
    'exploding_box': [
      pygame.image.load('assets/exploding_box/exploding_box_{}.png'.format(i)) for i in range(1, 7)],
    'power_up_sound': pygame.mixer.Sound('assets/sound/power_up_sound.ogg')
}

class BlockMatrix():
    def __init__(self, matrix = None):
        self.exploding = []
        self.matrix = matrix
        self.goal_open = False
        self.door_opening = None        

    def is_goal(self, x, y):
        return self.matrix[y][x] == Block.GOAL_OPEN


    def is_solid(self, x, y):
        return self.matrix[y][x] in [
          Block.WALL, Block.BOX, Block.BOX_GOAL, Block.BOX_POWERUP_BLAST, 
          Block.BOX_POWERUP_BOMBUP, Block.BOX_POWERUP_LIFE
        ]

    def open_door(self):
        self.goal_open = True        
        for y, row in enumerate(self.matrix):
            for x, cell in enumerate(row):                
                if cell == Block.GOAL_CLOSE:          
                    self.door_opening = [(x, y), 0.5]# tong thoi gian de chay het 5 khung hinh
                    self.matrix[y][x] = Block.GOAL_OPEN
                    return
                        

    def draw(self, canvas):
        for i, row in enumerate(self.matrix):
            for j, block in enumerate(row):
                block.draw(canvas, j, i)
        # open door
        if self.door_opening != None:
            pos, timer = self.door_opening
            current_frame = int(timer//0.1)#tong tg chia tg chay 1 khung hinh           
            current_frame = ASSETS['goal_opening'][current_frame]
            canvas.draw(current_frame, pos)
        for x, y, e_time in self.exploding:
            current_frame = int((0.375 - e_time)//0.0625)
            current_frame = ASSETS['exploding_box'][current_frame]
            canvas.draw(current_frame, (x, y))
    
    def loop(self, time):
        if self.door_opening != None:
            self.door_opening[1] -= time
            if self.door_opening[1] <=0:
                self.door_opening = None
        for i, (x, y, e_time) in enumerate(self.exploding):
            e_time -= time
            if e_time <= 0:
                del self.exploding[i]
                continue
            self.exploding[i] = (x, y, e_time)

    def explode_block(self, x, y):
        block = self.matrix[y][x]

        if block in [Block.POWERUP_BOMBUP, Block.BOX_POWERUP_BLAST, Block.POWERUP_LIFE]:
            self.matrix[y][x] = Block.GRASS
        elif block == Block.BOX:            
            self.exploding.append((x, y, 0.375))
            self.matrix[y][x] = Block.GRASS
        elif block == block.BOX_GOAL:
            self.exploding.append((x, y, 0.375))
            if self.goal_open:
                self.matrix[y][x] = Block.GOAL_OPEN
            else:
                self.matrix[y][x] = Block.GOAL_CLOSE
        elif block == Block.BOX_POWERUP_BLAST:
            self.exploding.append((x, y, 0.375))
            self.matrix[y][x] = Block.POWERUP_BLAST
        elif block == Block.BOX_POWERUP_BOMBUP:
            self.exploding.append((x, y, 0.375))
            self.matrix[y][x] = Block.POWERUP_BOMBUP
        elif block == Block.BOX_POWERUP_LIFE:
            self.exploding.append((x, y, 0.375))
            self.matrix[y][x] = Block.POWERUP_LIFE
        # tra ve loai block va cham trúng
        return block
            
    def check_eat_powerups(self, player):
        x, y = player.pos
        rx, ry = int(round(x)), int(round(y))
        if self.matrix[ry][rx] == Block.POWERUP_BOMBUP:
            ASSETS['power_up_sound'].play()            
            self.matrix[ry][rx] = Block.GRASS
            player.max_bomb += 1
        elif self.matrix[ry][rx] == Block.POWERUP_BLAST:
            ASSETS['power_up_sound'].play()            
            self.matrix[ry][rx] = Block.GRASS
            player.bomb_blast_radius += 1
        elif self.matrix[ry][rx] == Block.POWERUP_LIFE:
            ASSETS['power_up_sound'].play()            
            self.matrix[ry][rx] = Block.GRASS
            player.game.lives += 1
            
    def check_enter_goal(self, x, y):
        x, y = round(x), round(y)
        return self.is_goal(x, y)

    def check_bomb_placeable(self, x, y):
        return self.matrix[y][x] in [Block.GRASS, Block.GOAL_CLOSE]
    
    def check_collides(self, x, y):
        xl, xh, yl, yh = Calculate().list_colliding_coordinates(x, y) #tránh cho đối tượng không bi áp sát tường
        return self.is_solid(xl, yl) or self.is_solid(xl, yh) or self.is_solid(xh, yl) or self.is_solid(xh, yh)  





                
        
