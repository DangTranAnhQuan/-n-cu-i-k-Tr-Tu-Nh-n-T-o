import pygame
import button
import os
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import subprocess

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")

selected_map_id = None

game_paused = False
menu_state = "main"
sound_enabled = True  

font = pygame.font.SysFont("arialblack", 40)
font_button = pygame.font.SysFont("arialblack", 20)
TEXT_COL = (255, 255, 255)


settings_label = pygame.image.load('assets/GUI/Header_settings.png').convert_alpha()
sound_label = pygame.image.load('assets/GUI/Sound.png').convert_alpha()
music_label = pygame.image.load('assets/GUI/Music.png').convert_alpha()


img_bg = pygame.image.load('assets/GUI/Header_main.png')


pause_img = pygame.image.load("assets/GUI/Pause_BTN.png").convert_alpha()
settings_off_img = pygame.image.load("assets/GUI/Settings_BTN.png").convert_alpha()
settings_on_img = pygame.image.load("assets/GUI/Buttons/BTNs_Active/Settings_BTN.png").convert_alpha()

exit_img = pygame.image.load("assets/GUI/Exit_BTN.png").convert_alpha()

music_on_img = pygame.image.load('assets/GUI/Buttons/BTNs_Active/Music_BTN.png').convert_alpha()
music_off_img = pygame.image.load('assets/GUI/Music_BTN.png').convert_alpha()
    
sound_on_img = pygame.image.load('assets/GUI/Buttons/BTNs_Active/Sound_BTN.png').convert_alpha()
sound_off_img = pygame.image.load('assets/GUI/Sound_BTN.png').convert_alpha()

backward_img = pygame.image.load('assets/GUI/Backward_BTN.png').convert_alpha()
menu_off_img = pygame.image.load('assets/GUI/Menu_BTN.png').convert_alpha()
menu_on_img = pygame.image.load("assets/GUI/Buttons/BTNs_Active/Menu_BTN.png").convert_alpha()

play_off_img = pygame.image.load('assets/GUI/Play_BTN.png').convert_alpha()
play_on_img = pygame.image.load('assets/GUI/Buttons/BTNs_Active/Play_BTN.png').convert_alpha()


pause_button = button.Button(430, 250, pause_img, 0.55)
settings_button = button.Button(125, 250, settings_off_img, 0.55)
exit_button = button.Button(240, 410, exit_img, 0.55)
music_button = button.Button(400, 180, music_on_img, 0.55)
sound_button = button.Button(150, 180, sound_on_img, 0.55)
backward_button = button.Button(50, 370, backward_img, 0.55)
menu_button = button.Button(300, 270, menu_off_img, 0.55)
play_button = button.Button(300, 130, play_off_img, 0.55)

main_menu_buttons = [menu_button, exit_button, play_button]
pause_menu_buttons = [pause_button, settings_button]
options_menu_buttons = [music_button, sound_button, backward_button]

settings_delay_active = False
settings_delay_start_time = 0
SETTINGS_DELAY_DURATION = 200 

menu_delay_active = False
menu_delay_start_time = 0
MENU_DELAY_DURATION = 200


pygame.mixer.music.load('sfx/music.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

def delay_active(condition, duration):
    is_delaying = False
    start_time = 0

    if condition:
        is_delaying = True
        start_time = pygame.time.get_ticks()

    return is_delaying, start_time

def check_delay_over(is_delaying, start_time, duration):
    if is_delaying and pygame.time.get_ticks() - start_time >= duration:
        return True
    return False

def clear_buttons():
    global main_menu_buttons, pause_menu_buttons, options_menu_buttons, map_menu_buttons
    main_menu_buttons = []
    pause_menu_buttons = []
    options_menu_buttons = []
    map_menu_buttons = []

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg(img_bg):
    screen.fill((0, 0, 0))
    img_bg = pygame.transform.scale(img_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(img_bg, (0, 0))

def draw_img(surface, image, x, y, scale = 1):
    width = int(image.get_width() * scale)
    height = int(image.get_height() * scale)
    scaled_image = pygame.transform.scale(image, (width, height))
    surface.blit(scaled_image, (x, y))

def toggle_system_audio(enabled):
    if os.name == 'nt':
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() == "python3.12.exe":
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                if enabled:
                    volume.SetMasterVolume(1.0, None)
                else:
                    volume.SetMasterVolume(0.0, None)

run = True
while run:

    draw_bg(img_bg)

    if menu_state == "main" and not game_paused:
        for btn in main_menu_buttons:
            if btn.draw(screen):
                if btn == menu_button:
                    menu_button.update_image(menu_on_img)
                    menu_delay_active, menu_delay_start_time = delay_active(True, MENU_DELAY_DURATION)
                elif btn == exit_button:
                    run = False
                elif btn == play_button:
                    play_button.update_image(play_on_img)
                    subprocess.Popen(['python', 'src/main.py'])
                    
  
    if menu_delay_active:
        if check_delay_over(menu_delay_active, menu_delay_start_time, MENU_DELAY_DURATION):
            menu_delay_active = False
            game_paused = True 
            menu_button.update_image(menu_off_img) 

    elif game_paused == True:
        draw_img(screen, settings_label, (SCREEN_WIDTH - settings_label.get_width()) // 2, 30)
        if menu_state == "main":
            for btn in pause_menu_buttons:
                if btn.draw(screen):
                    if btn == pause_button:
                        game_paused = False
                        settings_button.update_image(settings_off_img)
                        menu_button.update_image(menu_off_img) 
                    elif btn == settings_button:
                        settings_button.update_image(settings_on_img)
                        settings_delay_active, settings_delay_start_time = delay_active(True, SETTINGS_DELAY_DURATION)
                    elif btn == exit_button:
                        run = False
    

        elif menu_state == "options":
            draw_img(screen, sound_label, 135, 130, 0.65)
            draw_img(screen, music_label, 390, 130, 0.65)
            for btn in options_menu_buttons:
                if btn.draw(screen):
                    if btn == music_button:
                        if pygame.mixer.music.get_volume() > 0:
                            pygame.mixer.music.set_volume(0)
                            music_button.update_image(music_off_img)
                        else:
                            pygame.mixer.music.set_volume(0.5)
                            music_button.update_image(music_on_img)
                    elif btn == sound_button:
                        sound_enabled = not sound_enabled
                        if sound_enabled:
                            sound_button.update_image(sound_on_img)
                            toggle_system_audio(True)
                        else:
                            sound_button.update_image(sound_off_img)
                            toggle_system_audio(False)
                    elif btn == backward_button:
                        menu_state = "main"
                        backward_button_clicked = False
                        settings_button.update_image(settings_off_img) 
                        menu_button.update_image(menu_off_img) 

    
    if settings_delay_active:
        if check_delay_over(settings_delay_active, settings_delay_start_time, SETTINGS_DELAY_DURATION):
            settings_delay_active = False
            menu_state = "options"
            backward_button_clicked = False
            settings_button.update_image(settings_off_img) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()