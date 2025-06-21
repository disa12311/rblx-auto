# Sử dụng ảnh nền Python 3.10-slim, một lựa chọn tốt cho production
FROM python:3.10-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Gộp tất cả các lệnh cài đặt hệ thống vào một layer để tối ưu kích thước
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Các công cụ cần thiết
    curl \
    unzip \
    wget \
    gnupg \
    # Các thư viện hệ thống bạn đã thêm vào, rất tốt!
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
    # Thêm kho lưu trữ của Google và cài đặt Chrome
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Dọn dẹp cache của apt để giữ image nhỏ gọn
    && rm -rf /var/lib/apt/lists/*

# === PHẦN TỰ ĐỘNG HÓA TẢI CHROMEDRIVER ===
# Tự động tìm URL của phiên bản ChromeDriver ổn định mới nhất cho Linux
RUN LATEST_CHROMEDRIVER_URL=$(wget -q -O - "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | grep -oP '"linux64":\[{"platform":"linux64","url":"\K[^"]+') \
    # Tải về ChromeDriver từ URL đã tìm thấy
    && wget -q --continue -P /tmp/ "${LATEST_CHROMEDRIVER_URL}" \
    # Giải nén và di chuyển vào thư mục PATH
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    # Dọn dẹp các file không cần thiết
    && rm -rf /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64

# Sao chép và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của bot vào
COPY . .

# Lệnh để chạy bot
CMD ["python", "rblx_bot.py"]
