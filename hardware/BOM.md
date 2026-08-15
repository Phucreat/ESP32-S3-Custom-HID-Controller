# 📋 Bill of Materials (BOM) & Hardware Specifications

Detailed component breakdown for the **ESP32-S3 Custom HID Controller**.

| STT | Tên linh kiện / Module | Model / Thông số kỹ thuật | Số lượng | Ghi chú & Chức năng |
|:---:|:---|:---|:---:|:---|
| 1 | **Microcontroller Board** | YD-ESP32-S3 (N16R8) (16MB Flash, 8MB PSRAM, Native USB OTG) | 1 | Bộ xử lý trung tâm, giao tiếp USB HID native |
| 2 | **Analog Joystick** | 2-Axis Thumb Joystick Module with Push Button | 2 | Điều hướng di chuyển & góc nhìn (J1, J2) |
| 3 | **Rotary Encoder** | EC11 Rotary Encoder 360° vô cấp (20 xung/vòng) | 2 | Cuộn chuột / Zoom (ENC1) & Điều chỉnh Volume (ENC2) |
| 4 | **I/O Expander** | PCF8574 I2C Module (Địa chỉ mặc định 0x3F/0x27) | 1 | Mở rộng 8 chân Digital Input qua chuẩn I2C 2 dây |
| 5 | **OLED Display** | 0.96 inch SSD1306 I2C Monochrome (128x64 pixels) | 1 | Màn hình HUD hiển thị Mode, Phím bấm, Encoder |
| 6 | **Buzzer** | Active/Passive 5V Buzzer (3.3V compatible) | 1 | Phản hồi âm thanh (Audio Feedback khi nhấn/chuyển mode) |
| 7 | **Tactile Push Buttons** | Nút bấm cơ 12x12mm / Omron Switch | 7 | 3 nút Vàng (BT1-BT3) & 4 nút Đỏ (BT4-BT7) |
| 8 | **Slide Switch / Mode Button**| Mini SPDT Switch / Tactile Button | 1 | Chuyển đổi trạng thái phím (Gõ phím / Standby) |
| 9 | **Passives & Connectors** | Trở kéo 4.7kΩ / 10kΩ, Tụ lọc nguồn 100nF, Header đực/cái | - | Lọc nhiễu nguồn I2C và ADC |
| 10 | **Custom PCB / Breadboard** | 2-layer FR4 PCB hoặc Bo đục lỗ Prototype | 1 | Khung mạch kết nối cố định toàn bộ linh kiện |

---

## ⚡ Nguồn điện & Điện áp hoạt động
- **Điện áp cung cấp (VBUS)**: 5V DC trực tiếp qua cổng USB-C.
- **Điện áp logic**: 3.3V DC (Điều áp On-board trên kit YD-ESP32-S3).
- **Mức tiêu thụ dòng**: ~60mA - 120mA (Tối ưu tiết kiệm điện, an toàn cho cổng USB máy tính/laptop).
