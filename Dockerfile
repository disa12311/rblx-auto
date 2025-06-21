# Sử dụng ảnh nền Python 3.10-slim
FROM python:3.10-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Gộp tất cả các lệnh cài đặt hệ thống vào một layer để tối ưu kích thước
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Các công cụ cần thiết, thêm 'jq' để xử lý JSON
    curl \
    unzip \
    wget \
    gnupg \
    jq \
    # Thư viện này cần thiết để tải GPG key theo cách mới
    dirmngr \
    # Các thư viện hệ thống cần thiết cho Chrome (đã bổ sung từ trước)
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
    fontconfig-config \
    fonts-liberation \
    libappindicator1 \
    libasound2 \
    libdbus-glib-1-2 \
    libindicator7 \
    xdg-utils \
    # Dọn dẹp cache của apt
    && rm -rf /var/lib/apt/lists/* \
    \
    # Thêm kho lưu trữ của Google Chrome bằng cách mới và an toàn hơn
    # (Đã thay thế apt-key add bằng cách tải key trực tiếp vào thư mục keyrings)
    && mkdir -p /etc/apt/keyrings \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /etc/apt/keyrings/google-chrome.gpg > /dev/null \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    \
    # Cập nhật lại apt và cài đặt Google Chrome Stable
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Dọn dẹp cache của apt lần cuối
    && rm -rf /var/lib/apt/lists/*

# === (SỬA LỖI) TẢI CHROMEDRIVER BẰNG PHƯƠNG PHÁP MỚI, ỔN ĐỊNH HƠN ===
RUN \
    CHROME_VERSION=$(google-chrome --product-version) && \
    CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d . -f 1-3) && \
    CHROMEDRIVER_URL=$(wget -q -O - "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | jq -r --arg ver "$CHROME_MAJOR_VERSION" '.versions[] | select(.version | startswith($ver)) | .downloads.chromedriver[] | select(.platform=="linux64") | .url' | head -n 1) && \
    \
    # Kiểm tra nếu CHROMEDRIVER_URL rỗng
    [ -z "$CHROMEDRIVER_URL" ] && echo "ERROR: Could not find ChromeDriver URL for Chrome version $CHROME_MAJOR_VERSION" && exit 1 || true && \
    \
    wget -q --continue -P /tmp/ "${CHROMEDRIVER_URL}" && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64

# Sao chép và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của bot vào
COPY . .

# Lệnh để chạy bot
CMD ["python", "rblx_bot.py"]
