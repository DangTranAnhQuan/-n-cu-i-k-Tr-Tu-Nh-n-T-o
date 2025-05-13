import pygame
from .baseCharacter import BaseCharacter
from Search_Algorithm import *
from q_learning_logic import *
import random
import setting

enemy_group = pygame.sprite.Group()
ACTION_MOVE_LEFT = 0
ACTION_MOVE_RIGHT = 1
ACTION_ATTACK = 2
ACTION_IDLE = 3
NUM_ACTIONS_GROUND_ENEMY = 4 

class Enemy(BaseCharacter):
    def __init__(self, screen, world, player, enemy_type, x, y, scale, speed, attack): 
        super().__init__(screen, world, enemy_type, x, y, scale, speed, attack)
        self.player = player
        self.health = 50
        self.max_health = self.health

        self.attack_cooldown = 0
        self.idle = False
        self.idle_counter = 0
        self.move_counter = 0
        
        self.search_path = [] 
        self.next_state = None 
        self.in_tile = False 

        self.algorithm_stats = {} 
        self.full_path_tile_coords_for_drawing = [] 

        self.q_agent = None
        self.last_q_state = None
        self.last_q_action_idx = None
        self.q_learning_episode_count = 0 

        self.did_damage_this_step = False
        try:
            self.q_agent = QLearningAgent(enemy_type=self.char_type)
        except ValueError as e:
            self.q_agent = None
        
        self.search_algorithm_functions = {
            "BFS": bfs,
            "A*": a_star_solve,
            "Steepest HC": steepest_ascent_hill_climbing,
            "And Or Search": and_or_solve,
            "Backtracking": backtracking_search,
            "Q-Learning": self.q_learning_decision_placeholder
        }
        
        if enemy_type == "FlyingDemon":
            vision_width = self.rect.width * 20
            vision_height = self.rect.height * 20
        elif enemy_type == "Boss Game": 
            vision_width = self.rect.width * 15
            vision_height = self.rect.height
        else:
            vision_width = self.rect.width * 5 
            vision_height = self.rect.height
        self.vision = pygame.Rect(0, 0, vision_width, vision_height)
        self.vision.center = self.rect.center
        
        self.path_update_interval = 500  
        self.last_path_update_time = 0
    
    def update(self):
        super().update()
        self.vision.center = self.rect.center

    def draw(self, offset=(0, 0)):
        super().draw(offset) 
        
        if setting.show_enemy_vision_rect: 
            vision_rect_on_screen_x = self.vision.x - offset[0]
            vision_rect_on_screen_y = self.vision.y - offset[1]
            drawable_vision_rect = pygame.Rect(vision_rect_on_screen_x, 
                                               vision_rect_on_screen_y, 
                                               self.vision.width, 
                                               self.vision.height)
            pygame.draw.rect(self.screen, "blue", drawable_vision_rect, 1)
            
        if setting.show_enemy_algorithm_stats and hasattr(self, 'algorithm_stats') and self.algorithm_stats:
            stats_base_y = self.rect.y - offset[1] - 25 

            info_to_display = [
                f"Algo: {self.algorithm_stats.get('name', 'N/A')}",
                f"Time: {self.algorithm_stats.get('time', 0):.4f}s",
                f"Nodes: {self.algorithm_stats.get('nodes', 0)}",
                f"PathLen: {self.algorithm_stats.get('length', 0)}"
            ]

            for i, text_content in enumerate(info_to_display):
                text_surface = setting.stats_font.render(text_content, True, (255, 20, 147)) 
                text_x_pos = self.rect.x - offset[0]
                text_y_pos = stats_base_y - (len(info_to_display) - 1 - i) * (setting.stats_font.get_height() + 2)
                self.screen.blit(text_surface, (text_x_pos, text_y_pos))

        if setting.show_enemy_calculated_path and hasattr(self, 'full_path_tile_coords_for_drawing') and self.full_path_tile_coords_for_drawing:
            path_points_on_screen = []
            for (r, c) in self.full_path_tile_coords_for_drawing: 
                screen_x = c * setting.TILE_SIZE + setting.TILE_SIZE // 2 - offset[0]
                screen_y = r * setting.TILE_SIZE + setting.TILE_SIZE // 2 - offset[1]
                path_points_on_screen.append((screen_x, screen_y))
            
            if len(path_points_on_screen) >= 2:
                pygame.draw.lines(self.screen, (0, 100, 255, 200), False, path_points_on_screen, 2) 
            elif path_points_on_screen: 
                pygame.draw.circle(self.screen, (0, 100, 255), path_points_on_screen[0], 3)


    def calculate_and_set_path(self):
        current_world_list_of_lists_for_search = [list(row) for row in self.world.world_data]
        start_state_tuple = get_start(self, current_world_list_of_lists_for_search)
        
        selected_algo_display_name = setting.AVAILABLE_SEARCH_ALGORITHMS_DISPLAY_NAMES[setting.current_global_search_algorithm_index]

        if find_enemy(start_state_tuple) is None:
            self.reset_pathfinding_info(f"{selected_algo_display_name}: Start Error")
            return

        self.goal_state_tuple = get_goal(self, start_state_tuple, self.player)
        if find_enemy(self.goal_state_tuple) is None:
            self.reset_pathfinding_info(f"{selected_algo_display_name}: Goal Error")
            return
        
        algorithm_to_run = self.search_algorithm_functions.get(selected_algo_display_name)

        if algorithm_to_run is None:
            algorithm_to_run = self.search_algorithm_functions.get("A*", self.search_algorithm_functions.get("BFS"))
            if algorithm_to_run is None:
                self.reset_pathfinding_info("Algorithm Load Error")
                return

        path_states_list, metrics_dict = algorithm_to_run(self, start_state_tuple, self.goal_state_tuple)
        
        self.algorithm_stats = metrics_dict
        
        if path_states_list:
            self.search_path = path_states_list
            self.full_path_tile_coords_for_drawing = []
            start_tile_pos = find_enemy(start_state_tuple)
            if start_tile_pos is not None:
                self.full_path_tile_coords_for_drawing.append((start_tile_pos[0], start_tile_pos[1]))
            for state_in_path in self.search_path:
                tile_pos = find_enemy(state_in_path) 
                if tile_pos is not None:
                    self.full_path_tile_coords_for_drawing.append((tile_pos[0], tile_pos[1]))
            
            if self.search_path:
                self.next_state = self.search_path.pop(0)
                self.in_tile = False
            else:
                self.next_state = None
                self.full_path_tile_coords_for_drawing = []
        else: 
            self.search_path = []
            self.next_state = None
            self.full_path_tile_coords_for_drawing = []
        
    def q_learning_decision_placeholder(self, enemy_obj, start_state, goal_state):
        return [], {"time": 0, "nodes": 0, "length": 0, "name": "Q-Learning"}
     
    def reset_pathfinding_info(self, status_name="N/A", time_taken=0, nodes_explored=0, path_len=0):
        self.search_path = []
        self.next_state = None
        self.full_path_tile_coords_for_drawing = []
        self.algorithm_stats = {
            "name": status_name,
            "time": time_taken,
            "nodes": nodes_explored,
            "length": path_len
        }
        if status_name == "Q-Learning" or "Q-Learning" in status_name:
            if self.q_agent:
                self.algorithm_stats["epsilon"] = round(self.q_agent.epsilon, 3)
                self.algorithm_stats["episodes"] = self.q_learning_episode_count
        
    def move_random(self):
        if not self.idle and random.randint(1, 200) == 1:
            self.update_action(0) 
            self.idle = True
            self.idle_counter = 150 

        if not self.idle:
            ai_moving_right = self.direction == 1
            self.move(not ai_moving_right, ai_moving_right) 
            self.update_action(1) 
            self.move_counter += 1

            if self.move_counter > setting.TILE_SIZE * 3:
                self.move_counter = 0
                self.direction *= -1
        else:
            self.idle_counter -= 1
            if self.idle_counter <= 0:
                self.idle = False
    
    def ai(self):
        if not self.alive:
            return
        
        current_world_data = self.world.world_data
        if not current_world_data:
            self.move_random()
            return

        self.did_damage_this_step = False
        
        if not self.player.alive:
            if self.q_agent and self.last_q_state and self.last_q_action_idx is not None:
                final_reward_player_dead = -30.0 
                
                current_q_state_at_player_death = None
                if self.char_type in ["Enemy_1", "Enemy_2", "Enemy_3", "Boss Game"]:
                    current_q_state_at_player_death = get_q_learning_state_ground(self, self.player, current_world_data)
                elif self.char_type == "FlyingDemon":
                    current_q_state_at_player_death = get_q_learning_state_flying(self, self.player, current_world_data)

                if current_q_state_at_player_death:
                    self.q_agent.update_q_value(self.last_q_state, self.last_q_action_idx, final_reward_player_dead, current_q_state_at_player_death)
                    self.q_agent.decay_exploration_rate()
                    self.q_learning_episode_count += 1
                    if self.q_learning_episode_count > 0 and self.q_learning_episode_count % 20 == 0:
                        self.q_agent.save_q_table()
            
            self.update_action(0)
            current_algo_name_display_on_death = setting.AVAILABLE_SEARCH_ALGORITHMS_DISPLAY_NAMES[setting.current_global_search_algorithm_index]
            if setting.show_enemy_algorithm_stats or setting.show_enemy_calculated_path:
                if current_algo_name_display_on_death == "Q-Learning" and self.q_agent:
                     self.reset_pathfinding_info(status_name=f"Q-L: Player Dead (Eps: {self.q_learning_episode_count}, EpsVal: {self.q_agent.epsilon:.2f})")
                else:
                    self.reset_pathfinding_info("Player Dead")
            self.move_random()
            self.last_q_state = None
            self.last_q_action_idx = None
            return

        current_algo_name_display = setting.AVAILABLE_SEARCH_ALGORITHMS_DISPLAY_NAMES[setting.current_global_search_algorithm_index]

        if self.attacking:
            dealt_damage_this_frame_common = False
            if self.char_type in ["Enemy_1", "Enemy_2", "Enemy_3", "Boss Game"]:
                if self.action == 3 and self.img_index in [max(0, len(self.animation_list[self.action]) // 3 -1), max(0, 2 * len(self.animation_list[self.action]) // 3 -1)]: 
                    attack_hitbox = self._create_directional_attack_hitbox()
                    if attack_hitbox and attack_hitbox.colliderect(self.player.rect):
                        if (self.direction == 1 and self.player.rect.centerx >= self.rect.centerx - self.rect.width*0.1) or \
                           (self.direction == -1 and self.player.rect.centerx <= self.rect.centerx + self.rect.width*0.1):
                            self.player.take_damage(self.attack, 100)
                            dealt_damage_this_frame_common = True
                elif self.action == 4 and self.img_index in [max(0,len(self.animation_list[self.action]) // 2 -1)]: 
                    attack_hitbox = self._create_directional_attack_hitbox()
                    if attack_hitbox and attack_hitbox.colliderect(self.player.rect):
                         if (self.direction == 1 and self.player.rect.centerx >= self.rect.centerx - self.rect.width*0.1) or \
                            (self.direction == -1 and self.player.rect.centerx <= self.rect.centerx + self.rect.width*0.1):
                            self.player.take_damage(self.attack * 1.2, 100)
                            dealt_damage_this_frame_common = True
            elif self.char_type == "FlyingDemon" and self.action == 3: 
                pass 

            if dealt_damage_this_frame_common:
                self.did_damage_this_step = True

            if self.img_index >= len(self.animation_list[self.action]) - 1:
                self.attacking = False
                self.attack_cooldown = 70 
                if self.char_type == "FlyingDemon" and self.action == 3:
                    self.skill() 
            return 

        if current_algo_name_display == "Q-Learning":
            if not self.q_agent:
                self.move_random()
                if setting.show_enemy_algorithm_stats: self.reset_pathfinding_info("Q-Learning: No Agent")
                return

            current_q_state_tuple = None
            if self.char_type in ["Enemy_1", "Enemy_2", "Enemy_3", "Boss Game"]:
                current_q_state_tuple = get_q_learning_state_ground(self, self.player, current_world_data)
            elif self.char_type == "FlyingDemon":
                current_q_state_tuple = get_q_learning_state_flying(self, self.player, current_world_data)
            
            if current_q_state_tuple is None:
                self.move_random()
                if setting.show_enemy_algorithm_stats: self.reset_pathfinding_info(status_name=f"Q-L: State Error (Eps: {self.q_learning_episode_count})")
                return

            if self.last_q_state is not None and self.last_q_action_idx is not None:
                reward = 0
                if self.char_type in ["Enemy_1", "Enemy_2", "Enemy_3", "Boss Game"]:
                    reward = calculate_reward_ground(self, self.last_q_state, self.last_q_action_idx, current_q_state_tuple, self.player, current_world_data)
                elif self.char_type == "FlyingDemon":
                    reward = calculate_reward_flying(self, self.last_q_state, self.last_q_action_idx, current_q_state_tuple, self.player, current_world_data)
                
                self.q_agent.update_q_value(self.last_q_state, self.last_q_action_idx, reward, current_q_state_tuple)
                self.q_agent.decay_exploration_rate()

            action_idx = self.q_agent.choose_action(current_q_state_tuple)
            
            move_left_q, move_right_q, move_down_q = False, False, None
            action_taken_str = ""
            q_decided_to_attack = False

            current_action_map = self.q_agent.action_map
            try:
                action_taken_str = list(current_action_map.keys())[list(current_action_map.values()).index(action_idx)]
            except ValueError:
                 action_taken_str = "STAY_STILL" 
                 action_idx = current_action_map.get("STAY_STILL", 0)

            if action_taken_str == "ATTACK":
                q_decided_to_attack = True 
                if not self.attacking and self.attack_cooldown == 0:
                    if self.player.rect.centerx > self.rect.centerx:
                        self.direction = 1
                        self.flip = False
                    else:
                        self.direction = -1
                        self.flip = True
                        
                    attack_animation_action = 3 
                    if self.char_type in ["Enemy_1", "Enemy_2", "Enemy_3", "Boss Game"]:
                         attack_animation_action = random.choice([3,4]) 
                    self.update_action(attack_animation_action)
                    self.attacking = True 

            elif action_taken_str == "MOVE_LEFT": 
                move_left_q = True
            elif action_taken_str == "MOVE_RIGHT": 
                move_right_q = True
            elif action_taken_str == "MOVE_UP" and self.char_type == "FlyingDemon": 
                move_down_q = False
            elif action_taken_str == "MOVE_DOWN" and self.char_type == "FlyingDemon": 
                move_down_q = True
            
            if not q_decided_to_attack and not self.attacking:
                self.move(move_left_q, move_right_q, move_down_q)
                if move_left_q or move_right_q or (self.char_type == "FlyingDemon" and move_down_q is not None):
                    self.update_action(1) 
                else: 
                    self.update_action(0) 
            
            self.last_q_state = current_q_state_tuple
            self.last_q_action_idx = action_idx

            if setting.show_enemy_algorithm_stats:
                 q_val_for_action = "N/A"
                 if self.q_agent and 0 <= action_idx < self.q_agent.num_actions:
                     q_val_for_action = f"{self.q_agent.get_q_value(current_q_state_tuple, action_idx):.2f}"

                 self.algorithm_stats = {
                    "name": "Q-Learning",
                    "epsilon": round(self.q_agent.epsilon, 3) if self.q_agent else -1,
                    "action": action_taken_str, 
                    "state": str(current_q_state_tuple), 
                    "episodes": self.q_learning_episode_count,
                    "Q_val": q_val_for_action
                 }
            if setting.show_enemy_calculated_path:
                 self.full_path_tile_coords_for_drawing = []

        else: 
            if self.last_q_state is not None: 
                self.last_q_state = None
                self.last_q_action_idx = None
                if self.q_agent:
                    self.q_agent.save_q_table()

            player_in_vision = self.vision.colliderect(self.player.rect)
            player_in_attack_range = False

            if player_in_vision:
                if self.char_type == "FlyingDemon":
                    player_row = int((self.player.rect.bottom - 1) // setting.TILE_SIZE)
                    enemy_row = int((self.rect.bottom - 1) // setting.TILE_SIZE)
                    attack_dist_x = setting.TILE_SIZE * 5 
                    if abs(self.rect.centerx - self.player.rect.centerx) < attack_dist_x and abs(enemy_row - player_row) <= 0.5 :
                        player_in_attack_range = True
                else: 
                    attack_width_multiplier = -0.2 
                    if self.char_type == "Boss Game": 
                        attack_width_multiplier = 1.5
                    effective_attack_range_x = self._original_width * attack_width_multiplier
                    
                    can_attack_player_directionally = False
                    if (self.direction == 1 and \
                        self.player.rect.centerx > self.rect.centerx and \
                        self.player.rect.left < self.rect.right + effective_attack_range_x) or \
                       (self.direction == -1 and \
                        self.player.rect.centerx < self.rect.centerx and \
                        self.player.rect.right > self.rect.left - effective_attack_range_x):
                        can_attack_player_directionally = True
                    
                    if can_attack_player_directionally and abs(self.rect.centery - self.player.rect.centery) < setting.TILE_SIZE * 1.0:
                         player_in_attack_range = True
            
            if player_in_vision and player_in_attack_range:
                if not self.attacking and self.attack_cooldown == 0: 
                    if setting.show_enemy_algorithm_stats or setting.show_enemy_calculated_path:
                        self.reset_pathfinding_info(f"{current_algo_name_display}: Attacking")
                    
                    if self.player.rect.centerx > self.rect.centerx: self.direction = 1; self.flip = False
                    else: self.direction = -1; self.flip = True
                    
                    action_choice_melee = random.choice([3, 4]) if self.char_type != "FlyingDemon" else 3
                    self.update_action(action_choice_melee)
                    self.attacking = True
                elif not self.attacking and self.attack_cooldown > 0 : 
                    self.update_action(0) 
            
            elif player_in_vision and not player_in_attack_range: 
                if self.attacking: self.attacking = False 
                
                current_time = pygame.time.get_ticks()
                needs_new_path = (not self.search_path and not self.next_state) or \
                                 (current_time - self.last_path_update_time > self.path_update_interval)
                if needs_new_path:
                    self.calculate_and_set_path() 
                    self.last_path_update_time = current_time 
                
                if self.next_state:
                    target_tile_rc = find_enemy(self.next_state) 
                    if target_tile_rc is None:
                        self.reset_pathfinding_info(f"{current_algo_name_display}: Path Invalid")
                        self.move_random()
                        return 

                    target_r, target_c = target_tile_rc[0], target_tile_rc[1]
                    target_center_x = target_c * setting.TILE_SIZE + setting.TILE_SIZE // 2
                    target_center_y = target_r * setting.TILE_SIZE + setting.TILE_SIZE // 2 
                    
                    dx_to_target = target_center_x - self.rect.centerx
                    dy_to_target = target_center_y - self.rect.centery 
                    move_left_p, move_right_p, move_down_flyer_p = False, False, None 

                    threshold = self.speed + 1 
                    if abs(dx_to_target) >= threshold: 
                        if dx_to_target > 0: move_right_p = True
                        else: move_left_p = True
                    
                    if self.char_type == "FlyingDemon":
                        if abs(dy_to_target) >= threshold: 
                            if dy_to_target > 0: move_down_flyer_p = True
                            else: move_down_flyer_p = False
                    
                    if move_left_p or move_right_p or move_down_flyer_p is not None:
                        self.move(move_left_p, move_right_p, move_down_flyer_p)
                        self.update_action(1)
                    else: 
                        self.update_action(0) 

                    if abs(self.rect.centerx - target_center_x) < self.speed * 0.8 and \
                       (self.char_type != "FlyingDemon" or abs(self.rect.centery - target_center_y) < self.speed * 0.8) :
                        self.in_tile = True

                    if self.in_tile:
                        if self.search_path: 
                            self.next_state = self.search_path.pop(0)
                            self.in_tile = False
                        else: 
                            self.next_state = None
                            self.full_path_tile_coords_for_drawing = []
                else: 
                    self.move_random()
            else: 
                if self.attacking: self.attacking = False
                if setting.show_enemy_algorithm_stats or setting.show_enemy_calculated_path:
                    if not self.algorithm_stats or self.algorithm_stats.get("name") != "No Vision":
                        self.reset_pathfinding_info(f"{current_algo_name_display}: No Vision")
                self.move_random()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def check_alive(self): 
        super().check_alive() 
        if not self.alive:
            if self.q_agent and self.last_q_state and self.last_q_action_idx is not None:
                death_reward = -25.0 
                
                current_world_data_on_death = self.world.world_data 
                if not current_world_data_on_death: return 

                current_q_state_at_death = None
                if self.char_type in ["Enemy_1", "Enemy_2", "Enemy_3", "Boss Game"]:
                     current_q_state_at_death = get_q_learning_state_ground(self, self.player, current_world_data_on_death)
                elif self.char_type == "FlyingDemon":
                     current_q_state_at_death = get_q_learning_state_flying(self, self.player, current_world_data_on_death)

                if current_q_state_at_death : 
                    self.q_agent.update_q_value(self.last_q_state, self.last_q_action_idx, death_reward, current_q_state_at_death) 
                    self.q_agent.decay_exploration_rate()
                    self.q_learning_episode_count += 1
                    if self.q_learning_episode_count > 0 and self.q_learning_episode_count % 10 == 0: 
                        self.q_agent.save_q_table()

                self.last_q_state = None 
                self.last_q_action_idx = None

class Boss(Enemy):
    def __init__(self, screen, world, player, x, y, scale, speed, attack):
        super().__init__(screen, world, player, "Boss Game", x, y, scale, speed, attack)
        self.health = 300
        self.max_health = self.health
        self.scale = scale
        self.phase = 1
        self.current_attack_rect = None

    def update_phase(self):
        if self.phase == 1 and self.health <= self.max_health * 0.2:
            self.phase = 2
            self.attack *= 1.5
            self.speed += 1
            self.health = self.max_health
            
            vision_width_phase2 = self.rect.width * 25
            vision_height_phase2 = self.rect.height
            self.vision = pygame.Rect(0, 0, vision_width_phase2, vision_height_phase2)

            self.vision.center = self.rect.center

            self.angry()

        elif self.action == 5 and self.img_index == len(self.animation_list[5]) - 1:
            self.spawn_minions()
            self.update_action(0)

    def angry(self):
        animation_types = ["Angry_Idle", "Angry_Run", "Dead", "Angry_Attack_1", "Angry_Attack_2", "Angry"]

        animation_list = []
        for anim in animation_types:
            images = []
            num_imgs = len(os.listdir(f'assets/Character/Boss Game/{anim}'))
            for i in range(num_imgs):
                img = pygame.image.load(f'assets/Character/Boss Game/{anim}/{i + 1}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                images.append(img)
            animation_list.append(images)

        self.animation_list = animation_list
        self.img_index = 0
        self.image = self.animation_list[self.action][self.img_index]

        self.update_action(5)

    def spawn_minions(self):
        for i in range(3):
            enemy = Enemy(self.screen, self.world, self.player, f"Enemy_{i+1}", self.rect.x + random.randint(-300, 300), self.rect.y, self.scale / 4, 1, 2)
            enemy_group.add(enemy)

    def ai(self):
        self.update_phase()
        if self.action == 5:
            return
        if not (self.alive and self.player.alive):
            return
        super().ai()
        if self.attacking:
            self.current_attack_rect = self._create_directional_attack_hitbox()
            if self.current_attack_rect.colliderect(self.player.rect):
                player_in_front = False
                if self.direction == 1 and self.rect.centerx <= self.player.rect.centerx:
                    player_in_front = True
                elif self.direction == -1 and self.rect.centerx >= self.player.rect.centerx:
                    player_in_front = True

                if player_in_front:
                    if self.action == 3 and self.img_index in [3, 9, 15]: 
                        self.player.take_damage(self.attack)
                    elif self.action == 4 and self.img_index in [5, 8]: 
                        self.player.take_damage(self.attack*1.2)