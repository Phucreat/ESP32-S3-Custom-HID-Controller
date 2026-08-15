# ==========================================
# Project: ESP32-S3 Keyboard & Mouse Controller
# Hardware Update: J2 on ADC pins (IO19, IO20), SWS on IO21
# ==========================================
import time
import json
import board
import busio
import digitalio
import analogio
import rotaryio
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode


import adafruit_pcf8574
import adafruit_ssd1306

# ==========================================
# 1. KHỞI TẠO PHẦN CỨNG
# ==========================================
i2c = busio.I2C(scl=board.GPIO9, sda=board.GPIO8, frequency=100000)

try:
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
    has_oled = True
except: has_oled = False

try:
    # Nhớ dùng đúng địa chỉ 0x3F mà chúng ta đã quét ra
    pcf = adafruit_pcf8574.PCF8574(i2c, address=0x3F)
    
    # Ghi 0xFF để kéo cả 8 chân lên HIGH (Sẵn sàng làm chân đọc nút nhấn)
    # Giống hệt lệnh pcf.write8(0xFF); bên C++
    pcf.write_gpio(0xFF)
    
    has_pcf = True
except Exception as e:
    print("Không tìm thấy PCF:", e)
    has_pcf = False

buzzer = digitalio.DigitalInOut(board.GPIO1); buzzer.direction = digitalio.Direction.OUTPUT

# Nút SWS đã dời sang GPIO21 theo mạch mới
mode_sw = digitalio.DigitalInOut(board.GPIO21); mode_sw.switch_to_input(pull=digitalio.Pull.UP)

# Joystick 1
jx1 = analogio.AnalogIn(board.GPIO6); jy1 = analogio.AnalogIn(board.GPIO5)
jsw1 = digitalio.DigitalInOut(board.GPIO4); jsw1.switch_to_input(pull=digitalio.Pull.UP)

# Joystick 2 ( Hoạt động Analog hoàn hảo)
jx2 = analogio.AnalogIn(board.GPIO7); jy2 = analogio.AnalogIn(board.GPIO2)
jsw2 = digitalio.DigitalInOut(board.GPIO48); jsw2.switch_to_input(pull=digitalio.Pull.UP)

# Encoders
enc1 = rotaryio.IncrementalEncoder(board.GPIO10, board.GPIO3)
enc2 = rotaryio.IncrementalEncoder(board.GPIO16, board.GPIO15)
# Khởi tạo bộ điều khiển âm lượng/đa phương tiện
cc = ConsumerControl(usb_hid.devices)
# ==========================================
# 2. KHỞI TẠO USB HID & CONFIG
# ==========================================
keyboard = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

try:
    with open("config.json", "r") as f:
        config = json.load(f)
except: config = {}

# Map phím ảo
# Từ điển Map toàn bộ phím chuẩn xác theo adafruit_hid.keycode
KEY_MAP = {
    # Bảng chữ cái
    "A": Keycode.A, "B": Keycode.B, "C": Keycode.C, "D": Keycode.D, "E": Keycode.E,
    "F": Keycode.F, "G": Keycode.G, "H": Keycode.H, "I": Keycode.I, "J": Keycode.J,
    "K": Keycode.K, "L": Keycode.L, "M": Keycode.M, "N": Keycode.N, "O": Keycode.O,
    "P": Keycode.P, "Q": Keycode.Q, "R": Keycode.R, "S": Keycode.S, "T": Keycode.T,
    "U": Keycode.U, "V": Keycode.V, "W": Keycode.W, "X": Keycode.X, "Y": Keycode.Y, "Z": Keycode.Z,
    
    # Hàng số
    "1": Keycode.ONE, "2": Keycode.TWO, "3": Keycode.THREE, "4": Keycode.FOUR, "5": Keycode.FIVE,
    "6": Keycode.SIX, "7": Keycode.SEVEN, "8": Keycode.EIGHT, "9": Keycode.NINE, "0": Keycode.ZERO,
    
    # Phím điều hướng & Chức năng
    "SPACE": Keycode.SPACE, "ENTER": Keycode.ENTER, "ESC": Keycode.ESCAPE,
    "UP_ARROW": Keycode.UP_ARROW, "DOWN_ARROW": Keycode.DOWN_ARROW,
    "LEFT_ARROW": Keycode.LEFT_ARROW, "RIGHT_ARROW": Keycode.RIGHT_ARROW,
    "BACKSPACE": Keycode.BACKSPACE, "TAB": Keycode.TAB,
    
    # Phím hệ thống
    "SHIFT": Keycode.SHIFT, "CTRL": Keycode.CONTROL, "ALT": Keycode.ALT, "WINDOWS": Keycode.WINDOWS
}

# ==========================================
# 3. CÁC HÀM XỬ LÝ
# ==========================================
def beep(duration=0.05):
    buzzer.value = True
    time.sleep(duration)
    buzzer.value = False

def execute_action(action_str, is_pressed):
    if not action_str: return
    
    # Xử lý phím Bàn phím (KEY_)
    if action_str.startswith("KEY_"):
        key_name = action_str.replace("KEY_", "")
        if key_name in KEY_MAP:
            if is_pressed: keyboard.press(KEY_MAP[key_name])
            else: keyboard.release(KEY_MAP[key_name])
            
    # Xử lý phím Chuột (MOUSE_)
    elif action_str.startswith("MOUSE_"):
        if is_pressed:
            if action_str == "MOUSE_WHEEL_UP": mouse.move(wheel=1)
            elif action_str == "MOUSE_WHEEL_DOWN": mouse.move(wheel=-1)
            elif action_str == "MOUSE_LEFT": mouse.click(Mouse.LEFT_BUTTON)
            
    # Xử lý phím Âm lượng/Đa phương tiện (CC_)
    elif action_str.startswith("CC_"):
        cc_name = action_str.replace("CC_", "")
        # Kiểm tra xem tên phím có tồn tại trong thư viện adafruit_hid không
        if hasattr(ConsumerControlCode, cc_name):
            if is_pressed:
                # Gửi lệnh (ví dụ VOLUME_INCREMENT)
                cc.send(getattr(ConsumerControlCode, cc_name))

def process_analog_axis(val, action_neg, action_pos, state_neg, state_pos, enable_usb):
    """ Biến trục Analog thành 2 nút nhấn (Đã cân chỉnh Deadzone chuẩn theo C++) """
    
    # Ngưỡng kích hoạt tương đương y < -1000 và y > 1000 trong C++
    is_neg = val < 16500
    is_pos = val > 49000
    
    if is_neg != state_neg:
        if enable_usb: execute_action(action_neg, is_neg)
        state_neg = is_neg
        
    if is_pos != state_pos:
        if enable_usb: execute_action(action_pos, is_pos)
        state_pos = is_pos
        
    return state_neg, state_pos

# ==========================================
# 4. VÒNG LẶP CHÍNH
# ==========================================
def main():
    beep(0.1)
    
    last_btn_states = {"BT"+str(i+1): False for i in range(8)}
    last_btn_states["J1_SW"] = False; last_btn_states["J2_SW"] = False
    
    # Trạng thái 4 hướng của Joystick
    st_j1_xn = False; st_j1_xp = False; st_j1_yn = False; st_j1_yp = False
    st_j2_xn = False; st_j2_xp = False; st_j2_yn = False; st_j2_yp = False

    last_e1_pos = enc1.position; last_e2_pos = enc2.position
    
    enable_typing = True 
    last_sws_state = False
    last_oled_update = 0

    while True:
        # --- BẬT / TẮT TÍNH NĂNG GÕ PHÍM BẰNG NÚT SWS ---
        current_sws = not mode_sw.value
        if current_sws and not last_sws_state:
            enable_typing = not enable_typing
            beep(0.1)
            if not enable_typing: keyboard.release_all() # Nhả toàn bộ phím an toàn
        last_sws_state = current_sws
        
        mode_text = "KEYBOARD: ON" if enable_typing else "STANDBY: OFF"
        pressed_list = []

        # --- NÚT NHẤN PCF ---
# --- NÚT NHẤN PCF (Tối ưu bằng read_gpio của thư viện) ---
        if has_pcf:
            try:
                # 1. Đọc 8 bit đúng 1 lần duy nhất (Cực nhanh, không nghẽn I2C)
                btns = pcf.read_gpio()
                
                # 2. Dùng vòng lặp nội bộ để tách bit 
                for i in range(8):
                    btn_key = f"BT{i+1}"
                    
                    # Phép toán Bitwise (Giống hệt bitRead(btns, i) == LOW)
                    is_pressed = (btns & (1 << i)) == 0 
                    
                    if is_pressed: pressed_list.append(f"B{i+1}")
                    
                    # 3. Kích hoạt gõ phím
                    if is_pressed != last_btn_states[btn_key]:
                        if enable_typing: execute_action(config.get(btn_key), is_pressed)
                        last_btn_states[btn_key] = is_pressed
                        
            except Exception as e:
                print("⚠️ Lỗi đọc PCF bằng thư viện:", e)

        # --- NÚT JOYSTICK ---
        for j_key, j_pin, j_name in [("J1_SW", jsw1, "J1"), ("J2_SW", jsw2, "J2")]:
            is_pressed = not j_pin.value
            if is_pressed: pressed_list.append(j_name)
            if is_pressed != last_btn_states[j_key]:
                if enable_typing: execute_action(config.get(j_key), is_pressed)
                last_btn_states[j_key] = is_pressed

        # --- TRỤC JOYSTICK 1 (BIẾN THÀNH PHÍM) ---
        st_j1_xn, st_j1_xp = process_analog_axis(jx1.value, config.get("J1_X_NEG"), config.get("J1_X_POS"), st_j1_xn, st_j1_xp, enable_typing)
        st_j1_yn, st_j1_yp = process_analog_axis(jy1.value, config.get("J1_Y_NEG"), config.get("J1_Y_POS"), st_j1_yn, st_j1_yp, enable_typing)
        
        if st_j1_xn: pressed_list.append("J1<")
        if st_j1_xp: pressed_list.append("J1>")
        if st_j1_yn: pressed_list.append("J1^")
        if st_j1_yp: pressed_list.append("J1v")

        # --- TRỤC JOYSTICK 2 (Đã fix phần cứng, chạy mượt) ---
        st_j2_xn, st_j2_xp = process_analog_axis(jx2.value, config.get("J2_X_NEG"), config.get("J2_X_POS"), st_j2_xn, st_j2_xp, enable_typing)
        st_j2_yn, st_j2_yp = process_analog_axis(jy2.value, config.get("J2_Y_NEG"), config.get("J2_Y_POS"), st_j2_yn, st_j2_yp, enable_typing)
        
        if st_j2_xn: pressed_list.append("J2<")
        if st_j2_xp: pressed_list.append("J2>")
        if st_j2_yn: pressed_list.append("J2^")
        if st_j2_yp: pressed_list.append("J2v")

        # --- ENCODERS ---
        e1_pos = enc1.position
        if e1_pos != last_e1_pos:
            if enable_typing:
                action = config.get("ENC1_CW") if e1_pos > last_e1_pos else config.get("ENC1_CCW")
                execute_action(action, True); execute_action(action, False)
            last_e1_pos = e1_pos

        e2_pos = enc2.position
        if e2_pos != last_e2_pos:
            if enable_typing:
                action = config.get("ENC2_CW") if e2_pos > last_e2_pos else config.get("ENC2_CCW")
                execute_action(action, True); execute_action(action, False)
            last_e2_pos = e2_pos

        # --- MÀN HÌNH OLED ---
        now = time.monotonic()
        if has_oled and (now - last_oled_update > 0.3):
            oled.fill(0)
            oled.text(mode_text, 0, 0, 1)
            oled.text("Btn:" + ",".join(pressed_list), 0, 15, 1)
            oled.text(f"Enc1:{e1_pos} Enc2:{e2_pos}", 0, 30, 1)
            oled.text("ESP32-S3 KEYBOARD", 0, 50, 1)
            oled.show()
            last_oled_update = now

        time.sleep(0.01)

if __name__ == "__main__":
    main()