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
    # Các thư viện hệ thống cần thiết cho Chrome
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
    # Dọn dẹp cache của apt
    && rm -rf /var/lib/apt/lists/*

# === (SỬA LỖI) TẢI CHROMEDRIVER BẰNG PHƯƠNG PHÁP MỚI, ỔN ĐỊNH HƠN ===
RUN \
    # Lấy phiên bản của Google Chrome đã cài đặt (ví dụ: 126.0.6478.126)
    CHROME_VERSION=$(google-chrome --product-version) && \
    # Cắt lấy phần chính của phiên bản (ví dụ: 126.0.6478) để tìm ChromeDriver tương ứng
    CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d . -f 1-3) && \
    # Tìm URL của ChromeDriver gần nhất với phiên bản Chrome đã cài
    CHROMEDRIVER_URL=$(wget -q -O - "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | jq -r --arg ver "$CHROME_MAJOR_VERSION" '.versions[] | select(.version | startswith($ver)) | .downloads.chromedriver[] | select(.platform=="linux64") | .url' | head -n 1) && \
    # Tải về, giải nén và di chuyển vào PATH
    wget -q --continue -P /tmp/ "${CHROMEDRIVER_URL}" && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    # Dọn dẹp
    rm -rf /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64

# Sao chép và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của bot vào
COPY . .

# Lệnh để chạy bot
CMD ["python", "rblx_bot.py"]
