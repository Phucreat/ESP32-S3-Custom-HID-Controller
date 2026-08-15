# 🔌 Pinout & Hardware Wiring Guide

Sơ đồ kết nối chi tiết giữa **YD-ESP32-S3** và các module ngoại vi.

`
 +-----------------------------------+
 | YD-ESP32-S3 |
 | |
 [I2C SCL] --->| GPIO 9 GPIO 1 |<--- [Buzzer Signal]
 [I2C SDA] --->| GPIO 8 GPIO 21 |<--- [Mode Switch SWS]
 | |
 [Joystick 1 VRx]| GPIO 6 GPIO 7 |<--- [Joystick 2 VRx]
 [Joystick 1 VRy]| GPIO 5 GPIO 2 |<--- [Joystick 2 VRy]
 [Joystick 1 SW] | GPIO 4 GPIO 48 |<--- [Joystick 2 SW]
 | |
 [Encoder 1 A] | GPIO 10 GPIO 16 |<--- [Encoder 2 A]
 [Encoder 1 B] | GPIO 3 GPIO 15 |<--- [Encoder 2 B]
 +-----------------------------------+
`

---

## 1. Bảng phân bổ chân GPIO (ESP32-S3)

| Nhóm chức năng | Tên chân thiết bị | Chân ESP32-S3 | Chế độ cấu hình | Mô tả kỹ thuật |
|:---|:---|:---|:---|:---|
| **I2C Bus** | I2C SCL | **GPIO 9** | BusIO I2C Clock | Chia sẻ chung cho OLED SSD1306 & PCF8574 |
| | I2C SDA | **GPIO 8** | BusIO I2C Data | Tốc độ chuẩn 100 kHz hoặc 400 kHz Fast-mode |
| **Joystick 1 (Trái)**| J1 X-Axis (VRx) | **GPIO 6** | ADC1 Channel 5 | Đọc tọa độ Analog X (16-bit ADC scale) |
| | J1 Y-Axis (VRy) | **GPIO 5** | ADC1 Channel 4 | Đọc tọa độ Analog Y (16-bit ADC scale) |
| | J1 Click (SW) | **GPIO 4** | Digital In (Pull-Up) | Nút nhấn tích hợp cần gạt trái |
| **Joystick 2 (Phải)**| J2 X-Axis (VRx) | **GPIO 7** | ADC1 Channel 6 | Đọc tọa độ Analog X (16-bit ADC scale) |
| | J2 Y-Axis (VRy) | **GPIO 2** | ADC1 Channel 1 | Đọc tọa độ Analog Y (16-bit ADC scale) |
| | J2 Click (SW) | **GPIO 48** | Digital In (Pull-Up) | Nút nhấn tích hợp cần gạt phải |
| **Rotary Encoder 1**| ENC1 Phase A | **GPIO 10** | RotaryIO Quadrature | Đọc xung quay Encoder 1 |
| | ENC1 Phase B | **GPIO 3** | RotaryIO Quadrature | Xác định chiều quay CW / CCW |
| **Rotary Encoder 2**| ENC2 Phase A | **GPIO 16** | RotaryIO Quadrature | Đọc xung quay Encoder 2 |
| | ENC2 Phase B | **GPIO 15** | RotaryIO Quadrature | Xác định chiều quay CW / CCW |
| **System Controls** | Mode Toggle (SWS)| **GPIO 21** | Digital In (Pull-Up) | Nút chuyển đổi ON/OFF Typing Mode |
| | Feedback Buzzer | **GPIO 1** | Digital Out | Phát tiếng bíp thông báo |

---

## 2. Kết nối Mở rộng I/O qua PCF8574 (Địa chỉ I2C: 0x3F)

Bộ mở rộng I/O PCF8574 giúp giải phóng chân vi điều khiển và chống nghẽn đường truyền:

| Chân PCF8574 | Tên nút trên tay cầm | Vị trí bố trí | Chức năng mặc định |
|:---:|:---|:---|:---|
| **P0** | **BT1** | Cụm Vàng - Đỉnh Trên | Phím 1 (hoặc phím tùy chỉnh) |
| **P1** | **BT2** | Cụm Vàng - Dưới Trái | Phím 2 |
| **P2** | **BT3** | Cụm Vàng - Dưới Phải | Phím 3 |
| **P3** | **BT4** | Cụm Đỏ - Đỉnh Trên | Phím 4 |
| **P4** | **BT5** | Cụm Đỏ - Đáy Dưới | Phím 5 |
| **P5** | **BT6** | Cụm Đỏ - Cạnh Trái | Phím 6 |
| **P6** | **BT7** | Cụm Đỏ - Cạnh Phải | Phím 7 |
| **P7** | **BT8 / Spare** | Dự phòng mở rộng | Phím 8 |
