from PIL import Image
import os

# Mở file GIF
gif_path = "Enemy_3.gif"
img = Image.open(gif_path)

# Tạo thư mục để lưu ảnh nếu chưa có
output_folder = "Enemy_3"
os.makedirs(output_folder, exist_ok=True)

# Lặp qua tất cả các khung hình
frame = 0
while True:
    frame_path = os.path.join(output_folder, f"frame_{frame}.png") 
    img.save(frame_path, format="PNG")  # Lưu từng khung hình dưới dạng PNG
    frame += 1
    try:
        img.seek(frame)  # Chuyển sang khung hình tiếp theo
    except EOFError:
        break  # Kết thúc khi không còn khung hình nào

print(f"Da trich xuat {frame} khung hinh vao thu muc '{output_folder}'.")

