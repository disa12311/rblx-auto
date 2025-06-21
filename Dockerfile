# Sử dụng ảnh nền Python chính thức và nhẹ nhàng
FROM python:3.10-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Cài đặt các gói hệ thống cần thiết cho Chrome và các công cụ khác
# Gộp các lệnh để tối ưu layer và cài đặt các thư viện cần cho Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    wget \
    gnupg \
    # Thư viện cần thiết cho Chrome/Chromium để chạy headless
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libgconf-2-4 \
    libxss1 \
    libxi6 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libgbm-dev \
    # Dọn dẹp để giữ kích thước image nhỏ
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Tải và cài đặt Google Chrome (phiên bản ổn định)
# Sử dụng URL GPG key đúng và thêm repo của Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Dọn dẹp sau khi cài đặt
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Sao chép file requirements.txt và cài đặt các thư viện Python
# Đặt bước này trước COPY . . để tận dụng Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của bot vào thư mục làm việc
COPY . .

# Lệnh để chạy bot khi container khởi động
# Đảm bảo rblx_bot.py có thể thực thi (nếu cần)
CMD ["python", "rblx_bot.py"]
