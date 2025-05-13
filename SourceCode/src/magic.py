import pygame
import os
import entities.enemy as enemy

magic_group = pygame.sprite.Group()

class Magic(pygame.sprite.Sprite):
    def __init__(self, screen, world, x, y, char_type, scale, direction, player):
        super().__init__()
        self.screen = screen
        self.world = world
        self.char_type = char_type
        self.player = player
        self.enemy_group = enemy.enemy_group
        self.magic_animation = []
        self.update_time = pygame.time.get_ticks()
        self.speed = 30 * scale * 1.75
        self.direction = direction
        self.img_index = 0

        num_img = len(os.listdir(f'assets/Character/{self.char_type}/Magic'))
        for i in range(num_img):
            img = pygame.image.load(f'assets/Character/{self.char_type}/Magic/{i + 1}.png')
            img = pygame.transform.scale(img, (int(img.get_width()) * scale, int(img.get_height()) * scale))
            self.magic_animation.append(img)

        self.image = self.magic_animation[self.img_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        self.image = self.magic_animation[self.img_index]

        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        for tile in self.world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.img_index += 1
            self.rect.x += (self.direction * self.speed)

            if self.img_index >= len(self.magic_animation):
                self.kill()

        if self.char_type == "Player":
            collided = pygame.sprite.spritecollideany(self, self.enemy_group)
            if collided and collided.alive:
                collided.health -= self.player.attack * 2
                self.kill()
        else:
            if self.rect.colliderect(self.player.rect):
                self.player.take_damage(5, 100)
                self.kill()
    def draw(self, screen, offset=(0, 0)):
        image_to_draw = self.image 
        render_pos_x = self.rect.x - offset[0]
        render_pos_y = self.rect.y - offset[1]
        screen.blit(image_to_draw, (render_pos_x, render_pos_y))