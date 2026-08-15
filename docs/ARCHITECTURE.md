# 🏗️ Technical Architecture & System Design

Tài liệu chuyên sâu về thiết kế kiến trúc phần mềm và kỹ thuật xử lý tín hiệu cho **ESP32-S3 Custom HID Controller**.

`mermaid
graph TD
 subgraph Hardware Layer
 J1[2-Axis Joystick 1] -->|Analog ADC| MCU[ESP32-S3 N16R8]
 J2[2-Axis Joystick 2] -->|Analog ADC| MCU
 ENC[2x Rotary Encoders] -->|Quadrature Signals| MCU
 BTNS[7x Tactile Buttons] -->|Parallel Inputs| PCF[PCF8574 I2C Expander]
 PCF -->|I2C 0x3F| MCU
 MCU -->|I2C 0x3C| OLED[SSD1306 128x64 OLED HUD]
 MCU -->|GPIO 1| BUZZ[Active Buzzer Feedback]
 end

 subgraph Firmware Engine CircuitPython
 MCU --> ADC_PROC[Deadzone & Threshold Filter]
 MCU --> BIT_READER[Bitwise 8-bit Port Reader]
 MCU --> ENC_ENGINE[Hardware Rotary Engine]
 
 ADC_PROC --> ACTION_MAPPER[Action & Keycode Resolver]
 BIT_READER --> ACTION_MAPPER
 ENC_ENGINE --> ACTION_MAPPER
 
 CONF[config.json Profile] -.->|Hot Reload / Boot Load| ACTION_MAPPER
 end

 subgraph USB Subsystem
 ACTION_MAPPER --> HID_KB[USB HID Keyboard]
 ACTION_MAPPER --> HID_MS[USB HID Mouse]
 ACTION_MAPPER --> HID_CC[USB HID Consumer Media]
 
 HID_KB --> HOST[Host Computer / Windows / Linux / macOS / Android]
 HID_MS --> HOST
 HID_CC --> HOST
 end

 subgraph Desktop Suite PyQt6
 HOST -.->|Read / Write config.json| GUI[Controller Configurator Pro]
 end
`

---

## 🔍 Kỹ thuật tối ưu hóa nổi bật

### 1. Tối ưu hóa đọc I2C Bitwise không gây nghẽn bus
Thay vì đọc từng chân riêng lẻ qua 8 lệnh I2C liên tiếp làm sụt giảm khung hình loop, firmware sử dụng phương pháp **Single-byte Bitwise Sampling**:
`python
# Đọc toàn bộ 8 chân chỉ bằng 1 byte truyền thông I2C duy nhất
btns = pcf.read_gpio()
for i in range(8):
 is_pressed = (btns & (1 << i)) == 0 # Trích xuất trạng thái tức thì
`
- **Hiệu quả**: Giảm 87.5% lưu lượng I2C bus, loại bỏ jitter và đảm bảo thời gian quét phím < 10ms.

### 2. Thuật toán lọc Deadzone cho trục Analog Joystick
Các biến trở cần gạt thường có hiện tượng trôi điểm zero (drift) do sai số cơ khí. Thuật toán phân ngưỡng hai đầu được áp dụng:
	ext{Negative State} = egin{cases} 	ext{True} & 	ext{if } V_{ADC} < 16500 \ 	ext{False} & 	ext{otherwise} \end{cases}
	ext{Positive State} = egin{cases} 	ext{True} & 	ext{if } V_{ADC} > 49000 \ 	ext{False} & 	ext{otherwise} \end{cases}
Vùng an toàn $[16500, 49000]$ (Deadzone) ngăn ngừa hoàn toàn hiện tượng bấm nhầm hoặc loạn phím khi tay cầm ở trạng thái nghỉ.

### 3. Cơ chế Hot-Config qua USB Mass Storage
Khác với các tay cầm thông thường phải flash lại firmware C++ mỗi khi muốn đổi nút:
1. Tay cầm tự động hiển thị như một ổ đĩa USB Flash mang tên CIRCUITPY.
2. Ứng dụng Desktop **Controller Configurator Pro (PyQt6)** trực tiếp đọc và ghi file config.json.
3. Firmware tải profile cấu hình và ánh xạ trực tiếp sang các Keycode, MouseAction, ConsumerControlCode chuẩn quốc tế.
