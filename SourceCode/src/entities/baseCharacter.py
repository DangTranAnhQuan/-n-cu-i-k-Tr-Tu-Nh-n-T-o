import pygame 
import os    
from setting import *
from magic import Magic, magic_group 

class BaseCharacter(pygame.sprite.Sprite):
    def __init__(self, screen, world,char_type, x, y, scale, speed, attack):
        super().__init__()
        self.char_type = char_type
        self.screen = screen
        self.world = world
        self.speed = speed
        self.health = 100
        self.attack = attack
        self.max_health = self.health
        self.alive = True
        self.direction = 1
        self.flip = False
        self.vel_y = 0
        self.in_air = True
        self.jump = False
        self.attacking = False

        self.action = 0
        self.img_index = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_list = self.load_animations(char_type, scale)
        self.image = self.animation_list[self.action][self.img_index]
        self.rect = self.image.get_rect()

        if self.char_type == "FlyingDemon":
            self.rect.width = int(self.rect.width * 0.2) 
            self.rect.height = int(self.rect.height * 0.2)
        elif self.char_type == "Player":
            self.rect.width = int(self.rect.width * 0.3) 
            self.rect.height = int(self.rect.height * 0.5)
        elif self.char_type == "Boss Game":
            self.rect.width = int(self.rect.width * 0.2) 
            self.rect.height = int(self.rect.height * 0.45)

        self.rect.center = (x, y)
        self._original_width = self.rect.width
        self._original_height = self.rect.height
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def load_animations(self, char_type, scale):
        animation_types = ["Idle", "Run", "Dead", "Attack_1", "Attack_2"]
        if char_type == "Player":
            animation_types += ["Skill", "Jump", "Recover", "Dash", "Parry", "Parry_Success"]
        elif char_type == "FlyingDemon":
            animation_types = ["Idle", "Run", "Dead", "Skill"]

        animation_list = []
        for anim in animation_types:
            images = []
            num_imgs = len(os.listdir(f'assets/Character/{char_type}/{anim}'))
            for i in range(num_imgs):
                img = pygame.image.load(f'assets/Character/{char_type}/{anim}/{i + 1}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                images.append(img)
            animation_list.append(images)
        return animation_list
    
    def move(self, moving_left, moving_right, down=None):
        delta_x, delta_y = 0, 0

        if moving_left:
            delta_x = -self.speed
            self.flip = True; self.direction = -1
        if moving_right:
            delta_x = self.speed
            self.flip = False; self.direction = 1

        if self.char_type != "FlyingDemon":
            if self.jump and not self.in_air:
                self.vel_y = -6.8 
                self.jump = False
                self.in_air = True
            self.vel_y += gravity
            if self.vel_y > 10: self.vel_y = 10
            delta_y += self.vel_y
        else:
            if down is True: delta_y += self.speed
            elif down is False: delta_y -= self.speed
        
        intended_dx = round(delta_x)
        intended_dy = round(delta_y)

        self.rect.x += intended_dx
        for tile_img, tile_rect in self.world.obstacle_list:
            if tile_rect.colliderect(self.rect):
                if intended_dx > 0: self.rect.right = tile_rect.left
                elif intended_dx < 0: self.rect.left = tile_rect.right
                elif intended_dx == 0: 
                    if self.rect.centerx < tile_rect.centerx: self.rect.right = tile_rect.left
                    else: self.rect.left = tile_rect.right
                if self.char_type != "Player" and intended_dx != 0: self.direction *= -1
        
        self.rect.y += intended_dy
        landed_on_surface_this_frame = False
        hit_ceiling_this_frame = False

        for tile_img, tile_rect in self.world.obstacle_list:
            if tile_rect.colliderect(self.rect):
                if intended_dy > 0:
                    self.rect.bottom = tile_rect.top
                    landed_on_surface_this_frame = True
                elif intended_dy < 0:
                    self.rect.top = tile_rect.bottom
                    hit_ceiling_this_frame = True
                elif intended_dy == 0:
                    if self.rect.centery < tile_rect.centery:
                        self.rect.bottom = tile_rect.top
                        landed_on_surface_this_frame = True
                    else: 
                        self.rect.top = tile_rect.bottom
                        hit_ceiling_this_frame = True
                self.vel_y = 0 

        if self.char_type != "FlyingDemon":
            if landed_on_surface_this_frame:
                self.in_air = False
            else:
                self.in_air = True 
            
            if hit_ceiling_this_frame:
                self.in_air = True
            
            if self.in_air: 
                core_feet_rect_left = self.rect.centerx - (self._original_width // 2)
                feet_core_rect = pygame.Rect(core_feet_rect_left, self.rect.bottom, self._original_width, 1)

                is_truly_on_ground = False
                for tile_img, tile_rect_ground in self.world.obstacle_list:
                    if feet_core_rect.colliderect(tile_rect_ground):
                        if self.rect.bottom <= tile_rect_ground.top + 2: 
                            is_truly_on_ground = True
                            break
                
                if is_truly_on_ground:
                    self.in_air = False
                    if self.vel_y > 0: self.vel_y = 0 
                else:
                    self.in_air = True
  
    def update_animation(self):
        cooldown = 80 if self.char_type == "Player" else 120
        if self.action in [3, 4, 5] and self.char_type == "Player":
            cooldown = 50
        elif self.action == 8:
            cooldown = 30

        self.image = self.animation_list[self.action][self.img_index]

        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.img_index += 1
            
            if self.img_index >= len(self.animation_list[self.action]):
                if self.action == 2:
                    self.img_index = len(self.animation_list[self.action]) - 1
                else:
                    self.img_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.img_index = 0
            self.update_time = pygame.time.get_ticks()

    def _create_directional_attack_hitbox(self):
        if not self.attacking:
            return None

        attack_reach_forward = self._original_width * 1.8  
        attack_width_of_slash = self._original_width * 1.2
        attack_height = self._original_height * 0.9 

        hitbox_top = self.rect.centery - (attack_height / 2)

        if self.direction == 1: 
            hitbox_left = self.rect.right - (self._original_width * 0.3) 
            return pygame.Rect(hitbox_left, hitbox_top, attack_reach_forward, attack_height)
        elif self.direction == -1: 
            hitbox_right = self.rect.left + (self._original_width * 0.3)
            hitbox_left = hitbox_right - attack_reach_forward
            return pygame.Rect(hitbox_left, hitbox_top, attack_reach_forward, attack_height)
        return None

    def skill(self):
        scale_skill = scale * 2 if self.char_type == "Player" else scale
        player = self if self.char_type == "Player" else self.player
        magic = Magic(self.screen, self.world, self.rect.centerx + self.direction * self.rect.width, self.rect.centery - scale * 10, self.char_type, scale_skill, self.direction, player)  
        magic_group.add(magic)
  
    def check_alive(self):
        if self.health <= 0:
            self.speed = 0
            self.alive = False
            self.update_action(2)

    def update(self):
        self.update_animation()
        self.check_alive()

    def draw(self, offset=(0, 0)):
        if self.char_type in ["Enemy_1", "Enemy_2", "Enemy_3"]:
            render_pos_x = self.rect.x - offset[0]
            render_pos_y = self.rect.y - offset[1] 
        else:
            render_pos_x = self.rect.centerx - self.image.get_width() // 2 - offset[0]
            render_pos_y = self.rect.y - self.image.get_height() // 2 - offset[1] 
        self.screen.blit(pygame.transform.flip(self.image, self.flip, False), (render_pos_x, render_pos_y))
   
        if self.char_type != "Player": 
            health_bar_bg_x = self.rect.x - 2 - offset[0]
            health_bar_bg_y = self.rect.y - 22 - offset[1]
            health_bar_red_x = self.rect.x - offset[0]
            health_bar_red_y = self.rect.y - 20 - offset[1]
            health_bar_green_x = self.rect.x - offset[0]
            health_bar_green_y = self.rect.y - 20 - offset[1]

            ratio = self.health / self.max_health
            pygame.draw.rect(self.screen, "black", [health_bar_bg_x, health_bar_bg_y, 74, 14])
            pygame.draw.rect(self.screen, "red", [health_bar_red_x, health_bar_red_y, 70, 10])
            pygame.draw.rect(self.screen, "green", [health_bar_green_x, health_bar_green_y, 70 * ratio, 10])