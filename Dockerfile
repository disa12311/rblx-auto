# Dockerfile tối ưu cho Bot Discord Selenium trên Railway
# Sử dụng ảnh nền Python 3.10-slim, nhẹ và hiệu quả cho production.
FROM python:3.10-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Thiết lập biến môi trường để vô hiệu hóa các câu hỏi tương tác khi cài đặt gói
ENV DEBIAN_FRONTEND=noninteractive

# Gộp các lệnh cài đặt hệ thống vào một layer duy nhất để tối ưu kích thước image
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Các công cụ cần thiết
    curl \
    unzip \
    wget \
    gnupg \
    jq \
    # Các thư viện hệ thống quan trọng cho Chrome headless
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
    # Dọn dẹp cache của apt ngay trong cùng một layer để giảm kích thước
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Google Chrome và ChromeDriver một cách tự động và bền vững
RUN \
    # Cài đặt Google Chrome Stable
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    # Tự động tìm và cài đặt phiên bản ChromeDriver tương thích
    && CHROME_VERSION=$(google-chrome --product-version) \
    && CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d . -f 1-3) \
    && CHROMEDRIVER_URL=$(wget -q -O - "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | jq -r --arg ver "$CHROME_MAJOR_VERSION" '.versions[] | select(.version | startswith($ver)) | .downloads.chromedriver[] | select(.platform=="linux64") | .url' | head -n 1) \
    && wget -q --continue -P /tmp/ "${CHROMEDRIVER_URL}" \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64

# Sao chép và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của bot vào thư mục làm việc
COPY . .

# Lệnh để chạy bot khi container khởi động
CMD ["python", "rblx_bot.py"]
