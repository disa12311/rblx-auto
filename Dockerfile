# Sử dụng ảnh nền Python 3.10-slim
FROM python:3.10-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Bước 1: Cập nhật apt và cài đặt các công cụ cơ bản + gói phụ thuộc cần cho Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    wget \
    gnupg \
    jq \
    dirmngr \
    # Các thư viện hệ thống cần thiết cho Chrome
    # Đã tinh gọn lại danh sách này, tập trung vào những cái thiết yếu nhất
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgdk-pixbuf2.0-0 \
    libgbm-dev \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    # Các gói font và tiện ích khác mà Chrome có thể cần
    fonts-liberation \
    xdg-utils \
    # Dọn dẹp cache của apt ngay sau khi cài đặt gói đầu tiên
    && rm -rf /var/lib/apt/lists/*

# Bước 2: Thêm kho lưu trữ của Google Chrome và cài đặt Chrome
# Tách ra một lệnh RUN riêng để dễ gỡ lỗi hơn
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Tải GPG key và thêm repo theo cách hiện đại
    # Đảm bảo mkdir -p được gọi trước khi wget
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    && mkdir -p /etc/apt/keyrings \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /etc/apt/keyrings/google-chrome.gpg > /dev/null \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    \
    # Cập nhật apt và cài đặt Google Chrome Stable
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Dọn dẹp cache của apt lần cuối
    && rm -rf /var/lib/apt/lists/*

# Bước 3: Tải và cài đặt ChromeDriver
# Giữ nguyên logic thông minh của bạn để khớp phiên bản
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
