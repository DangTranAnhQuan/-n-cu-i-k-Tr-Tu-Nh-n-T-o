import pygame, random, os, csv, queue
import numpy as np
import pandas as pd
from collections import deque

pygame.font.init()
font = pygame.font.SysFont('Futura', 30)

screen_width = 1300
screen_height = screen_width * 0.5
FPS = 60

gravity = 0.25
ROWS = 16
COLS = 150

TILE_SIZE = screen_height // ROWS
TILE_TYPES = 89
level = 1
MAP = 2

scale = 0.3
moving_left = False
moving_right = False
attack_1 = False
attack_2 = False
skill = False
recover = False
dash = False
parry = False
skill_cooldown = 1500 
recover_cooldown = 5000
dash_cooldown = 1000
parry_cooldown = 500
last_skill_time = 0 
last_recover_time = 0
last_dash_time = 0
last_parry_time = 0

AVAILABLE_SEARCH_ALGORITHMS_DISPLAY_NAMES = [
    "BFS", 
    "A*", 
    "Steepest HC",         
    "And Or Search", 
    "Backtracking",   
    "Q-Learning"       
]
current_global_search_algorithm_index = 0 

show_enemy_algorithm_stats = False
show_enemy_calculated_path = False
stats_font = pygame.font.SysFont('Arial', 16)
show_enemy_vision_rect = False 