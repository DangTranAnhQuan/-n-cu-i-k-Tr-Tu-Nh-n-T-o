import pygame
import os
import random
import csv
from entities.enemy import Boss, Enemy
from entities.player import Player, HealthBar
from environment import *
import setting

pygame.init() 

img_list = []
speed_box_img = pygame.image.load("assets/ItemBox/Speed.png")
attack_box_img = pygame.image.load("assets/ItemBox/Attack.png")
health_box_img = pygame.image.load("assets/ItemBox/Health.png")
bonus_box_img = pygame.image.load("assets/ItemBox/Bonus.png")
item_box_list = {"Speed": speed_box_img, "Attack": attack_box_img, "Health": health_box_img, "Bonus": bonus_box_img}

item_group = pygame.sprite.Group()

def load_tile_images():
    global img_list
    img_list.clear()
    for tile_id in range(setting.TILE_TYPES):
        img = None 
        try:
            img_path = f'assets/map/Map_{setting.MAP}/Tile/{tile_id}.png'
            loaded_img = pygame.image.load(img_path).convert_alpha()

            if 60 <= tile_id <= 79:  
                img = loaded_img  
            else:  
                img = pygame.transform.scale(loaded_img, (setting.TILE_SIZE, setting.TILE_SIZE))

        except pygame.error as e:
            print(f"Error loading tile {tile_id} from '{img_path}': {e}. Using a placeholder.")
            if 60 <= tile_id <= 79:
                img = pygame.Surface((setting.TILE_SIZE // 2, setting.TILE_SIZE // 2), pygame.SRCALPHA)
                img.fill((200, 100, 255, 180)) 
                pygame.draw.rect(img, (0,0,0), img.get_rect(), 1) 
            else:
                img = pygame.Surface((setting.TILE_SIZE, setting.TILE_SIZE), pygame.SRCALPHA)
                img.fill((255, 0, 255, 180))  
                pygame.draw.rect(img, (0,0,0), img.get_rect(), 1) 
            try:
                font_size = 10 if 60 <= tile_id <= 79 else 12
                font = pygame.font.SysFont("arial", font_size, bold=True)
                text_surf = font.render(str(tile_id), True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=img.get_rect().center)
                img.blit(text_surf, text_rect)
            except Exception as font_e: 
                print(f"Could not render text on placeholder for tile {tile_id}: {font_e}")
                
        img_list.append(img)

def load_world(world_data = []):
    filepath = f'assets/map/Map_{setting.MAP}/{setting.level}.csv'
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            world_data.append([int(tile) for tile in row])

    return world_data


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, player, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.item_type = item_type
        self.image = item_box_list[item_type]
        self.rect = self.image.get_rect()
        cell_center_x = x + setting.TILE_SIZE // 2
        cell_center_y = y + setting.TILE_SIZE // 1.5 + 2
        self.rect.center = (cell_center_x, cell_center_y)

    def update(self):
        if pygame.sprite.collide_rect(self, self.player):
            if self.item_type == "Speed":
                self.player.speed += 0.5
            elif self.item_type == "Attack":
                self.player.attack += 2
            elif self.item_type == "Health":
                if self.player.health == self.player.max_health:
                    self.player.max_health += 10
                    self.player.health = self.player.max_health
                else:
                    if self.player.health + 20 <= self.player.max_health:
                        self.player.health += 20
                    else:
                        self.player.health = self.player.max_health
            elif self.item_type == "Bonus":
                self.player.speed += 0.25
                self.player.attack += 1
                self.player.max_health += 5
                self.player.health += 5
                    
            self.kill()
            
    def draw(self, screen, offset=(0, 0)):
         render_pos_x = self.rect.x - offset[0]
         render_pos_y = self.rect.y - offset[1]
         screen.blit(self.image, (render_pos_x, render_pos_y))

def draw_status(screen, status_list, healthbar, health, max_health, atk, speed, offset=(0, 0)):

    healthbar.draw(health, max_health, offset=offset)

    attack_icon_pos_x = 10 
    attack_icon_pos_y = 60 
    attack_text_pos_x = 50
    attack_text_pos_y = 70 
    screen.blit(status_list["Attack"], (attack_icon_pos_x, attack_icon_pos_y))
    img_atk = setting.font.render(f": {atk}", True, "black")
    screen.blit(img_atk, (attack_text_pos_x, attack_text_pos_y))

    speed_icon_pos_x = 10 
    speed_icon_pos_y = 100 
    speed_text_pos_x = 50 
    speed_text_pos_y = 110 
    screen.blit(status_list["Speed"], (speed_icon_pos_x, speed_icon_pos_y))
    img_speed = setting.font.render(f": {speed}", True, "black")
    screen.blit(img_speed, (speed_text_pos_x, speed_text_pos_y))

    skill_icon_pos_x = 10 
    skill_icon_pos_y = 140 
    skill_text_pos_x = 50 
    skill_text_pos_y = 150 
    skill_time = (setting.skill_cooldown - (pygame.time.get_ticks() - setting.last_skill_time)) / 1000
    screen.blit(status_list["Skill"], (skill_icon_pos_x, skill_icon_pos_y))
    img_skill = setting.font.render(f": {round(skill_time, 1) if skill_time > 0 else 'Ready'}", True, "black") 
    screen.blit(img_skill, (skill_text_pos_x, skill_text_pos_y))

    map_icon_pos_x = 10
    map_icon_pos_y = 190
    map_text_pos_x = 50
    map_text_pos_y = 190
    text_icon_map = setting.font.render(f"Map", True, "black")
    screen.blit(text_icon_map, (map_icon_pos_x, map_icon_pos_y))
    img_map = setting.font.render(f": {setting.MAP}", True, "black")
    screen.blit(img_map, (map_text_pos_x, map_text_pos_y))

class World:
    def __init__(self, screen, players, enemy_group, magic_group, magic_class):

        self.screen = screen
        self.players = players
        self.enemy_group = enemy_group
        self.magic_group = magic_group
        self.magic_class = magic_class
        self.obstacle_list = []
        self.world_data = None

        layer_names = ['1', '2', '3', '4', '5']
        base_bg_path = f'assets/map/Map_{setting.MAP}/Background/'

        layer_scale_percentages = [1, 1, 0.8, 0.7, 0.4] 

        scaled_layers = []

        for i, name in enumerate(layer_names):
            path = os.path.join(base_bg_path, f'{name}.png')
            img = pygame.image.load(path).convert_alpha()
            
            if i < len(layer_scale_percentages):
                scale_factor = layer_scale_percentages[i]
                new_width = int(setting.screen_width * scale_factor)
                new_height = int(setting.screen_height * scale_factor)

                if new_width > 0 and new_height > 0:
                    scaled_img = pygame.transform.scale(img, (new_width, new_height))
                    scaled_layers.append(scaled_img)
                else:
                    scaled_layers.append(img) 
            else:
                scaled_layers.append(img) 

        self.background_layers = scaled_layers 

        if not self.background_layers:
            path = os.path.join(base_bg_path, 'background.png')
            try:
                img = pygame.image.load(path).convert_alpha()
                scaled_fallback = pygame.transform.scale(img, (setting.screen_width, setting.screen_height))
                self.background_layers = [scaled_fallback]
            except pygame.error as e:
                self.background_layers = []

    def process_data(self, data):
        self.world_data = data
        player = None
        health_bar = None

        self.obstacle_list.clear()
        water_group.empty()
        decoration_group.empty()
        exit_group.empty()
        item_group.empty()
        self.enemy_group.empty()

        item_creation_info = []
        enemy_creation_info = []

        max_y = len(data)
        max_x = len(data[0]) if max_y > 0 else 0

        enemy_type = ["Enemy_1", "Enemy_2", "Enemy_3"]
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    if tile >= len(img_list): 
                        continue
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.topleft = (x * setting.TILE_SIZE, y * setting.TILE_SIZE)
                    tile_data = (img, img_rect)

                    if 0 <= tile <= 59:
                        self.obstacle_list.append(tile_data)
                    elif 60 <= tile <= 79:
                        decoration = Decoration(img, x * setting.TILE_SIZE, y * setting.TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 80:
                        player = Player(self.screen, self, setting.random.choice(self.players),
                                            x * setting.TILE_SIZE, y * setting.TILE_SIZE, setting.scale, 2, 5, 
                                            self.enemy_group, self.magic_group, self.magic_class)
                        health_bar = HealthBar(self.screen, 10, 10, player.health, player.max_health)
                    elif tile == 81:
                        enemy_info = (random.choice(enemy_type), x * setting.TILE_SIZE, y * setting.TILE_SIZE, setting.scale * 0.5, 1, 3)
                        enemy_creation_info.append(enemy_info)
                    elif tile == 82:
                        enemy_info = ('FlyingDemon', x * setting.TILE_SIZE, y * setting.TILE_SIZE, setting.scale * 1.25, 1, 3)
                        enemy_creation_info.append(enemy_info)
                    elif tile == 83:
                        enemy_info = ('Boss Game', x * setting.TILE_SIZE, y * setting.TILE_SIZE, setting.scale * 1.75, 1, 5) 
                        enemy_creation_info.append(enemy_info)
                    elif tile == 87:
                        item_info = ('Speed', x * setting.TILE_SIZE, y * setting.TILE_SIZE)
                        item_creation_info.append(item_info)
                    elif tile == 84:
                        item_info = ('Attack', x * setting.TILE_SIZE, y * setting.TILE_SIZE)
                        item_creation_info.append(item_info)
                    elif tile == 85:
                        item_info = ('Bonus', x * setting.TILE_SIZE, y * setting.TILE_SIZE)
                        item_creation_info.append(item_info)
                    elif tile == 86:
                        item_info = ('Health', x * setting.TILE_SIZE, y * setting.TILE_SIZE)
                        item_creation_info.append(item_info)
                    elif tile == 88:
                        exit_obj = Exit(img, x * setting.TILE_SIZE, y * setting.TILE_SIZE)                        
                        exit_group.add(exit_obj)

        if player is None:
            raise ValueError("Player start position (tile 80) not found in level data!")
        
        for item_type, x, y in item_creation_info:
            item_box = ItemBox(player, item_type, x, y)
            item_group.add(item_box)

        for enemy_type, x, y, enemy_scale, speed, attack in enemy_creation_info:
            if enemy_type == 'Boss Game':
                enemy = Boss(self.screen, self, player, x, y, enemy_scale, speed, attack)
                self.enemy_group.add(enemy)
            elif enemy_type == 'FlyingDemon':
                enemy_0 = Enemy(self.screen, self, player, 'FlyingDemon', x, y, enemy_scale, speed, attack)
                self.enemy_group.add(enemy_0)
            elif enemy_type == 'Enemy_1':
                enemy_1 = Enemy(self.screen, self, player, 'Enemy_1', x, y, enemy_scale, speed, attack)
                self.enemy_group.add(enemy_1)
            elif enemy_type == 'Enemy_2':
                enemy_2 = Enemy(self.screen, self, player, 'Enemy_2', x, y, enemy_scale, speed, attack)
                self.enemy_group.add(enemy_2)
            elif enemy_type == 'Enemy_3':
                enemy_3 = Enemy(self.screen, self, player, 'Enemy_3', x, y, enemy_scale, speed, attack)
                self.enemy_group.add(enemy_3)
             
        
        return player, health_bar

    def draw_tiles(self, offset=(0, 0)):
        for tile in self.obstacle_list:
            img = tile[0]
            rect = tile[1]
            render_pos_x = rect.x - offset[0]
            render_pos_y = rect.y - offset[1]
            if rect.right > offset[0] and rect.left < offset[0] + setting.screen_width and \
               rect.bottom > offset[1] and rect.top < offset[1] + setting.screen_height:
                self.screen.blit(img, (render_pos_x, render_pos_y))

    def draw_background(self, bg_scroll_offset):
        self.screen.fill((0, 0, 0))

        if not self.background_layers:
            return

        scroll_factors = [0.2, 0.4, 0.6, 0.8, 1.0]

        if len(self.background_layers) > len(scroll_factors):
            scroll_factors.extend([scroll_factors[-1]] * (len(self.background_layers) - len(scroll_factors)))

        for i, layer_img in enumerate(self.background_layers):
            if i >= len(scroll_factors): continue

            factor = scroll_factors[i]
            img_width = layer_img.get_width()
            img_height = layer_img.get_height()

            if img_width <= 0: continue

            y_pos = setting.screen_height - img_height

            tiles_to_draw = int(setting.screen_width / img_width) + 3
            start_tile_index = int((bg_scroll_offset * factor) // img_width)

            for tile_num in range(start_tile_index - 1, start_tile_index + tiles_to_draw):
                blit_x = (tile_num * img_width) - (bg_scroll_offset * factor)
                self.screen.blit(layer_img, (blit_x, y_pos))

def update_world_data(world_data, enemy_group, player):
    """Cập nhật world_data với vị trí player và enemies."""
    if not world_data: return world_data
    rows = len(world_data)
    if rows == 0: return world_data
    cols = len(world_data[0])
    if cols == 0: return world_data

    for r in range(rows):
        for c in range(cols):
            if world_data[r][c] in range(60, 84):
                world_data[r][c] = -1

    for enemy in enemy_group:
        col = int(enemy.rect.centerx // setting.TILE_SIZE)
        row = int((enemy.rect.bottom - 1) // setting.TILE_SIZE)
        if 0 <= row < rows and 0 <= col < cols:
            if world_data[row][col] == -1:
                if enemy.char_type == "FlyingDemon":
                    world_data[row][col] = 82
                elif enemy.char_type == "Boss Game":
                    world_data[row][col] = 83
                else:
                    world_data[row][col] = 81

    col = int(player.rect.centerx // setting.TILE_SIZE)
    row = int((player.rect.bottom - 1) // setting.TILE_SIZE)
    if 0 <= row < rows and 0 <= col < cols:
         if world_data[row][col] == -1:
            world_data[row][col] = 80

    return world_data
