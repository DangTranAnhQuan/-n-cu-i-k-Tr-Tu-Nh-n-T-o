import pygame
import setting
from world import World, update_world_data, item_group, speed_box_img, attack_box_img, bonus_box_img, draw_status, load_world, load_tile_images
from magic import magic_group, Magic
from entities.enemy import enemy_group
from environment import decoration_group, water_group, exit_group

pygame.init()

screen = pygame.display.set_mode((setting.screen_width, setting.screen_height))
pygame.display.set_caption('Game')
clock = pygame.time.Clock()

GameOver_img = pygame.image.load('assets/GUI/GameOver.png').convert_alpha()
Win_img = pygame.image.load('assets/GUI/You_Win/youwin.png').convert_alpha()

MAX_MAPS = 3

def run_game_level():
    global moving_left, moving_right 

    load_tile_images()
    
    enemy_group.empty()
    magic_group.empty()
    item_group.empty()
    decoration_group.empty()
    exit_group.empty()

    world_data = []
    world_data = load_world(world_data)

    players = ["Player"]
    world = World(screen, players, enemy_group, magic_group, Magic)
    status_list = {"Speed": speed_box_img, "Attack": attack_box_img, "Skill": bonus_box_img}
    player, health_bar = world.process_data(world_data)

    camera_offset = [0.0, 0.0]
    SMOOTHING_FACTOR = 20

    setting.attack_1 = False
    setting.attack_2 = False
    setting.skill = False
    setting.recover = False
    setting.dash = False
    setting.parry = False
    setting.last_skill_time = 0
    setting.last_recover_time = 0
    setting.last_dash_time = 0
    setting.last_parry_time = 0
    
    level_running = True
    while level_running:
        clock.tick(setting.FPS)

        target_camera_x = player.rect.centerx - setting.screen_width / 2
        target_camera_y = player.rect.centery - setting.screen_height / 2
        camera_offset[0] += (target_camera_x - camera_offset[0]) / SMOOTHING_FACTOR
        camera_offset[1] += (target_camera_y - camera_offset[1]) / SMOOTHING_FACTOR
        max_camera_x = len(world_data[0]) * setting.TILE_SIZE - setting.screen_width if world_data and world_data[0] else 0
        max_camera_y = len(world_data) * setting.TILE_SIZE - setting.screen_height if world_data else 0
        render_offset_x = int(max(0, min(camera_offset[0], max_camera_x)))
        render_offset_y = int(max(0, min(camera_offset[1], max_camera_y)))
        render_offset = (render_offset_x, render_offset_y)

        bg_scroll = render_offset_x
        world.draw_background(bg_scroll)
        world.draw_tiles(offset=render_offset)

        for deco in decoration_group: deco.draw(screen, offset=render_offset)
        for water in water_group: water.draw(screen, offset=render_offset)
        for exit_tile in exit_group: exit_tile.draw(screen, offset=render_offset)
        for item in item_group: item.draw(screen, offset=render_offset)
        for magic_instance in magic_group: magic_instance.draw(screen, offset=render_offset)
        
        world_data = update_world_data(world_data , enemy_group, player)
        
        player.update() 

        if player.rect.top > len(world_data) * setting.TILE_SIZE + 100:
             player.health = 0
             player.check_alive()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "quit_to_menu"
                if event.key == pygame.K_F1:
                    setting.show_enemy_algorithm_stats = not setting.show_enemy_algorithm_stats
                if event.key == pygame.K_F2:
                    setting.show_enemy_calculated_path = not setting.show_enemy_calculated_path
                    if setting.show_enemy_calculated_path:
                        for enemy_obj in enemy_group:
                            enemy_obj.search_path = []
                            enemy_obj.next_state = None
                            enemy_obj.full_path_tile_coords_for_drawing = []
                if event.key == pygame.K_F3:
                    setting.show_enemy_vision_rect = not setting.show_enemy_vision_rect
                if player.alive:
                    if event.key == pygame.K_a: setting.moving_left = True
                    if event.key == pygame.K_d: setting.moving_right = True
                    if event.key == pygame.K_SPACE and not player.in_air: player.jump = True
                    if event.key == pygame.K_r:
                        if pygame.time.get_ticks() - setting.last_skill_time >= setting.skill_cooldown:
                            setting.skill = True; setting.last_skill_time = pygame.time.get_ticks()
                    if event.key == pygame.K_q:
                        if pygame.time.get_ticks() - setting.last_recover_time >= setting.recover_cooldown :
                            setting.recover = True; setting.last_recover_time = pygame.time.get_ticks()
                    if event.key == pygame.K_LSHIFT:
                        if pygame.time.get_ticks() - setting.last_dash_time >= setting.dash_cooldown :
                            setting.dash = True; setting.last_dash_time = pygame.time.get_ticks()
                    if event.key == pygame.K_e:
                        if pygame.time.get_ticks() - setting.last_parry_time >= setting.parry_cooldown :
                            setting.parry = True; setting.last_parry_time = pygame.time.get_ticks()

                    if event.key == pygame.K_F4:
                        setting.current_global_search_algorithm_index = (setting.current_global_search_algorithm_index + 1) % len(setting.AVAILABLE_SEARCH_ALGORITHMS_DISPLAY_NAMES)
                        new_algo_name = setting.AVAILABLE_SEARCH_ALGORITHMS_DISPLAY_NAMES[setting.current_global_search_algorithm_index]
                        for enemy_obj in enemy_group:
                            enemy_obj.search_path = [] 
                            enemy_obj.next_state = None  
                            enemy_obj.full_path_tile_coords_for_drawing = []
                            enemy_obj.reset_pathfinding_info(f"Algo: {new_algo_name}")
                    
            if player.alive:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a: setting.moving_left = False
                    if event.key == pygame.K_d: setting.moving_right = False
                    if event.key == pygame.K_e:
                        if player.parry and player.action == 9:
                            setting.parry = False; player.parry = False
            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not player.attacking and not player.recovering and not player.dashing and not player.parry:
                        if event.button == 1: setting.attack_1 = True
                        elif event.button == 3: setting.attack_2 = True
        
        if player.alive:
            player_can_control_x_movement = True
            input_moving_left = setting.moving_left
            input_moving_right = setting.moving_right

            if player.attacking:
                player.player_attack()
                player_can_control_x_movement = False 
            elif player.recovering:
                player.player_recover()
                player_can_control_x_movement = False
            elif player.dashing:
                player.player_dash()
                player_can_control_x_movement = False
            elif player.parry:
                player.player_parry()
                player_can_control_x_movement = False
            else:
                action_initiated_this_frame = False
                action_initiated_this_frame = False
                if setting.attack_1:
                    if not player.attacking: 
                        player.attacking = True
                        player.update_action(3) 
                        player_can_control_x_movement = False
                        action_initiated_this_frame = True
                elif setting.attack_2:
                    if not player.attacking:
                        player.attacking = True
                        player.update_action(4)
                        player_can_control_x_movement = False
                        action_initiated_this_frame = True
                elif setting.skill:
                    if not player.attacking: 
                        player.attacking = True
                        player.update_action(5)
                        player_can_control_x_movement = False
                        action_initiated_this_frame = True
                elif setting.recover:
                    if not player.recovering:
                        player.recovering = True
                        player.update_action(7)
                        player_can_control_x_movement = False
                        action_initiated_this_frame = True
                elif setting.dash:
                     if not player.dashing:
                        player.dashing = True
                        player.update_action(8)
                        player_can_control_x_movement = False 
                        action_initiated_this_frame = True
                elif setting.parry:
                    if not player.parry:
                        player.parry = True
                        player.update_action(9)
                        player_can_control_x_movement = False
                        action_initiated_this_frame = True
                
                if not action_initiated_this_frame:
                    if player.in_air:
                        player.update_action(6)
                    elif input_moving_left or input_moving_right:
                        player.update_action(1)
                    else:
                        player.update_action(0)
            
            if not player.dashing:
                final_player_dx_left = input_moving_left if player_can_control_x_movement else False
                final_player_dx_right = input_moving_right if player_can_control_x_movement else False
                player.move(final_player_dx_left, final_player_dx_right)
        else:
            player.update_action(2)

        player.draw(offset=render_offset)
        draw_status(screen, status_list, health_bar, player.health, player.max_health, player.attack, player.speed, offset=render_offset)

        for monster in enemy_group:
            monster.update()
            monster.draw(offset=render_offset)
            monster.ai()
            if not monster.alive:
                if monster.action == 2 and monster.img_index == len(monster.animation_list[2]) - 1:
                    monster.kill()

        magic_group.update()
        item_group.update()
        decoration_group.update()
        exit_group.update()

        if not player.alive:
            if player.action == 2 and player.img_index >= len(player.animation_list[2]) -1 :
                return "game_over"

        if player.alive and exit_group and pygame.sprite.spritecollide(player, exit_group, False):
            return "next_level"

        pygame.display.update()
    
    return "quit_to_menu"


def main_game_manager():
    game_session_running = True

    while game_session_running:
        level_status = run_game_level() 

        if level_status == "next_level":
            setting.MAP += 1 

            if setting.MAP > MAX_MAPS:
                screen.blit(Win_img, ((setting.screen_width - Win_img.get_width()) // 2,
                                         (setting.screen_height - Win_img.get_height()) // 2))
                pygame.display.update()
                pygame.time.wait(3000) 
                game_session_running = False 
            else:
                pygame.time.wait(200) 

        elif level_status == "game_over":
            screen.blit(GameOver_img, ((setting.screen_width - GameOver_img.get_width()) // 2,
                                     (setting.screen_height - GameOver_img.get_height()) // 2))
            pygame.display.update()
            pygame.time.wait(3000)
            game_session_running = False 

        elif level_status == "quit_to_menu":
            game_session_running = False 

if __name__ == '__main__':
    main_game_manager()
    pygame.quit()