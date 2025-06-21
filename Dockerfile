# Sử dụng ảnh nền selenium/standalone-chrome đã được cấu hình sẵn Chrome và ChromeDriver
FROM selenium/standalone-chrome:latest

# Đặt người dùng là root để đảm bảo quyền apt-get
USER root

# Cập nhật apt và cài đặt các công cụ cơ bản + Python nếu cần
# Ảnh selenium/standalone-chrome thường đã có sẵn Python,
# nên chúng ta chỉ cài các gói công cụ và đảm bảo python3.10 có sẵn nếu không phải mặc định.
# Nếu python3.10 đã có sẵn, lệnh này sẽ không cài đặt lại.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-distutils \
    python3-pip \
    # Các công cụ cần thiết khác nếu bạn vẫn cần chúng
    curl \
    unzip \
    wget \
    jq \
    # Dọn dẹp cache của apt
    && rm -rf /var/lib/apt/lists/*

# Đặt alias cho python và pip nếu cần (hoặc sử dụng python3.10/pip3)
# Chắc chắn rằng chúng ta đang sử dụng đúng phiên bản python3.10
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 100 \
    && update-alternatives --install /usr/bin/pip pip /usr/usr/bin/pip3 100

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của bot vào
COPY . .

# Bạn có thể cân nhắc chuyển về người dùng mặc định của ảnh Selenium nếu muốn bảo mật hơn,
# nhưng thường không cần thiết cho ứng dụng đơn giản này.
# USER seluser # hoặc bất kỳ user nào được định nghĩa trong ảnh nền

# Lệnh để chạy bot
# ChromeDriver và Chrome đã được cài đặt và nằm trong PATH từ ảnh nền
CMD ["python", "rblx_bot.py"]
