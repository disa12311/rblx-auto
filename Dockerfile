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
# Cách an toàn hơn: dùng một phiên bản ChromeDriver cố định hoặc đảm bảo lệnh grep hoạt động đúng
# Cách 1: Tải ChromeDriver bằng phiên bản cụ thể (khuyến nghị cho sự ổn định)
# Bạn nên kiểm tra phiên bản ChromeDriver tương thích với Google Chrome Stable đã cài ở trên.
# Ví dụ: nếu google-chrome-stable là 126.x.x.x, bạn có thể tìm ChromeDriver 126.x.x.x
# Truy cập https://googlechromelabs.github.io/chrome-for-testing/ để tìm phiên bản mới nhất
ARG CHROMEDRIVER_VERSION="126.0.6478.126" # Cập nhật số phiên bản này thường xuyên!
RUN wget -q --continue -P /tmp/ https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && rm -r /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64

# Hoặc Cách 2: Giữ lệnh tải tự động, nhưng điều chỉnh đường dẫn sau khi giải nén
# RUN LATEST_CHROMEDRIVER_VERSION=$(wget -q -O - "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | grep -oP '"linux64":\[{"platform":"linux64","url":"\K[^"]+') \
#     && wget -q --continue -P /tmp/ https://storage.googleapis.com/chrome-for-testing-public/${LATEST_CHROMEDRIVER_VERSION} \
#     && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
#     && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/ \
#     && rm -r /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64

# Sao chép file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của bot vào thư mục làm việc
COPY . .

# Lệnh để chạy bot khi container khởi động
CMD ["python", "rblx_bot.py"]
