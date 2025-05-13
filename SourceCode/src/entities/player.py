import pygame
import os
from .baseCharacter import BaseCharacter
import setting

class Player(BaseCharacter):
    def __init__(self, screen, world, char_type, x, y, scale, speed, attack, enemy_group, magic_group, magic_class):
        super().__init__(screen, world, char_type, x, y, scale, speed, attack)
        self.recovering = False
        self.dashing = False
        self.parry = False
        self.last_hit_time = 0
        self.last_parry_time = 0
        self.defense = 0
        self.enemy_group = enemy_group
        self.magic_group = magic_group
        self.Magic = magic_class 
        
        self.current_attack_rect = None 
        self.attack_hitbox_debug_color = (255, 100, 0, 150)
    
    def player_attack(self):
        if self.attacking:
            self.current_attack_rect = self._create_directional_attack_hitbox()
            if (self.action == 3 and self.img_index in [4, 9, 14]) or (self.action == 4 and self.img_index in [3, 8]):
                for monster in self.enemy_group:  
                    if self.current_attack_rect.colliderect(monster.rect):
                        monster.health -= self.attack / 4 
        else:
            self.current_attack_rect = None

        if self.img_index == len(self.animation_list[self.action]) - 1:
            self.attacking = False
            setting.attack_1 = False 
            setting.attack_2 = False
            setting.skill = False 
            
            self.current_attack_rect = None

            if self.action == 5:
                self.skill()

    def player_recover(self):
        if self.img_index == len(self.animation_list[self.action]) - 1:
            self.health += self.max_health * 0.1
            if self.health > self.max_health:
                self.health = self.max_health
            self.recovering = False
            setting.recover = False

    def player_dash(self):
        if self.img_index == len(self.animation_list[self.action]) - 1:
            self.dashing = False
            setting.dash = False
            return
        dx = self.speed * 2 * self.direction
  
        for tile in self.world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y - 1, self.rect.width, self.rect.height):
                dx = 0
        self.rect.x += dx

    def player_parry(self):
        if pygame.time.get_ticks() - setting.last_parry_time >= 1000:
            setting.last_parry_time = pygame.time.get_ticks()
            self.parry = False
            setting.parry = False	

        elif self.action == 10 and self.img_index == len(self.animation_list[self.action]) - 1:
            self.defense = 0
            self.parry = False
            setting.parry = False
    
    def take_damage(self, amount, cooldown=500):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time >= cooldown:
            if self.parry == True:
                self.defense = 85
                self.update_action(10)
            self.health -= amount * ((100 - self.defense) / 100)
            self.last_hit_time = current_time
    def draw(self, offset=(0, 0)):
        super().draw(offset) 
        if self.current_attack_rect and setting.show_enemy_vision_rect: 
            drawable_attack_rect = self.current_attack_rect.copy()
            drawable_attack_rect.x -= offset[0]
            drawable_attack_rect.y -= offset[1]
            
            debug_surface = pygame.Surface((drawable_attack_rect.width, drawable_attack_rect.height), pygame.SRCALPHA)
            debug_surface.fill(self.attack_hitbox_debug_color) 
            self.screen.blit(debug_surface, drawable_attack_rect.topleft)
            pygame.draw.rect(self.screen, "orange", drawable_attack_rect, 1) 
            
class HealthBar:
    def __init__(self, screen, x, y, health, max_health):
        self.screen = screen
        self.health = health
        self.max_health = max_health
        self.x = x
        self.y = y
        self.healthbar_list = []

        for i in range(0, 101, 5):
            path = f'assets/Character/HealthBar/{i}.png'
            if os.path.exists(path):
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (int(img.get_width() * 0.2), int(img.get_height() * 0.2)))
                self.healthbar_list.append(img)

        dead_img = pygame.image.load('assets/Character/HealthBar/Dead.png')
        dead_img = pygame.transform.scale(dead_img, (int(dead_img.get_width() * 0.2), int(dead_img.get_height() * 0.2)))
        self.healthbar_list.append(dead_img)

        self.image = self.healthbar_list[-2]

    def draw(self, health, max_health, offset=(0, 0)): 
        self.health = health
        self.max_health = max_health
        ratio = (self.health / self.max_health) * 100

        if health > 0:
            index = min(int(ratio // 5), len(self.healthbar_list) - 2)
            self.image = self.healthbar_list[index]
        else:
            self.image = self.healthbar_list[-1] 
        render_pos_x = 0
        render_pos_y = 10
        self.screen.blit(self.image, (render_pos_x, render_pos_y))