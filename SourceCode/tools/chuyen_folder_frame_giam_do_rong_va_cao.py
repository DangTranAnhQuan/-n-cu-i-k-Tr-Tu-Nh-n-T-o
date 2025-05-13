from PIL import Image
import os

# Thư mục chứa ảnh (Dùng raw string hoặc \\)
folder_path = r"Enemy_1"  # Thay đường dẫn phù hợp
new_width = 632  # Độ rộng mong muốn
new_height = 435-65  # Độ cao mong muốn

# Lặp qua các file trong thư mục
for filename in os.listdir(folder_path):
    if filename.endswith(".png"):
        img_path = os.path.join(folder_path, filename)
        img = Image.open(img_path)

        # Lấy kích thước gốc
        width, height = img.size

        # Kiểm tra nếu ảnh quá nhỏ
        if new_width > width or new_height > height:
            print(f"❌ Ảnh {filename} ({width}x{height}) quá nhỏ để cắt, bỏ qua...")
            continue

        # Xác định tọa độ cắt để lấy phần giữa
        
        left = (width - new_width) // 2
        right = left + new_width
        
        top = (height - new_height) // 2
        bottom = top + new_height

        # Cắt ảnh
        cropped_img = img.crop((left, top, right, bottom))

        # Lưu ảnh mới
        new_path = os.path.join(folder_path, filename)
        cropped_img.save(new_path)

print("✅ Đã cắt ảnh xong!")