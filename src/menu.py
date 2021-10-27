import pygame
from settings import Settings

ASSETS = {
    'logo_game': pygame.image.load('assets/logo_game_2.png'),
    'menu_pointer': pygame.image.load('assets/menu_pointer.png'),     
}


PAUSE_KEY = pygame.K_ESCAPE
SELECT_KEY = pygame.K_RETURN
UP_KEY = pygame.K_UP 
DOWN_KEY = pygame.K_DOWN



class MenuOption:
    def __init__(self, screen, label, select):
        self.screen = screen
        self.label = label
        self.select = select

    def draw(self, y, point):                
        cursor = ASSETS['menu_pointer']
        label = Settings().GAME_FONT_MENU.render(self.label, True, (255, 255, 255))

        if point:#kiem tra xem sel dang chi vao dau
            self.screen.blit(cursor, cursor.get_rect(left=120, centery=y))
        self.screen.blit(label, label.get_rect(left=190, centery=y))


class Menu:
    def __init__(self, screen, ai_game):
        self.ai_game = ai_game
        self.screen = screen
        self.is_open = True
        self.selected = 0
        self.mode = 'main'
        self.score = None
        self.stage = None
        self.options = {
          'main': [
            MenuOption(screen, 'Play Game', self.ai_game.new_classic_game), 
            MenuOption(screen, 'Quit Game', self.ai_game.quit),
          ],
          'pause': [
            MenuOption(screen, 'Continue', self.ai_game.resume_game), 
            MenuOption(screen, 'Main menu',  lambda: self.open('main')) #truyền vào tham số là một function (vì self.open trả về nonetype nên phải thêm lambda)
          ],
          'gameover': [
            MenuOption(screen, 'New Game', self.ai_game.restart_game), 
            MenuOption(screen, 'Main menu',  lambda: self.open('main'))
          ]     
        }

    def open(self, mode, score=None, stage=None):
        self.score = score
        self.stage = stage
        if self.mode != mode:
            self.selected = 0 #khi chuyen menu, con tro luon o vi tri dau tien
        self.mode = mode
        self.is_open = True

    def draw(self):
        if self.mode == 'main' or self.mode == 'pause':
            logo_game = ASSETS['logo_game']
            self.screen.blit(logo_game, logo_game.get_rect(centerx=325, top=0))
        elif self.mode == 'gameover':
            gameover_label = Settings().GAME_FONT_MENU.render('Game Over', True, (255, 255, 255))
            score = 'SCORE: {:04d}'.format(self.score)
            score = Settings().GAME_FONT_MENU.render(score, True, (255, 255, 255))
            stage = 'STAGE: {:02d}'.format(self.stage)
            stage = Settings().GAME_FONT_MENU.render(stage, True, (255, 255, 255))

            self.screen.blit(gameover_label, gameover_label.get_rect(left=80, top=190))
            self.screen.blit(score, gameover_label.get_rect(left=80, top=250))
            self.screen.blit(stage, gameover_label.get_rect(left=80, top=300))        
        y = 500
        for i, option in enumerate(self.options[self.mode]):
          option.draw(y, self.selected == i)
          y += 70 #khoang cach giua cac dong
        
    def handle_key(self, key):
        if key == PAUSE_KEY and self.mode == 'pause':
            self.ai_game.resume_game()
        elif key == SELECT_KEY:
            self.options[self.mode][self.selected].select()
        elif key == UP_KEY:
            if self.selected == 0:
                self.selected = len(self.options[self.mode]) - 1 #nhay xuong cuoi
            else:
                self.selected -= 1
        elif key == DOWN_KEY:
            if self.selected == len(self.options[self.mode]) - 1:
                self.selected = 0 #nhay len dau
            else:
                self.selected += 1