import pygame
import button # Đảm bảo file button.py của bạn ở cùng thư mục hoặc trong PYTHONPATH
import csv
# import pickle # Pickle không được sử dụng, có thể bỏ qua

pygame.init()

clock = pygame.time.Clock()
FPS = 60

# Game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 500 # Increased

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Editor')


# Define game variables
ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS  # Kết quả là 40
TILE_TYPES = 89 # Số loại tile bạn có (ví dụ: file ảnh từ 0.png đến 83.png)
level = 0
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1

# --- Thêm định nghĩa cho ID của tile trang trí ---
DECORATIVE_TILE_START_ID = 60
DECORATIVE_TILE_END_ID = 79 # Giả sử tile trang trí của bạn có ID từ 60 đến 79

# Load images
pine1_img = pygame.image.load('tools/LevelEditor-main/img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('tools/LevelEditor-main/img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('tools/LevelEditor-main/img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('tools/LevelEditor-main/img/Background/sky_cloud.png').convert_alpha()

# --- Sửa đổi cách tải hình ảnh ---
# `palette_img_list`: Dùng cho các nút bấm chọn tile, tất cả được scale về TILE_SIZE
# `world_img_list`: Dùng để vẽ lên map, tile trang trí sẽ giữ kích thước gốc
palette_img_list = []
world_img_list = []
map = 3

for x in range(TILE_TYPES):
    try:
        img_path = f'assets/map/Map_{map}/Tile/{x}.png' # Đảm bảo đường dẫn này chính xác
        original_img = pygame.image.load(img_path).convert_alpha()

        # Ảnh cho bảng chọn (palette) - luôn scale về TILE_SIZE
        palette_scaled_img = pygame.transform.scale(original_img, (TILE_SIZE, TILE_SIZE))
        palette_img_list.append(palette_scaled_img)

        # Ảnh để vẽ lên thế giới (world)
        if DECORATIVE_TILE_START_ID <= x <= DECORATIVE_TILE_END_ID:
            world_img_list.append(original_img)  # Giữ kích thước gốc cho tile trang trí
        else:
            world_scaled_img = pygame.transform.scale(original_img, (TILE_SIZE, TILE_SIZE))
            world_img_list.append(world_scaled_img) # Scale các tile khác

    except pygame.error as e:
        print(f"Lỗi tải ảnh img/tile/{x}.png: {e}. Sử dụng placeholder.")
        # Tạo placeholder nếu không tải được ảnh
        placeholder_palette = pygame.Surface((TILE_SIZE, TILE_SIZE))
        placeholder_palette.fill((255, 0, 255)) # Màu hồng
        palette_img_list.append(placeholder_palette)

        placeholder_world = pygame.Surface((TILE_SIZE, TILE_SIZE)) # Placeholder cho world có thể khác nếu muốn
        if DECORATIVE_TILE_START_ID <= x <= DECORATIVE_TILE_END_ID:
             # Có thể tạo placeholder nhỏ hơn hoặc khác màu cho đồ trang trí nếu ảnh gốc bị lỗi
             placeholder_world = pygame.Surface((20, 20)) # Ví dụ
             placeholder_world.fill((200, 0, 200))
        else:
            placeholder_world.fill((255,0,255))
        world_img_list.append(placeholder_world)


save_img = pygame.image.load('tools/LevelEditor-main/img/save_btn.png').convert_alpha()
load_img = pygame.image.load('tools/LevelEditor-main/img/load_btn.png').convert_alpha()


# Define colours
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

# Define font
font = pygame.font.SysFont('Futura', 30)

# Create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)

# Create ground
for tile in range(0, MAX_COLS):
    world_data[ROWS - 1][tile] = 0


# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Create function for drawing background
def draw_bg():
    screen.fill(GREEN)
    width = sky_img.get_width()
    for x in range(4): # Lặp 4 lần để có background đủ rộng cho cuộn
        screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

# Draw grid
def draw_grid():
    # Vertical lines
    for c in range(MAX_COLS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
    # Horizontal lines
    for c in range(ROWS + 1): # Vẽ ROWS + 1 đường để có đường bao cuối cùng
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))


# --- Sửa đổi hàm vẽ thế giới để căn chỉnh tile trang trí ---
def draw_world():
    for y_row, row_data in enumerate(world_data):
        for x_col, tile_id in enumerate(row_data):
            if tile_id >= 0 and tile_id < len(world_img_list) : # Kiểm tra tile_id hợp lệ
                img_to_draw = world_img_list[tile_id]
                
                # Vị trí vẽ mặc định (góc trên bên trái của ô lưới)
                blit_x = x_col * TILE_SIZE - scroll
                blit_y = y_row * TILE_SIZE

                # Nếu là tile trang trí, điều chỉnh blit_y để căn đáy tile với đáy ô lưới
                if DECORATIVE_TILE_START_ID <= tile_id <= DECORATIVE_TILE_END_ID:
                    blit_y = (y_row * TILE_SIZE) + (TILE_SIZE - img_to_draw.get_height())
                
                screen.blit(img_to_draw, (blit_x, blit_y))


# Create buttons
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)

# Make a button list for tile palette
button_list = []
button_col = 0
button_row = 0
cols_per_row = 8 
button_spacing = 55 # Khoảng cách giữa các nút, bao gồm kích thước nút và lề

# --- Sử dụng `palette_img_list` cho các nút bấm ---
for i in range(len(palette_img_list)):
    # Các nút bấm sẽ được tạo ở phần SIDE_MARGIN
    # Tọa độ x: SCREEN_WIDTH + lề nhỏ + vị trí cột * khoảng cách
    # Tọa độ y: lề nhỏ + vị trí hàng * khoảng cách
    tile_button = button.Button(SCREEN_WIDTH + 50 + (button_spacing * button_col), \
                                50 + (button_spacing * button_row), \
                                palette_img_list[i], 1)
    button_list.append(tile_button)
    button_col += 1
    if button_col == cols_per_row:
        button_row += 1
        button_col = 0


run = True
while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()
    draw_world()

    draw_text(f'Level: {level}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text('Press UP or DOWN to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

    # Save and load data
    if save_button.draw(screen):
        with open(f'{level}.csv', 'w', newline='') as csvfile: # Đổi tên file lưu cho rõ ràng
            writer = csv.writer(csvfile, delimiter = ',')
            for row in world_data:
                writer.writerow(row)
    if load_button.draw(screen):
        scroll = 0 # Reset scroll khi load map
        try:
            with open(f'data/Map_{map}/{level}.csv', newline='') as csvfile: # Đọc từ file đã đổi tên
                reader = csv.reader(csvfile, delimiter = ',')
                for x, row in enumerate(reader):
                    # Đảm bảo không đọc quá số hàng cho phép của world_data
                    if x < ROWS:
                        for y, tile in enumerate(row):
                            # Đảm bảo không đọc quá số cột cho phép
                            if y < MAX_COLS:
                                world_data[x][y] = int(tile)
        except FileNotFoundError:
            print(f"Không tìm thấy file level{level}_data.csv")
        except Exception as e:
            print(f"Lỗi khi tải map: {e}")


    # Draw tile panel (khung chứa các nút chọn tile)
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN)) # Mở rộng chiều cao panel

    # Choose a tile from palette
    button_count = 0 # Reset button_count mỗi frame
    for i, btn in enumerate(button_list): # Sử dụng enumerate để lấy cả index và button
        if btn.draw(screen): # btn.draw() sẽ vẽ nút và trả về True nếu được click
            current_tile = i # Gán ID tile là index của nút được chọn

    # Highlight the selected tile button
    if current_tile < len(button_list): # Kiểm tra current_tile hợp lệ
        pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    # Scroll the map
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
        scroll += 5 * scroll_speed

    # Add new tiles to the screen from mouse input
    pos = pygame.mouse.get_pos()
    # Chuyển đổi tọa độ chuột trên màn hình thành tọa độ ô lưới trên thế giới (có tính scroll)
    world_x = (pos[0] + scroll) // TILE_SIZE
    world_y = pos[1] // TILE_SIZE

    # Check if mouse is within the world editing area (không phải panel)
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        # Check if click is within world bounds (đã quy đổi ra world_x, world_y)
        if 0 <= world_x < MAX_COLS and 0 <= world_y < ROWS:
            if pygame.mouse.get_pressed()[0] == 1: # Left click
                if world_data[world_y][world_x] != current_tile:
                    world_data[world_y][world_x] = current_tile
            if pygame.mouse.get_pressed()[2] == 1: # Right click
                world_data[world_y][world_x] = -1 # Xóa tile (đặt là -1)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT: # Chấp nhận cả 2 Shift
                scroll_speed = 5
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                scroll_speed = 1

    pygame.display.update()

pygame.quit()