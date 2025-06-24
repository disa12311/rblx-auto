# Dockerfile Tối ưu Cuối cùng

# Sử dụng ảnh nền Python 3.10-slim.
FROM python:3.10-slim

# Đặt thư mục làm việc trong container.
WORKDIR /app

# Vô hiệu hóa các câu hỏi tương tác khi cài đặt gói.
ENV DEBIAN_FRONTEND=noninteractive

# --- TỐI ƯU LAYER CACHING ---
# Gộp tất cả các lệnh cài đặt hệ thống và trình duyệt vào một layer RUN duy nhất.
# Layer này ít thay đổi nhất, nên được đặt ở trên cùng để tận dụng cache.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip wget gnupg jq \
    libglib2.0-0 libnss3 libfontconfig1 libgconf-2-4 libxss1 libxi6 \
    libatk1.0-0 libatk-bridge2.0-0 libgtk-3-0 libgdk-pixbuf2.0-0 libgbm-dev \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Tìm và cài đặt phiên bản ChromeDriver tương thích
    && CHROME_VERSION=$(google-chrome --product-version) \
    && CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d . -f 1-3) \
    && CHROMEDRIVER_URL=$(wget -q -O - "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | jq -r --arg ver "$CHROME_MAJOR_VERSION" '.versions[] | select(.version | startswith($ver)) | .downloads.chromedriver[] | select(.platform=="linux64") | .url' | head -n 1) \
    && wget -q --continue -P /tmp/ "${CHROMEDRIVER_URL}" \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64 \
    # Dọn dẹp cache của apt để giữ image nhỏ gọn
    && rm -rf /var/lib/apt/lists/*

# Các layer tiếp theo sẽ được cache lại nếu không có gì thay đổi ở trên.
# Cài đặt các thư viện Python (thay đổi thường xuyên hơn các gói hệ thống).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép healthcheck script và cấp quyền thực thi.
COPY healthcheck.sh .
RUN chmod +x healthcheck.sh

# Sao chép toàn bộ mã nguồn của bot vào (thay đổi thường xuyên nhất).
COPY . .

# --- (MỚI) TÍCH HỢP HEALTH CHECK ---
# Railway và Docker sẽ chạy lệnh này định kỳ để kiểm tra xem container có đang hoạt động tốt không.
# interval=60s: Chạy kiểm tra mỗi 60 giây.
# timeout=10s: Nếu lệnh kiểm tra chạy quá 10 giây, coi như thất bại.
# retries=3: Nếu thất bại 3 lần liên tiếp, container sẽ được đánh dấu là "unhealthy".
HEALTHCHECK --interval=60s --timeout=10s --retries=3 CMD /app/healthcheck.sh

# Lệnh để chạy bot khi container khởi động.
CMD ["python", "main.py"]
