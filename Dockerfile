# Sử dụng ảnh nền Python chính thức
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
    # Thư viện cần thiết cho Chrome/Chromium
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
    && rm -rf /var/lib/apt/lists/*

# Tải và cài đặt Google Chrome (phiên bản ổn định)
# Sử dụng URL GPG key đúng
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Dọn dẹp sau khi cài đặt
    && rm -rf /var/lib/apt/lists/*

# Tải và cài đặt ChromeDriver
# Tìm phiên bản ChromeDriver tương thích với Chrome 137.0.7151.119
# Bạn cần truy cập: https://googlechromelabs.github.io/chrome-for-testing/
# và tìm phiên bản MỚI NHẤT của ChromeDriver cho Chrome version 137.*
# Ví dụ: nếu bạn thấy "137.0.7151.119", hãy sử dụng số này.
# Hoặc, bạn có thể thử một regex linh hoạt hơn hoặc đơn giản là để nó tự động
# nếu bạn đã cài đặt google-chrome-stable
# Hoặc tốt nhất là dùng một biến môi trường để truyền vào khi build Docker
ARG CHROMEDRIVER_VERSION="137.0.7151.119" # CẬP NHẬT VÀ KIỂM TRA PHIÊN BẢN NÀY THƯỜNG XUYÊN!

RUN wget -q --continue -P /tmp/ https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && rm -r /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64

# Sao chép file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của bot vào thư mục làm việc
COPY . .

# Lệnh để chạy bot khi container khởi động
CMD ["python", "rblx_bot.py"]
