import os
from PIL import Image

def remove_background_folder(input_folder, output_folder, bg_color=None, tolerance=10):
    """Chuyển nền thành trong suốt cho tất cả ảnh trong thư mục"""
    
    # Tạo thư mục đầu ra nếu chưa có
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):  # Chỉ xử lý file PNG
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            img = Image.open(input_path).convert("RGBA")
            pixels = img.load()
            
            # Nếu không có màu nền -> Tự lấy pixel góc trên trái
            if bg_color is None:
                bg_color = pixels[0, 0][:3]

            width, height = img.size
            for x in range(width):
                for y in range(height):
                    r, g, b, a = pixels[x, y]
                    if abs(r - bg_color[0]) <= tolerance and abs(g - bg_color[1]) <= tolerance and abs(b - bg_color[2]) <= tolerance:
                        pixels[x, y] = (r, g, b, 0)  # Đặt alpha = 0

            img.save(output_path, "PNG")
            print(f"✔ Đã xử lý: {filename}")

# 🟢 Chạy thử với folder chứa các frame
remove_background_folder("Enemy_1", "test", tolerance=15)
# import os
# import requests

# # API Key của Remove.bg (thay thế bằng API Key của bạn)
# api_key = 'VzEZaWQriSY3GZTbGYPjZgTH'

# # Thư mục chứa ảnh đầu vào và đầu ra
# input_folder = "Boss1"
# output_folder = "Boss Game"
# os.makedirs(output_folder, exist_ok=True)

# # URL của API Remove.bg
# url = 'https://api.remove.bg/v1.0/removebg'

# # Xử lý tất cả ảnh trong thư mục
# for filename in os.listdir(input_folder):
#     if filename.lower().endswith((".png", ".jpg", ".jpeg")):
#         input_path = os.path.join(input_folder, filename)
#         output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + "_removed.png")

#         print(f"Đang xử lý: {filename}...")

#         # Mở ảnh và gửi lên API
#         with open(input_path, 'rb') as img_file:
#             response = requests.post(
#                 url,
#                 files={'image_file': img_file},
#                 data={'size': 'auto'},
#                 headers={'X-Api-Key': api_key}
#             )

#         # Kiểm tra nếu xóa nền thành công
#         if response.status_code == 200:
#             # Lưu ảnh đã xóa nền
#             with open(output_path, 'wb') as out_file:
#                 out_file.write(response.content)
#             print(f"✅ Đã xử lý và lưu ảnh: {filename}")
#         else:
#             print(f"❌ Lỗi khi xử lý ảnh {filename}: {response.status_code}")

# print("✅ Xử lý hoàn tất! Ảnh đã được lưu vào thư mục Boss1.")

