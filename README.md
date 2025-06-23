# RBLX-Auto Bot

Bot Discord tự động hóa các tác vụ trên website `rblx.earth` bằng Selenium.

## ✨ Tính năng chính

* Điều khiển bằng lệnh gạch chéo (`/`) trên Discord.
* **`/start <username>`**: Liên kết tài khoản Roblox.
* **`/promo <code>`**: Tự động nhập mã khuyến mãi.
* **`/balance`**: Kiểm tra số dư hiện tại.
* Chạy 24/7 trên các nền tảng hosting như Railway nhờ Docker.

## 🚀 Cài đặt và Chạy

### Yêu cầu

* Python 3.10+
* Docker
* Tài khoản Railway (hoặc một nền tảng hosting Docker khác)
* Tài khoản Discord và một Bot Application

### Cài đặt Local (Để phát triển)

1.  Clone repository này:
    ```bash
    git clone [https://github.com/disa12311/rblx-auto.git](https://github.com/disa12311/rblx-auto.git)
    cd rblx-auto
    ```

2.  Tạo môi trường ảo và cài đặt các thư viện:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  Tạo file `.env` và thêm token của bạn:
    ```
    DISCORD_TOKEN="YOUR_DISCORD_BOT_TOKEN_HERE"
    ```
    *Lưu ý: Code cần được chỉnh sửa để đọc từ file `.env` khi chạy local.*

4.  Chạy bot:
    ```bash
    python main.py
    ```

### Deploy lên Railway

1.  Push code của bạn lên một repository GitHub.
2.  Trên Railway, tạo một "New Project" và chọn "Deploy from GitHub repo".
3.  Chọn repository của bạn. Railway sẽ tự động build từ `Dockerfile`.
4.  Vào tab "Variables" của project, thêm một biến môi trường mới:
    * **Name:** `DISCORD_TOKEN`
    * **Value:** Dán token bot Discord của bạn vào đây.

## 📝 Cách sử dụng

Sau khi bot online và đã được mời vào server của bạn:

1.  **`/start <tên_user_roblox>`**: Luôn chạy lệnh này đầu tiên để đăng nhập.
2.  **`/balance`**: Kiểm tra số dư.
3.  **`/promo <mã_code>`**: Nhập mã khuyến mãi.

## 📁 Cấu trúc dự án

```
/rblx-auto/
├── main.py             # File chạy chính
├── config.py           # Quản lý cấu hình
├── bot/                # Module chứa logic của bot Discord
├── selenium_handler/   # Module quản lý Selenium
└── utils/              # Các công cụ tiện ích (logging)
```
