import pygame
import os
from setting import TILE_SIZE

decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def draw(self, screen, offset=(0, 0)): 
        rect = self.rect
        render_pos_x = rect.x - offset[0]
        render_pos_y = rect.y - offset[1]
        screen.blit(self.image, (render_pos_x, render_pos_y))

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def draw(self, screen, offset=(0, 0)): 
        rect = self.rect
        render_pos_x = rect.x - offset[0]
        render_pos_y = rect.y - offset[1]
        screen.blit(self.image, (render_pos_x, render_pos_y))

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    def draw(self, screen, offset=(0, 0)): 
        rect = self.rect
        render_pos_x = rect.x - offset[0]
        render_pos_y = rect.y - offset[1]
        screen.blit(self.image, (render_pos_x, render_pos_y))

