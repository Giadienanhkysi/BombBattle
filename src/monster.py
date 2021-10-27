import math, random
import pygame

from settings import Settings
pygame.init()
ASSETS = {
    'monster': {
      'up': [
        pygame.image.load('assets/monster/monster_up_{}.png'.format(i)) for i in range(1, 5)
      ],
      'down': [
        pygame.image.load('assets/monster/monster_down_{}.png'.format(i)) for i in range(1, 5)
      ],
      'left': [
        pygame.image.load('assets/monster/monster_left_{}.png'.format(i)) for i in range(1, 5)
      ],
      'right': [
        pygame.image.load('assets/monster/monster_right_{}.png'.format(i)) for i in range(1, 5)
      ],
      'idle': [
        pygame.image.load('assets/monster/monster_idle_{}.png'.format(i)) for i in range(1, 5)
      ],
    },
    'monster_dead': [
      pygame.image.load('assets/monster/monster_dead_{}.png'.format(i)) for i in range(1, 6)
    ],
    'monster_dead_sound': pygame.mixer.Sound('assets/sound/monster_dead_sound.ogg'),
    'door_opening_sound': pygame.mixer.Sound('assets/sound/door_opening_sound.ogg')         
    
}
class Monster:
    V = 1.6 #van toc
    def __init__(self, game, x, y, direction):
        self.game = game
        self.pos = [x, y]        
        self.direction = direction
        self.alive = True
        self.score = 50
        self.time_to_disappear = None
        self.clock = 0
        self.seconds_since_eyes_closed = 0
        self.eyes_closed = False

    def die(self, lvl):
        ASSETS['monster_dead_sound'].play()
        self.alive = False
        self.game.score += self.score
        if(self.game.high_score < self.game.score):
            self.game.high_score = self.game.score
            Settings().write_file('assets/point.txt', self.game.score)
        self.time_to_disappear = 1   
        if len(lvl.monsters) == 1:            
            pygame.mixer.Sound('assets/sound/door_opening_sound.ogg').play() 

    def loop(self, lvl, time):
        self.clock += time
        self.seconds_since_eyes_closed += time
        self.loop_eyes()
        if self.alive:
            self.check_has_to_change_direction_due_to_bomb(lvl)
            self.move(lvl, self.V*time)
            for f in lvl.flames:
                if f.collides(*self.pos):
                    self.die(lvl)
        else:
            self.time_to_disappear -= time
            if self.time_to_disappear <= 0:
                lvl.monsters.remove(self)                

    def check_has_to_change_direction_due_to_bomb(self, lvl):
        if self.direction == 'up':
            px, nx = self.pos[0], self.pos[0]
            py, ny = math.ceil(self.pos[1]), math.floor(self.pos[1]) # vi tri cũ, vị trí tiếp theo sẽ đến
            d = 'down'
        elif self.direction == 'down':
            px, nx = self.pos[0], self.pos[0]
            py, ny = math.floor(self.pos[1]), math.ceil(self.pos[1])
            d = 'up'
        elif self.direction == 'left':
            px, nx = math.ceil(self.pos[0]), math.floor(self.pos[0])
            py, ny = self.pos[1], self.pos[1]
            d = 'right'
        elif self.direction == 'right':
            px, nx = math.floor(self.pos[0]), math.ceil(self.pos[0])
            py, ny = self.pos[1], self.pos[1]
            d = 'left'
        elif self.direction == 'idle':
            return

        if (nx, ny) not in lvl.bombs:
            return
        elif (px, py) not in lvl.bombs:
            self.direction = d      
        else:
            self.direction = 'idle'                          
    def maybe_try_change_directions(self, lvl):
        x, y = int(self.pos[0]), int(self.pos[1])
        if self.direction == 'up':
            weights = [87, 3, 7, 3] #trọng số hướng tương ứng [up, right, down, left]
        elif self.direction == 'right':
            weights = [3, 87, 3, 7]
        elif self.direction == 'down':
            weights = [7, 3, 87, 3]
        elif self.direction == 'left':
            weights = [3, 7, 3, 87]
        elif self.direction == 'idle':
            weights = [25, 25, 25, 25] # tất cả các hướng tương đương nhau

        #[up, right, down, left]
        # kiểm tra các hướng xem có vật cản không, nếu không thì được phép đi qua
        possible = [True, True, True, True]
        for i, pos in enumerate([(x, y-1), (x+1, y), (x, y+1), (x-1, y)]):
            for bomb in lvl.bombs.values():
                if bomb.collides(*pos):
                    possible[i] = False
                    break
            possible[i] = possible[i] and not (lvl.matrix.is_solid(*pos))
         # Tổng trọng số của tất cả các hướng có thể đi
        total = sum([w for w, a in zip(weights, possible) if a])  

        # lưu lại trọng số của các hướng nếu không thể đi thì lưu = 0    
        weights = [w/total if a else 0 for w, a in zip(weights, possible)]    
        rnd = random.random()
        d = 0
        # chọn hướng đầu tiên có tổng giá trị từ trước tính đến nó lớn hơn rnd để di chuyển theo hướng đó
        for w, direction in zip(weights, ['up', 'right', 'down', 'left']):
            if w ==0:
                continue
            d += w
            if d > rnd:
                self.direction = direction
                return
        # nếu ko có, khởi tạo trị bằng nhau
        self.direction = 'idle'        


    def move(self, lvl, distance):#0.0128
        cx, cy = self.pos
        rx, ry = round(self.pos[0]), round(self.pos[1])
        if (ry - cy == 0 and rx - cx == 0) or self.direction == 'idle':# nếu đứng đúng vị trí hàng(cột) mới thực hiện nếu không sẽ bị đè lên vật cản            
            self.maybe_try_change_directions(lvl)

        if self.direction == 'up':                                
            if -distance <= ry - cy < 0:
                self.pos[1] = ry
                self.maybe_try_change_directions(lvl)
                self.move(lvl, distance )
            else:
                self.pos[1] -= distance
        elif self.direction == 'down':                                
            if 0 < ry - cy <= distance:
                self.pos[1] = ry
                self.maybe_try_change_directions(lvl)
                self.move(lvl, distance )
            else:
                self.pos[1] += distance
        elif self.direction == 'left':                                
            if -distance <= rx - cx < 0:
                self.pos[0] = rx
                self.maybe_try_change_directions(lvl)
                self.move(lvl, distance )
            else:
                self.pos[0] -= distance
        elif self.direction == 'right':                                
            if 0 < rx - cx <= distance: # giá trị làm tròn bằng, hoặc gần bằng bước tiếp theo(round_x = 4, current_x = 3.999)
                self.pos[0] = rx #thì gán luôn vị trí bằng giá trị đó
                self.maybe_try_change_directions(lvl)
                self.move(lvl, distance )
            else:
                self.pos[0] += distance # nếu còn cách xa thì cộng thêm bước nhay  
                          
    def collides(self, x, y):
        return -0.6 <= x - self.pos[0] <= 0.6 and -0.6 <= y - self.pos[1] <= 0.6
    
    def loop_eyes(self): 
        if self.seconds_since_eyes_closed >= 0.2:
            self.eyes_closed = False            
        if self.seconds_since_eyes_closed >= 0.4:
            if random.random() <= 0.5:
                self.eyes_closed = True
                self.seconds_since_eyes_closed = 0

    def draw(self, canvas):
        if self.alive:
            current_frame = int((self.clock%0.4)//0.2)# luôn thu được 2 giá trị 0, 1
            if self.eyes_closed:
                current_frame += 2
            canvas.draw(ASSETS['monster'][self.direction][current_frame], self.pos)
        else:
            current_frame = int((1-self.time_to_disappear)//0.2)
            canvas.draw(ASSETS['monster_dead'][current_frame], self.pos)                
            


