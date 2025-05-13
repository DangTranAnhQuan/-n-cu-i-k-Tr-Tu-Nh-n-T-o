import numpy as np
import random
import os
import json
from setting import TILE_SIZE, ROWS, COLS

GROUND_ENEMY_ACTIONS = {
    "MOVE_LEFT": 0,
    "MOVE_RIGHT": 1,
    "STAY_STILL": 2,
    "ATTACK": 3
}
NUM_GROUND_ACTIONS = len(GROUND_ENEMY_ACTIONS)

FLYING_ENEMY_ACTIONS = {
    "MOVE_LEFT": 0,
    "MOVE_RIGHT": 1,
    "MOVE_UP": 2,
    "MOVE_DOWN": 3,
    "STAY_STILL": 4,
    "ATTACK": 5
}
NUM_FLYING_ACTIONS = len(FLYING_ENEMY_ACTIONS)


class QLearningAgent:
    def __init__(self, enemy_type, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay_rate=0.999, min_exploration_rate=0.1, q_table_filename_prefix="q_table"):
        self.enemy_type = enemy_type
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.exploration_decay_rate = 0.9995
        self.min_epsilon = 0.05         
        self.q_table_filename = f"{q_table_filename_prefix}_{self.enemy_type}.json"

        if self.enemy_type in ["Enemy_1", "Enemy_2", "Enemy_3", "Boss Game"]:
            self.num_actions = NUM_GROUND_ACTIONS
            self.action_map = GROUND_ENEMY_ACTIONS
        elif self.enemy_type == "FlyingDemon":
            self.num_actions = NUM_FLYING_ACTIONS
            self.action_map = FLYING_ENEMY_ACTIONS
        else:
            raise ValueError(f"Unknown enemy type for QLearningAgent: {self.enemy_type}")

        self.q_table = {}
        self.load_q_table()

    def get_q_value(self, state_tuple, action_index):
        default_q_values = self.q_table.get(state_tuple, np.zeros(self.num_actions))
        if 0 <= action_index < self.num_actions:
            return default_q_values[action_index]
        else:
            return -float('inf') 

    def update_q_value(self, state_tuple, action_index, reward, next_state_tuple):
        old_value = self.get_q_value(state_tuple, action_index)
        if old_value == -float('inf') : 
             return

        next_max_q = np.max(self.q_table.get(next_state_tuple, np.zeros(self.num_actions)))
        new_value = old_value + self.lr * (reward + self.gamma * next_max_q - old_value)
        
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(self.num_actions)
        
        if 0 <= action_index < self.num_actions:
            self.q_table[state_tuple][action_index] = new_value

    def choose_action(self, state_tuple):
        if random.uniform(0, 1) < self.epsilon:
            action_index = random.choice(range(self.num_actions))
        else:
            q_values_for_state = self.q_table.get(state_tuple, np.zeros(self.num_actions))
            action_index = np.argmax(q_values_for_state)
        return action_index

    def decay_exploration_rate(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.exploration_decay_rate)

    def save_q_table(self):
        q_table_serializable = {str(k): v.tolist() for k, v in self.q_table.items()}
        try:
            with open(self.q_table_filename, 'w') as f:
                json.dump(q_table_serializable, f)
        except Exception as e:
            print(f"Error saving Q-table for {self.enemy_type}: {e}")

    def load_q_table(self):
        try:
            if os.path.exists(self.q_table_filename):
                with open(self.q_table_filename, 'r') as f:
                    q_table_loaded_serializable = json.load(f)
                    self.q_table = {} 
                    for k_str, v_list in q_table_loaded_serializable.items():
                        state_tuple_loaded = eval(k_str)
                        q_values_from_file = np.array(v_list)

                        if len(q_values_from_file) == self.num_actions:
                            self.q_table[state_tuple_loaded] = q_values_from_file
                        elif len(q_values_from_file) < self.num_actions:
                            new_q_values = np.zeros(self.num_actions)
                            new_q_values[:len(q_values_from_file)] = q_values_from_file
                            self.q_table[state_tuple_loaded] = new_q_values
        except FileNotFoundError:
            print(f"No Q-table file for {self.enemy_type}. Starting new.")
            self.q_table = {}
        except Exception as e:
            print(f"Error loading Q-table for {self.enemy_type}: {e}. Starting new.")
            self.q_table = {}

def get_q_learning_state_ground(enemy, player, world_data):
    if not world_data: return None 

    player_dx = player.rect.centerx - enemy.rect.centerx
    player_dy = player.rect.centery - enemy.rect.centery

    if abs(player_dx) < TILE_SIZE * 0.75: player_rel_x_cat = 0 
    elif abs(player_dx) < TILE_SIZE * 2.5: player_rel_x_cat = -1 if player_dx < 0 else 1 
    else: player_rel_x_cat = -2 if player_dx < 0 else 2
    
    player_approachable = 0
    if abs(player_dy) < TILE_SIZE * 1.5 : 
         player_approachable = 1
    
    if player_approachable == 0:
        player_rel_x_cat = 99 

    enemy_col = int(enemy.rect.centerx // TILE_SIZE)
    enemy_row = int((enemy.rect.bottom -1) // TILE_SIZE) 
    enemy_row = min(max(0, enemy_row), ROWS - 1)

    can_move_L = 1
    can_move_R = 1
    obstacle_in_front = 0
    
    left_tile_col = enemy_col - 1
    if left_tile_col < 0 or \
       (0 <= enemy_row < len(world_data) and 0 <= left_tile_col < len(world_data[0]) and world_data[enemy_row][left_tile_col] in range(0, 60)):
        can_move_L = 0
    elif 0 <= enemy_row + 1 < len(world_data) and 0 <= left_tile_col < len(world_data[0]) and \
         world_data[enemy_row + 1][left_tile_col] not in range(0,60) and \
         (enemy_row + 2 >= ROWS or (0 <= enemy_row + 2 < len(world_data) and world_data[enemy_row+2][left_tile_col] not in range(0,60))):
        can_move_L = 0

    right_tile_col = enemy_col + 1
    if right_tile_col >= COLS or \
       (0 <= enemy_row < len(world_data) and 0 <= right_tile_col < len(world_data[0]) and world_data[enemy_row][right_tile_col] in range(0, 60)):
        can_move_R = 0
    elif 0 <= enemy_row + 1 < len(world_data) and 0 <= right_tile_col < len(world_data[0]) and \
         world_data[enemy_row + 1][right_tile_col] not in range(0,60) and \
         (enemy_row + 2 >= ROWS or (0 <= enemy_row + 2 < len(world_data) and world_data[enemy_row+2][right_tile_col] not in range(0,60))):
        can_move_R = 0

    check_col_front = enemy_col + enemy.direction
    if 0 <= check_col_front < COLS:
        if 0 <= enemy_row < len(world_data) and world_data[enemy_row][check_col_front] in range(0, 60):
            obstacle_in_front = 1
        elif 0 <= enemy_row + 1 < len(world_data) and \
             world_data[enemy_row + 1][check_col_front] not in range(0,60) and \
             (enemy_row + 2 >= ROWS or (0 <= enemy_row + 2 < len(world_data) and world_data[enemy_row+2][check_col_front] not in range(0,60))):
            obstacle_in_front = 2
    else:
        obstacle_in_front = 1 

    player_is_in_front = 0
    if player_approachable == 1:
        if (enemy.direction == 1 and player_rel_x_cat >= 0) or \
           (enemy.direction == -1 and player_rel_x_cat <= 0):
            player_is_in_front = 1
            
    return (player_rel_x_cat, player_approachable, can_move_L, can_move_R, obstacle_in_front, player_is_in_front)

def get_q_learning_state_flying(enemy, player, world_data):
    if not world_data: return None

    player_dx = player.rect.centerx - enemy.rect.centerx
    player_dy = player.rect.centery - enemy.rect.centery

    if abs(player_dx) < TILE_SIZE * 1.5: dx_cat = 0 
    elif abs(player_dx) < TILE_SIZE * 5: dx_cat = -1 if player_dx < 0 else 1
    else: dx_cat = -2 if player_dx < 0 else 2

    if abs(player_dy) < TILE_SIZE * 1.5: dy_cat = 0
    elif abs(player_dy) < TILE_SIZE * 5: dy_cat = -1 if player_dy < 0 else 1
    else: dy_cat = -2 if player_dy < 0 else 2

    enemy_col = int(enemy.rect.centerx // TILE_SIZE)
    enemy_row = int(enemy.rect.centery // TILE_SIZE)
    enemy_row = min(max(0, enemy_row), ROWS - 1)
    enemy_col = min(max(0, enemy_col), COLS - 1)

    obs_L, obs_R, obs_U, obs_D = 0,0,0,0
    def is_obstacle(r, c):
        return not (0 <= r < ROWS and 0 <= c < COLS and world_data[r][c] not in range(0, 60))

    if is_obstacle(enemy_row, enemy_col - 1): obs_L = 1
    if is_obstacle(enemy_row, enemy_col + 1): obs_R = 1
    if is_obstacle(enemy_row - 1, enemy_col): obs_U = 1
    if is_obstacle(enemy_row + 1, enemy_col): obs_D = 1
        
    return (dx_cat, dy_cat, obs_L, obs_R, obs_U, obs_D)


def calculate_reward_ground(enemy, old_state, action_idx, new_state, player, world_data):
    base_action_cost = -0.8 
    reward = base_action_cost 

    if new_state is None: 
        return reward - 20.0 
    old_player_rel_x, old_player_appr, old_can_L, old_can_R, old_obs_front, old_player_front = old_state
    new_player_rel_x, new_player_appr, new_can_L, new_can_R, new_obs_front, new_player_front = new_state
    
    try:
        action_taken_str = list(GROUND_ENEMY_ACTIONS.keys())[list(GROUND_ENEMY_ACTIONS.values()).index(action_idx)]
    except ValueError:
        print(f"Critical Error: action_idx {action_idx} not in GROUND_ENEMY_ACTIONS for ground enemy.")
        return reward - 25.0 

    if old_player_appr == 1 and new_player_appr == 1:
        dist_old = abs(old_player_rel_x)
        dist_new = abs(new_player_rel_x)
        
        if action_taken_str in ["MOVE_LEFT", "MOVE_RIGHT"]:
            if dist_new < dist_old:
                reward += 3.5  
                if dist_new == 0 and new_player_front == 1: 
                    reward += 1.5 
            elif dist_new > dist_old and dist_old <= 1 :
                 reward -= 2.5

    in_optimal_attack_pos_new = (new_player_appr == 1 and new_player_rel_x == 0 and new_player_front == 1)
    
    if in_optimal_attack_pos_new:
         reward += 2.0 

    if action_taken_str == "ATTACK":
        if in_optimal_attack_pos_new:
            reward += 8.0 
            if hasattr(enemy, 'did_damage_this_step') and enemy.did_damage_this_step:
                reward += 18.0 
                enemy.did_damage_this_step = False
        elif new_player_appr == 1 and new_player_front == 1:
            reward -= 3.0
        elif new_player_appr == 1 :
             reward -= 6.0
        else:
            reward -= 9.0 

    if action_taken_str == "MOVE_LEFT":
        if old_can_L == 0 :
            reward -= 7.0
        elif new_player_rel_x == old_player_rel_x and old_player_appr == 1 and not in_optimal_attack_pos_new:
            reward -= 1.0
    elif action_taken_str == "MOVE_RIGHT":
        if old_can_R == 0:
            reward -= 7.0
        elif new_player_rel_x == old_player_rel_x and old_player_appr == 1 and not in_optimal_attack_pos_new:
            reward -= 1.0

    if action_taken_str == "STAY_STILL":
        if new_player_appr == 1:
            if not in_optimal_attack_pos_new:
                if abs(new_player_rel_x) <= 1 and new_player_front == 1 :
                     reward -= 3.0
                elif abs(new_player_rel_x) > 1 :
                     reward -= 2.5
        else:
            reward -= 0.5

    if not player.alive :
        reward -= 30.0

    if new_player_appr == 1 and new_player_front == 1 and not in_optimal_attack_pos_new:
        reward += 0.5

    return reward

def calculate_reward_flying(enemy, old_state, action_idx, new_state, player, world_data):
    base_action_cost = -0.8
    reward = base_action_cost

    if new_state is None:
        return reward - 20.0

    old_dx, old_dy, old_oL, old_oR, old_oU, old_oD = old_state
    new_dx, new_dy, new_oL, new_oR, new_oU, new_oD = new_state

    try:
        action_taken_str = list(FLYING_ENEMY_ACTIONS.keys())[list(FLYING_ENEMY_ACTIONS.values()).index(action_idx)]
    except ValueError:
        print(f"Critical Error: action_idx {action_idx} not in FLYING_ENEMY_ACTIONS for flying enemy.")
        return reward - 25.0

    dist_old = abs(old_dx) + abs(old_dy)
    dist_new = abs(new_dx) + abs(new_dy)

    if action_taken_str not in ["ATTACK", "STAY_STILL"]:
        if dist_new < dist_old:
            reward += 3.0 
            if dist_new == 0:
                reward += 1.0
        elif dist_new > dist_old and dist_old <= 1:
            reward -= 2.0

    in_optimal_attack_pos_new_flying = (dist_new == 0)
    if in_optimal_attack_pos_new_flying:
        reward += 2.5

    if action_taken_str == "ATTACK":
        if in_optimal_attack_pos_new_flying:
            reward += 8.0
            if hasattr(enemy, 'did_damage_this_step') and enemy.did_damage_this_step:
                reward += 18.0
                enemy.did_damage_this_step = False
        else:
            reward -= 7.0

    collided_with_obstacle = False
    if (action_taken_str == "MOVE_LEFT" and old_oL == 1) or \
       (action_taken_str == "MOVE_RIGHT" and old_oR == 1) or \
       (action_taken_str == "MOVE_UP" and old_oU == 1) or \
       (action_taken_str == "MOVE_DOWN" and old_oD == 1):
        reward -= 7.0
        collided_with_obstacle = True

    if action_taken_str not in ["ATTACK", "STAY_STILL"] and new_dx == old_dx and new_dy == old_dy:
        if collided_with_obstacle:
             reward -= 0.5
        else:
            reward -= 1.5


    if action_taken_str == "STAY_STILL":
        if not in_optimal_attack_pos_new_flying and dist_new <= 1 :
            reward -= 2.5
        elif dist_new > 1 :
             reward -= 2.0

    if not player.alive:
        reward -= 30.0

    return reward