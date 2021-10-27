import random
from bomb import Bomb
from blockmatrix import BlockMatrix, Block
from player import Player
from monster import Monster
class Canvas:
    '''graphic class'''
    def __init__(self, screen, pos, scale = 50):
        self.screen = screen
        self.pos = pos # vị trí của cả map
        self.scale = scale
        self.delayed = []

    def draw(self, img, pos):
        '''Draw graphic'''        
        # vị trí bằng vị trí nhân kích thước ảnh + độ lùi xuống của map chừa không gian để in chữ, logo
        x = pos[0] * self.scale + self.pos[0]
        y = pos[1] * self.scale + self.pos[1]
        self.screen.blit(img, (x, y))
          
        


class Level:
    def __init__(self, canvas, matrix, player, monsters=[]):
        self.canvas = canvas
        self.matrix = matrix
        self.players = player
        self.bombs = {}
        self.flames = []
        self.monsters = monsters

    def draw(self):
        self.matrix.draw(self.canvas)
        for flame in self.flames:
            flame.draw(self.canvas)
        for bomb in self.bombs.values():
            bomb.draw(self.canvas)
        for player in self.players:
            player.draw(self.canvas)    
        for monster in self.monsters:
            monster.draw(self.canvas)

        
    
    def loop(self, time):
        self.matrix.loop(time)
        for flame in self.flames:
            flame.loop(self, time)
        for bomb in self.bombs.values():
            bomb.loop(self, time)
        # xóa bom đã nổ trong list bomb
        for k in list(self.bombs.keys()):        
            if self.bombs[k] == None:
                del self.bombs[k]
        for player in self.players:
            player.loop(self, time)
        #mở cửa
        if(len(self.monsters)==0):
            self.matrix.open_door()
        for monster in self.monsters:
            monster.loop(self, time)

    def handle_key(self, key):        
        for player in self.players:
            player.handle_key(key, self)

    def try_place_bomb(self, x, y, placer):
        '''kiểm tra xem có thể đặt bom hay không'''
        pos = round(x), round(y)
        can_place = (
          pos not in self.bombs 
          and self.matrix.check_bomb_placeable(*pos)
          and not (0.45 < x - int(x) < 0.55)#tránh bị kẹt giữa 2 quả bom
          and not (0.45 < y - int(y) < 0.55)
        )
        if can_place:
            self.bombs[pos] = Bomb(*pos, placer, placer.bomb_blast_radius) #them bom vào danh sách các bom            
        return can_place

    def placed_bombs(self, player):
        count = 0
        for bomb in self.bombs.values():
            if bomb.placer == player:
                count += 1
        return count
    NUMBER_OF_TILES = 13*13
    NUMBER_OF_RANDOMIZABLE_TILES_SP = NUMBER_OF_TILES - 77

    @staticmethod
    def singleplayer(game, canvas, monsters_lim=[3, 4], boxes_lim=[15, 35], max_bomb = 1, bomb_blast_radius = 2):
        monsters_number = random.randrange(monsters_lim[0], monsters_lim[1]+1)
        boxes_number = random.randrange(boxes_lim[0], boxes_lim[1]+1)
        grass_number = Level.NUMBER_OF_RANDOMIZABLE_TILES_SP - monsters_number - boxes_number

        # 0: Grass
        # 1: Boxes
        # 2: Goal
        # 3: Monsters
        # 4: Powerups
        elements = [0]*grass_number + [1]*boxes_number + [2] + [3]*monsters_number + [4]
        
        monsters = []
        random.shuffle(elements)#đảo thứ tự các phần tử ngẫu nhiên

        matrix = [[None]*13 for _ in range(13)]
        players = [Player(game, 1, 1, max_bomb = max_bomb , bomb_blast_radius = bomb_blast_radius)]
        # vẽ đồ họa
        for x in range(0, 13):
            for y in range(0, 13): 
                if x == 0 or x == 12 or y == 0 or y == 12:
                    matrix[y][x] = Block.WALL
                elif x % 2 == 0 and y % 2 == 0:
                    matrix[y][x] = Block.WALL
                elif x in [1, 2] and y in [1, 2]:
                    matrix[y][x] = Block.GRASS
                else:
                    rnd_element = elements.pop()
                    if rnd_element == 0:
                        matrix[y][x] = Block.GRASS
                    elif rnd_element == 1:
                        matrix[y][x] = Block.BOX
                    elif rnd_element == 2:
                        matrix[y][x] = Block.BOX_GOAL
                    elif rnd_element == 3:
                        matrix[y][x] = Block.GRASS
                        direction = random.choice(['up', 'down', 'left', 'right'])
                        monsters.append(Monster(game, x, y, direction))
                    elif rnd_element == 4:
                        powerup = random.choice([
                          Block.BOX_POWERUP_BLAST, Block.BOX_POWERUP_BOMBUP, Block.BOX_POWERUP_LIFE
                        ])
                        matrix[y][x] = powerup
        
        matrix = BlockMatrix(matrix)
        return Level(canvas, matrix, players, monsters)

        