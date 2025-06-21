# Sử dụng ảnh nền selenium/standalone-chrome đã được cấu hình sẵn Chrome và ChromeDriver
FROM selenium/standalone-chrome:latest

# Đặt người dùng là root để đảm bảo quyền apt-get cho các gói phụ trợ
USER root

# Cập nhật apt và cài đặt CHỈ các công cụ dòng lệnh phụ trợ
# KHÔNG CÀI LẠI PYTHON VÀ PIP, VÌ ẢNH NỀN ĐÃ CÓ SẴN!
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    wget \
    jq \
    # Dọn dẹp cache của apt
    && rm -rf /var/lib/apt/lists/*

# (Bỏ qua bước update-alternatives cho Python và Pip)
# Vì chúng ta không cài đặt lại Python, chúng ta không cần cấu hình lại alias.
# Python mặc định của ảnh nền sẽ được sử dụng.

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của bot vào
COPY . .

# Lệnh để chạy bot
# ChromeDriver và Chrome đã được cài đặt và nằm trong PATH từ ảnh nền
CMD ["python", "rblx_bot.py"]
