import os
import random
import pygame
import time

pygame.init()
WIN = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Video Game - Kodland - PG")

S_RED = pygame.image.load(os.path.join("assets", "ship_red.png"))
S_BLUE = pygame.image.load(os.path.join("assets", "ship_blue.png"))
S_GREEN = pygame.image.load(os.path.join("assets", "ship_green.png"))
S_YELLOW = pygame.image.load(os.path.join("assets", "pixel_OG.png"))
L_ORANGE = pygame.image.load(os.path.join("assets", "laser_orange.png"))
L_BLUE = pygame.image.load(os.path.join("assets", "laser_blue.png"))
L_GREEN = pygame.image.load(os.path.join("assets", "laser_green.png"))
L_PURPLE = pygame.image.load(os.path.join("assets", "laser_purple.png"))
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (800, 800))
SOUND_EXP = pygame.mixer.Sound(os.path.join("sounds", "explosion.wav"))
SOUND_LASER = pygame.mixer.Sound(os.path.join("sounds", "laser.wav"))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
    
    def move(self, SPEED_LASER):
        self.y += SPEED_LASER
    
    def off_screen(self, height):
        return self.y > height or self.y < 0
    
    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health= 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(800):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                pygame.mixer.Channel(2).play(SOUND_EXP)
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            if sound_check(laser):
                pygame.mixer.Channel(0).play(SOUND_LASER)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health= 100):
        super().__init__(x, y, health)
        self.ship_img = S_YELLOW
        self.laser_img = L_PURPLE
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(-vel)
            if laser.off_screen(800):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        pygame.mixer.Channel(2).play(SOUND_EXP)
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
    
    def draw(self, window):
        super().draw(window)
        self.healthbar(WIN)


    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y+self.get_height()+10, self.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y+self.get_height()+10, int(self.get_width()*(self.health/self.max_health)), 10))

class Enemy(Ship):

    MAPPING_SHIPS = {
        "red": (S_RED, L_ORANGE),
        "blue": (S_BLUE, L_BLUE),
        "green": (S_GREEN, L_GREEN)
    }

    def __init__(self, x, y, color, health= 100):
        super().__init__(x, y, health)
        self.ship_img = self.MAPPING_SHIPS[color][0]
        self.laser_img = self.MAPPING_SHIPS[color][1]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def move(self, vel): 
        self.y += vel

    def shoot(self): 
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            if sound_check(laser):
                pygame.mixer.Channel(1).play(SOUND_LASER)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def sound_check(obj: Laser): 
    if obj.y < 0 or obj.y > 750:
        return False
    else:
        return True

def main():
    run = True
    lost = False
    lost_count = 0
    FPS = 75
    level = 0
    lives = 5
    SPEED_PLAYER = 5
    SPEED_ENEMY = 1
    SPEED_LASER = 5
    enemies = []
    wave_length = 0
    main_font = pygame.font.SysFont("arial", size= 30)
    player = Player(300, 630)
    
    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BACKGROUND, (0,0))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (800 - level_label.get_width() - 10, 10))
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        if lost:
            lost_label = main_font.render("You've Lost!", 1, (255,255,255))
            WIN.blit(lost_label, ((800-lost_label.get_width())//2, (800-lost_label.get_height())//2))

        pygame.display.update()
    
    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        if lost:
            if lost_count > FPS*3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(50, 800-100), random.randrange(-1500 *(1+level//4), -100), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - SPEED_PLAYER > 0: 
            player.x -= SPEED_PLAYER
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + SPEED_PLAYER + player.get_width() < 800: 
            player.x += SPEED_PLAYER
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - SPEED_PLAYER > 0: 
            player.y -= SPEED_PLAYER
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + SPEED_PLAYER + player.get_height() + 15 < 800:
            player.y += SPEED_PLAYER
        if keys[pygame.K_SPACE]:
            player.shoot()
        
        mouse_press = pygame.mouse.get_pressed()
        if mouse_press[0]: 
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(SPEED_ENEMY)
            enemy.move_lasers(SPEED_LASER, player)
            if random.randrange(0, 2*FPS) == 1: 
                enemy.shoot()
            if collide(enemy, player):
                player.health -= 10
                pygame.mixer.Channel(2).play(SOUND_EXP)
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > 800:
                lives -= 1
                enemies.remove(enemy)
        player.move_lasers(SPEED_LASER, enemies)

def main_menu():
    title_font = pygame.font.SysFont("arial", 40)
    run = True
    while run:
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(BACKGROUND, (0,0))
        WIN.blit(title_label, ((800-title_label.get_width())//2, (800-title_label.get_height())//2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()