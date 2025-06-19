# Sử dụng một ảnh nền Python chính thức
FROM python:3.10-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Cài đặt các gói hệ thống cần thiết cho Chrome và các công cụ khác
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    gnupg \
    # Dọn dẹp để giữ kích thước image nhỏ
    && rm -rf /var/lib/apt/lists/*

# Tải và cài đặt Google Chrome (phiên bản ổn định)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Tải và cài đặt ChromeDriver
# Tìm phiên bản ChromeDriver mới nhất cho Linux
RUN LATEST_CHROMEDRIVER_VERSION=$(wget -q -O - "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | grep -oP '"linux64":\[{"platform":"linux64","url":"\K[^"]+') \
    && wget -q --continue -P /tmp/ https://storage.googleapis.com/chrome-for-testing-public/${LATEST_CHROMEDRIVER_VERSION} \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver-linux64.zip

# Sao chép file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của bot vào thư mục làm việc
COPY . .

# Lệnh để chạy bot khi container khởi động
CMD ["python", "rblx_bot.py"]
