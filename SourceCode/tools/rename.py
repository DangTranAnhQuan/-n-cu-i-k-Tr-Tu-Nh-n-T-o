import os

# Đường dẫn đến thư mục chứa ảnh
# folder_path = "Character/Enemy/Orc/Idle"
folder_path = "Enemy_1/Dead"

# Lấy danh sách tất cả các tệp trong thư mục và sắp xếp chúng
files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
log_file_path = "log.txt"

# Đổi tên từng tệp theo thứ tự 1.png, 2.png, ...
with open(log_file_path, "w", encoding="utf-8") as log_file:
    for i, filename in enumerate(files, start=1):
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, f"{i}.png")
        
        # Đổi tên file
        os.rename(old_path, new_path)
        print(f"Đã đổi: {filename} -> {i}.png")
        log_message = f"Đã đổi: {filename} -> {i}.png"
        print(log_message)  # Hiển thị trên terminal
        log_file.write(log_message + "\n")  # Ghi vào file log.txt

print("Hoàn tất đổi tên!")
# from PIL import Image
# import os

# input_folder = "Character/FlyingDemon/Magic"  # Đường dẫn tới folder chứa ảnh
# output_folder = "Character/FlyingDemon/Magic1"  # Nơi lưu ảnh sau khi flip

# os.makedirs(output_folder, exist_ok=True)

# for filename in os.listdir(input_folder):
#     if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
#         img_path = os.path.join(input_folder, filename)
#         img = Image.open(img_path)

#         flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)  # Flip ngang (horizontal)
#         # flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)  # Flip dọc (vertical)

#         flipped_img.save(os.path.join(output_folder, filename))
