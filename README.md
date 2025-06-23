# RBLX-Auto Bot

Một bot Discord được lập trình bằng Python, sử dụng Selenium để tự động hóa các tác vụ trên website `rblx.earth`, giúp bạn tham gia các hoạt động một cách hiệu quả. Bot được thiết kế để chạy 24/7 trên các nền tảng hosting như Railway.

## ✨ Tính năng chính

Bot được điều khiển hoàn toàn thông qua các lệnh gạch chéo (`/`) tiện lợi trên Discord:

* **`/start <username>`**: Lệnh quan trọng nhất, dùng để liên kết bot với tài khoản Roblox của bạn trên website.
* **`/balance`**: Kiểm tra số dư Robux hiện tại mà bạn đã kiếm được.
* **`/promo <code>`**: Tự động điều hướng và nhập mã khuyến mãi.
* **`/auto_giveaway <On/Off>`**: Bật hoặc tắt chế độ tự động tham gia các sự kiện giveaway định kỳ.
* **`/send_to`**: Một lệnh tiện ích để gửi tin nhắn tùy chỉnh đến một kênh hoặc cho chính bạn qua DM.

## 🚀 Cài đặt và Deploy

### Yêu cầu

* Python 3.10+
* Docker (cho việc build trên Railway)
* Tài khoản [Railway](https://railway.app/) (hoặc một nền tảng hosting Docker tương tự)
* Tài khoản Discord và một Bot Application đã được tạo trên [Discord Developer Portal](https://discord.com/developers/applications).

### Deploy lên Railway

Đây là phương pháp được đề xuất để bot hoạt động 24/7.

1.  **Fork/Clone Repository:** Tạo một bản sao của repository này về tài khoản GitHub của bạn.
2.  **Tạo Project trên Railway:**
    * Đăng nhập vào Railway, chọn "New Project".
    * Chọn "Deploy from GitHub repo" và kết nối với repository bạn vừa tạo.
    * Railway sẽ tự động phát hiện `Dockerfile` và bắt đầu quá trình build.
3.  **Thêm Biến môi trường:**
    * Sau khi project được tạo, vào tab **"Variables"**.
    * Thêm 2 biến sau:
        * `DISCORD_TOKEN`: (Bắt buộc) Dán mã token của bot Discord của bạn vào đây.
        * `STATUS_CHANNEL_ID`: (Tùy chọn nhưng khuyến khích) Dán ID của kênh Discord mà bạn muốn bot gửi các thông báo trạng thái (ví dụ: tham gia giveaway thành công, báo lỗi).

## 📝 Cách sử dụng

Sau khi bot đã online và được mời vào server Discord của bạn:

1.  **Bắt đầu:** Luôn chạy lệnh này đầu tiên để bot đăng nhập vào website.
    * `/start roblox_username:tên_tài_khoản_roblox_của_bạn`

2.  **Bật tự động:** Để bot tự làm việc, hãy bật tính năng auto giveaway.
    * `/auto_giveaway status:On`
    * Bot sẽ gửi thông báo vào kênh `STATUS_CHANNEL_ID` mỗi khi nó hoạt động.

3.  **Kiểm tra & Tương tác:**
    * `/balance` - Xem bạn đã kiếm được bao nhiêu.
    * `/promo code:SOMECODE` - Nhập một mã khuyến mãi mới.
    * `/send_to message:"Hello" channel:#general send_dm:Off` - Gửi tin nhắn đến kênh #general.

## 📁 Cấu trúc dự án

Dự án được tổ chức theo mô hình module hóa để dễ dàng quản lý và mở rộng:

```
/rblx-auto/
├── main.py             # File chính để chạy bot, rất gọn nhẹ
├── config.py           # Quản lý cấu hình tập trung (token, URL, cài đặt...)
├── requirements.txt    # Danh sách các thư viện Python
├── Dockerfile          # Cấu hình môi trường để deploy
├── README.md           # Tài liệu hướng dẫn
|
├── bot/                # Module chứa logic của bot Discord
│   ├── core.py         # Khởi tạo bot, load Cogs, xử lý sự kiện
│   └── cogs/
│       └── roblox.py     # Chứa tất cả các lệnh slash command
|
├── selenium_handler/   # Module quản lý Selenium
│   └── driver_setup.py   # Khởi tạo và cấu hình WebDriver
|
└── utils/              # Các công cụ tiện ích
    └── app_logger.py     # Thiết lập hệ thống logging
```
