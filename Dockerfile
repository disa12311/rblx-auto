# Sử dụng ảnh nền selenium/standalone-chrome đã được cấu hình sẵn Chrome và ChromeDriver
FROM selenium/standalone-chrome:latest

# Cài đặt Python 3.10 (nếu chưa có hoặc cần phiên bản cụ thể)
# Ảnh selenium/standalone-chrome thường dựa trên Debian, nên có thể cài Python bằng apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-distutils \
    python3-pip \
    # Các công cụ cần thiết khác nếu bạn vẫn cần chúng
    curl \
    unzip \
    wget \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Đặt alias cho python và pip nếu cần (hoặc sử dụng python3.10/pip3)
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của bot vào
COPY . .

# Lệnh để chạy bot
# ChromeDriver và Chrome đã được cài đặt và nằm trong PATH từ ảnh nền
CMD ["python", "rblx_bot.py"]
