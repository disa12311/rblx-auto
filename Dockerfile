# Sử dụng ảnh nền selenium/standalone-chrome đã được cấu hình sẵn Chrome và ChromeDriver
FROM selenium/standalone-chrome:latest

# Đặt người dùng là root để đảm bảo quyền apt-get cho các gói phụ trợ
USER root

# Cập nhật apt và cài đặt CHỈ các công cụ dòng lệnh phụ trợ (build-essential, curl, unzip, wget, jq)
# KHÔNG CÀI LẠI PYTHON VÀ PIP, VÌ ẢNH NỀN ĐÃ CÓ SẴN!
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    wget \
    jq \
    build-essential \
    # Các gói phụ thuộc chung khác nếu cần, nhưng ít khi gây lỗi
    # ca-certificates \
    # software-properties-common \
    # Dọn dẹp cache của apt
    && rm -rf /var/lib/apt/lists/*

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
