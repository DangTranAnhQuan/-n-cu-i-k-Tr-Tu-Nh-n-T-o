import time
import queue
import numpy as np
from setting import * 

def get_start(enemy, current_world_list_of_lists):
    enemy_col = int(enemy.rect.centerx // TILE_SIZE)
    enemy_row = int((enemy.rect.bottom - 1) // TILE_SIZE)

    start_state_list = [list(r) for r in current_world_list_of_lists]

    temp_np_array = np.array(start_state_list)
    for r_idx, c_idx in np.argwhere(np.isin(temp_np_array, [81, 82, 83])):
        start_state_list[r_idx][c_idx] = -1

    if 0 <= enemy_row < ROWS and 0 <= enemy_col < COLS:
        if start_state_list[enemy_row][enemy_col] not in range(0, 60):
             start_state_list[enemy_row][enemy_col] = 999 

    return tuple(tuple(row) for row in start_state_list)

def get_goal(enemy_obj, start_state_tuple, player_obj):
    goal_state_list = [list(row) for row in start_state_tuple]

    current_enemy_pos_in_start = find_enemy(start_state_tuple)
    
    if current_enemy_pos_in_start is not None: 
        goal_state_list[current_enemy_pos_in_start[0]][current_enemy_pos_in_start[1]] = -1

    player_col = int(player_obj.rect.centerx // TILE_SIZE)
    player_row = int((player_obj.rect.bottom - 1) // TILE_SIZE)

    if 0 <= player_row < ROWS and 0 <= player_col < COLS:
        if goal_state_list[player_row][player_col] not in range(0, 60):
            goal_state_list[player_row][player_col] = 999

    return tuple(tuple(row) for row in goal_state_list)

def find_enemy(state_tuple):
    try:
        state_array = np.array(state_tuple, dtype=np.int32) 
        coords = np.argwhere(state_array == 999)
        if coords.size > 0:
            return coords[0]  
        return None
    except Exception as e:
        return None

def generate_new_states(enemy, current_state_tuple):
    new_states = []
    enemy_pos = find_enemy(current_state_tuple)

    if enemy_pos is None:
        return new_states 

    r, c = enemy_pos[0], enemy_pos[1]

    if enemy.char_type == "FlyingDemon":
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        possible_moves = [(0, -1), (0, 1)]

    for dr, dc in possible_moves:
        new_r, new_c = r + dr, c + dc

        if 0 <= new_r < ROWS and 0 <= new_c < COLS:
            if current_state_tuple[new_r][new_c] not in range(0, 60):
                new_state_list = [list(row_data) for row_data in current_state_tuple]
                
                new_state_list[r][c] = -1
                new_state_list[new_r][new_c] = 999
                
                new_states.append(tuple(tuple(row) for row in new_state_list))
    return new_states

def manhattan(state_tuple, goal_state_tuple):
    enemy_pos_state = find_enemy(state_tuple)
    enemy_pos_goal = find_enemy(goal_state_tuple)

    if enemy_pos_state is None or enemy_pos_goal is None:
        return float('inf')

    r1, c1 = enemy_pos_state[0], enemy_pos_state[1]
    r2, c2 = enemy_pos_goal[0], enemy_pos_goal[1]
    return abs(r1 - r2) + abs(c1 - c2)

def bfs(enemy, start_state, goal_state):
    s_time = time.perf_counter()
    nodes_count = 0
    q = queue.Queue()
    q.put((start_state, [])) 
    visited_states = {start_state} 

    while not q.empty():
        current_s, path = q.get()
        nodes_count += 1

        if current_s == goal_state:
            e_time = time.perf_counter()
            return path, {"time": e_time - s_time, "nodes": nodes_count, "length": len(path), "name": "BFS"}

        for next_s in generate_new_states(enemy, current_s):
            if next_s not in visited_states:
                visited_states.add(next_s)
                q.put((next_s, path + [next_s])) 
    
    e_time = time.perf_counter()
    return [], {"time": e_time - s_time, "nodes": nodes_count, "length": 0, "name": "BFS"}

def a_star_solve(enemy, start_state, goal_state):
    s_time = time.perf_counter()
    nodes_count = 0
    pq = queue.PriorityQueue()
    pq.put((manhattan(start_state, goal_state), 0, start_state, [])) 
    
    visited_costs = {start_state: 0}

    while not pq.empty():
        f, g, current_s, path = pq.get()
        
        if g > visited_costs.get(current_s, float('inf')): 
            continue
        
        nodes_count +=1 

        if current_s == goal_state:
            e_time = time.perf_counter()
            return path, {"time": e_time - s_time, "nodes": nodes_count, "length": len(path), "name": "A*"}

        for next_s in generate_new_states(enemy, current_s):
            new_g = g + 1
            if new_g < visited_costs.get(next_s, float('inf')):
                visited_costs[next_s] = new_g
                h = manhattan(next_s, goal_state)
                new_f = new_g + h
                pq.put((new_f, new_g, next_s, path + [next_s])) 
        
    e_time = time.perf_counter()
    return [], {"time": e_time - s_time, "nodes": nodes_count, "length": 0, "name": "A*"}

def steepest_ascent_hill_climbing(enemy, start, goal, max_iterations=1000):
    s_time = time.perf_counter()
    current_state = start
    path_accumulator = [current_state]
    iterations = 0 

    while current_state != goal and iterations < max_iterations:
        
        neighbors = generate_new_states(enemy, current_state)
        if not neighbors:
            break

        h_of_current_state = manhattan(current_state, goal)
        best_h_found_among_neighbors = float('inf')
        best_neighbor_overall = None

        for neighbor_node in neighbors:
            h_n = manhattan(neighbor_node, goal)
            if h_n < best_h_found_among_neighbors:
                best_h_found_among_neighbors = h_n
                best_neighbor_overall = neighbor_node
        
        if best_neighbor_overall is not None and best_h_found_among_neighbors < h_of_current_state:
            current_state = best_neighbor_overall
            path_accumulator.append(current_state)
        else:
            break
        
        iterations += 1

    e_time = time.perf_counter()

    actual_path_to_return = []

    if current_state == goal:
        if path_accumulator and len(path_accumulator) > 1:
            actual_path_to_return = path_accumulator[1:]
          
    metrics = {
        "time": e_time - s_time,
        "nodes": iterations, 
        "length": len(actual_path_to_return),
        "name": "Steepest HC" 
    }
    return actual_path_to_return, metrics


def and_or_search(problem, initial_state):
    return or_search(initial_state, problem, [])

def or_search(state, problem, path):
    if problem.is_goal(state):
        return [] 

    if state in path:
        return None 

    for action in problem.actions(state):
        next_states = problem.results(state, action)
        plan = and_search(next_states, problem, path + [state])
        if plan is not None:
            return [action] + plan
    return None

def and_search(states, problem, path):
    plans = []
    for s in states:
        plan_i = or_search(s, problem, path)
        if plan_i is None:
            return None
        plans.append(plan_i)

    final_plan = []
    for plan in plans:
        final_plan.extend(plan)
    return final_plan

class EnemyProblem:
    def __init__(self, initial_state, goal_state, enemy_obj):
        self.initial_state = initial_state
        self.goal_state = goal_state
        self.enemy = enemy_obj

    def is_goal(self, state):
        return state == self.goal_state

    def actions(self, state):
        return generate_new_states(self.enemy, state)

    def results(self, state, action):
        return [action]

def and_or_solve(enemy, start_state, goal_state):
    s_time = time.perf_counter()
    problem = EnemyProblem(start_state, goal_state, enemy)
    plan = and_or_search(problem, start_state)
    e_time = time.perf_counter()
    nodes_count = -1

    if plan:
        return plan, {"time": e_time - s_time, "nodes": nodes_count, "length": len(plan), "name": "And Or Search"}
    else:
        return [], {"time": e_time - s_time, "nodes": nodes_count, "length": 0, "name": "And Or Search"}

def backtracking_search(enemy, start_state, goal_state):
    s_time = time.perf_counter()
    nodes_count = [0] 
    visited_states = set()
    path_accumulator = []

    def backtrack_recursive(current_s):
        nodes_count[0] += 1
        visited_states.add(current_s)
        path_accumulator.append(current_s) 

        if current_s == goal_state:
            return True

        neighbors = generate_new_states(enemy, current_s)
        try:
            sorted_neighbors = sorted(neighbors, key=lambda s: manhattan(s, goal_state))
        except Exception as e:
            print(f"Warning: Could not sort neighbors in backtracking: {e}")
            sorted_neighbors = neighbors
            
        for next_s in sorted_neighbors:
            if next_s not in visited_states:
                if backtrack_recursive(next_s):
                    return True 
        path_accumulator.pop() 
        return False 

    found = backtrack_recursive(start_state)
    e_time = time.perf_counter()

    if found:
        final_path = []
        if path_accumulator:
            if len(path_accumulator) > 1 :
                final_path = path_accumulator[1:]
        metrics = {
            "time": e_time - s_time,
            "nodes": nodes_count[0],
            "length": len(final_path), 
            "name": "Backtracking Search"
        }
        return final_path, metrics
    else:
        metrics = {
            "time": e_time - s_time,
            "nodes": nodes_count[0],
            "length": 0,
            "name": "Backtracking Search"
        }
        return [], metrics