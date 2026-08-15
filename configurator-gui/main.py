import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QComboBox,
                             QGroupBox, QGridLayout, QScrollArea, QFrame, QMessageBox,
                             QFileDialog)
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QPen, QLinearGradient

# =================================================================
# DANH SÁCH DỮ LIỆU PHÍM (THEO THƯ VIỆN CIRCUITPYTHON HID)
# =================================================================
HID_KEYS = {
    "Bàn phím (Alphabet)": [f"KEY_{c}" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"],
    "Hàng phím số": [f"KEY_{c}" for c in "ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE ZERO".split()],
    "Phím Chức năng": [f"KEY_F{i}" for i in range(1, 13)],
    "Điều hướng & Hệ thống": [
        "KEY_ENTER", "KEY_ESCAPE", "KEY_BACKSPACE", "KEY_TAB", "KEY_SPACE",
        "KEY_UP_ARROW", "KEY_DOWN_ARROW", "KEY_LEFT_ARROW", "KEY_RIGHT_ARROW",
        "KEY_DELETE", "KEY_HOME", "KEY_END", "KEY_PAGE_UP", "KEY_PAGE_DOWN",
        "KEY_PRINT_SCREEN", "KEY_SCROLL_LOCK", "KEY_PAUSE", "KEY_INSERT"
    ],
    "Phím đặc biệt (Modifiers)": [
        "KEY_SHIFT", "KEY_CONTROL", "KEY_ALT", "KEY_GUI", "KEY_WINDOWS", "KEY_COMMAND"
    ],
    "Chuột (Mouse)": [
        "MOUSE_LEFT", "MOUSE_RIGHT", "MOUSE_MIDDLE",
        "MOUSE_WHEEL_UP", "MOUSE_WHEEL_DOWN"
    ],
    "Đa phương tiện (Media)": [
        "CC_VOLUME_INCREMENT", "CC_VOLUME_DECREMENT", "CC_MUTE",
        "CC_PLAY_PAUSE", "CC_SCAN_NEXT_TRACK", "CC_SCAN_PREVIOUS_TRACK",
        "CC_BRIGHTNESS_INCREMENT", "CC_BRIGHTNESS_DECREMENT"
    ]
}

ALL_OPTIONS = [item for sublist in HID_KEYS.values() for item in sublist]

# =================================================================
# LỚP ĐỒ HỌA TÁI HIỆN TAY CẦM THỰC TẾ (V2.1 - ĐÃ SỬA BỐ CỤC)
# =================================================================


class ControllerGraphic(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 600)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Vẽ bo mạch PCB (Xanh lá đậm hệt như ảnh)
        p.setPen(QPen(QColor("#244224"), 3))
        p.setBrush(QBrush(QColor("#1b331b")))
        p.drawRoundedRect(20, 20, 460, 560, 10, 10)

        # 2. Vẽ ESP32-S3 (Chính giữa)
        p.setBrush(QBrush(QColor("#1a1a1a")))
        p.drawRoundedRect(180, 180, 140, 200, 5, 5)
        p.setPen(QPen(Qt.GlobalColor.white))
        p.drawText(QRect(180, 250, 140, 30),
                   Qt.AlignmentFlag.AlignCenter, "ESP32-S3")

        # 3. Nút SWS (Chính giữa trên cùng)
        p.setBrush(QBrush(QColor("#333333")))
        p.drawRect(230, 40, 40, 40)
        p.drawText(225, 35, "MODE SWS")

        # 4. Buzzer (Loa - Bên trái ESP32)
        p.setBrush(QBrush(QColor("#222222")))
        p.drawEllipse(140, 255, 30, 30)
        p.drawText(135, 250, "BEEP")

        # 5. Màn hình OLED (Gắn dưới Center)
        p.setBrush(QBrush(QColor("#000000")))
        p.setPen(QPen(QColor("#38bdf8"), 2))
        p.drawRect(175, 420, 150, 80)
        p.drawText(QRect(175, 420, 150, 80),
                   Qt.AlignmentFlag.AlignCenter, "OLED DISPLAY")

        # --- PHÍA TRÁI ---

        # 6. Joystick 1 (Trái) - Hạ thấp hơn để nhường chỗ Mode Switch
        p.setBrush(QBrush(QColor("#000000")))
        p.drawEllipse(60, 140, 100, 100)  # J1 (Cx: 110, Cy: 190)

        # 7. 3 nút Vàng bố trí hình TAM GIÁC
        p.setBrush(QBrush(QColor("#facc15")))  # Nút vàng
        # Đỉnh trên
        p.drawEllipse(90, 260, 40, 40)  # BT1
        # Hai đỉnh dưới
        p.drawEllipse(50, 320, 40, 40)  # BT2 (dưới trái)
        p.drawEllipse(130, 320, 40, 40)  # BT3 (dưới phải)

        p.setPen(QPen(Qt.GlobalColor.black))
        p.drawText(100, 285, "BT1")
        p.drawText(60, 345, "BT2")
        p.drawText(140, 345, "BT3")

        # --- PHÍA PHẢI ---

        # 8. Joystick 2 (Phải)
        p.setBrush(QBrush(QColor("#000000")))
        p.drawEllipse(340, 160, 100, 100)  # J2 (Cx: 390, Cy: 210)

        # 9. Hai Encoder (SỬA LẠI VỊ TRÍ: Nằm ngay trên Joystick Phải)
        p.setBrush(QBrush(QColor("#777777")))
        p.setPen(QPen(Qt.GlobalColor.white))
        # Encoder 1
        p.drawEllipse(355, 80, 30, 30)  # E1 Knob
        p.drawText(360, 75, "E1")
        # Encoder 2
        p.drawEllipse(395, 80, 30, 30)  # E2 Knob
        p.drawText(400, 75, "E2")

        # 10. 4 nút Đỏ bố trí hình THOI (Diamond)
        p.setBrush(QBrush(QColor("#ef4444")))  # Nút đỏ
        # Bố trí hình thoi quanh Cx: 390, Cy: 340
        # Nút Trên
        p.drawEllipse(370, 280, 40, 40)  # BT4
        # Nút Dưới
        p.drawEllipse(370, 360, 40, 40)  # BT5
        # Nút Trái
        p.drawEllipse(330, 320, 40, 40)  # BT6
        # Nút Phải
        p.drawEllipse(410, 320, 40, 40)  # BT7

        p.setPen(QPen(Qt.GlobalColor.black))
        p.drawText(380, 305, "BT4")
        p.drawText(380, 385, "BT5")
        p.drawText(340, 345, "BT6")
        p.drawText(420, 345, "BT7")

# =================================================================
# GIAO DIỆN CHÍNH (V2.1 - SỬA LỖI MÀU SẮC MENU)
# =================================================================


class Configurator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROV Controller Configurator Pro V2.1")
        self.setMinimumSize(1200, 800)
        self.combos = {}
        self.init_ui()
        self.load_current_config()

    def init_ui(self):
        # Style hiện đại (Dark Slate) với fix lỗi trùng màu phím
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QLabel { color: #cbd5e1; font-weight: bold; font-family: 'Segoe UI'; }
            QGroupBox { border: 2px solid #1e293b; border-radius: 10px; margin-top: 15px; 
                        color: #38bdf8; font-size: 16px; font-weight: bold; padding-top: 20px;}
            
            /* CÀI ĐẶT MÀU CHO COMBOBOX (VỐN BỊ LỖI MÀU) */
            QComboBox { 
                background-color: #1e293b; 
                color: #f8fafc; /* Chữ màu trắng khi được chọn */
                border: 1px solid #334155; 
                padding: 5px; 
                border-radius: 5px; 
                font-size: 13px; 
                min-width: 150px; 
            }
            QComboBox:hover { border-color: #38bdf8; }
            
            /* CÀI ĐẶT MÀU CHO DROPDOWN LIST (KHI ĐANG CHỌN) */
            QComboBox QAbstractItemView {
                background-color: #1e293b; /* Nền tối */
                color: #f8fafc; /* Chữ trắng */
                selection-background-color: #0284c7; /* Nền xanh khi di chuột qua */
                selection-color: #ffffff; /* Chữ trắng khi di chuột qua */
                border: 1px solid #334155;
            }
            /* Đặt màu riêng cho các item không thể chọn (Header) */
            QComboBox QAbstractItemView::item:disabled {
                color: #64748b;
            }

            QPushButton { background-color: #0284c7; color: white; font-weight: bold; 
                          border-radius: 8px; font-size: 16px; min-height: 50px; }
            QPushButton:hover { background-color: #0369a1; }
            QScrollArea { border: none; background-color: transparent; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # CỘT TRÁI: Đồ họa
        left_side = QVBoxLayout()
        header = QLabel("MÔ PHỎNG BỐ CỤC CHUẨN")
        header.setStyleSheet(
            "font-size: 20px; color: #38bdf8; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_side.addWidget(header)

        self.graphic = ControllerGraphic()
        left_side.addWidget(self.graphic)
        main_layout.addLayout(left_side, 45)

        # CỘT PHẢI: Cài đặt (Scrollable)
        scroll = QScrollArea()
        scroll_content = QWidget()
        self.settings_layout = QVBoxLayout(scroll_content)

        # 1. Nhóm nút bấm Vàng (3 nút - Tam giác)
        yellow_box = QGroupBox("Cụm Phím Vàng (Trái - Tam giác)")
        y_grid = QGridLayout()
        self.add_setting(y_grid, "BT1 (Vàng - Đỉnh trên)", "BT1", 0)
        self.add_setting(y_grid, "BT2 (Vàng - Dưới trái)", "BT2", 1)
        self.add_setting(y_grid, "BT3 (Vàng - Dưới phải)", "BT3", 2)
        yellow_box.setLayout(y_grid)
        self.settings_layout.addWidget(yellow_box)

        # 2. Nhóm nút bấm Đỏ (4 nút - Hình thoi)
        red_box = QGroupBox("Cụm Phím Đỏ (Phải - Hình thoi)")
        r_grid = QGridLayout()
        self.add_setting(r_grid, "BT4 (Đỏ - Trên đỉnh)", "BT4", 0)
        self.add_setting(r_grid, "BT5 (Đỏ - Dưới đáy)", "BT5", 1)
        self.add_setting(r_grid, "BT6 (Đỏ - Cạnh trái)", "BT6", 2)
        self.add_setting(r_grid, "BT7 (Đỏ - Cạnh phải)", "BT7", 3)
        red_box.setLayout(r_grid)
        self.settings_layout.addWidget(red_box)

        # 3. Nhóm Joystick 1
        j1_box = QGroupBox("Joystick 1 (Bên Trái)")
        j1_grid = QGridLayout()
        self.add_setting(j1_grid, "J1 Lên", "J1_Y_NEG", 0)
        self.add_setting(j1_grid, "J1 Xuống", "J1_Y_POS", 1)
        self.add_setting(j1_grid, "J1 Trái", "J1_X_NEG", 2)
        self.add_setting(j1_grid, "J1 Phải", "J1_X_POS", 3)
        self.add_setting(j1_grid, "J1 Nhấn (SW)", "J1_SW", 4)
        j1_box.setLayout(j1_grid)
        self.settings_layout.addWidget(j1_box)

        # 4. Nhóm Joystick 2
        j2_box = QGroupBox("Joystick 2 (Bên Phải)")
        j2_grid = QGridLayout()
        self.add_setting(j2_grid, "J2 Lên", "J2_Y_NEG", 0)
        self.add_setting(j2_grid, "J2 Xuống", "J2_Y_POS", 1)
        self.add_setting(j2_grid, "J2 Trái", "J2_X_NEG", 2)
        self.add_setting(j2_grid, "J2 Phải", "J2_X_POS", 3)
        self.add_setting(j2_grid, "J2 Nhấn (SW)", "J2_SW", 4)
        j2_box.setLayout(j2_grid)
        self.settings_layout.addWidget(j2_box)

        # 5. Nhóm Encoder
        e_box = QGroupBox("Núm Xoay (Encoders - Trên J2)")
        e_grid = QGridLayout()
        self.add_setting(e_grid, "E1 Xoay Phải (CW)", "ENC1_CW", 0)
        self.add_setting(e_grid, "E1 Xoay Trái (CCW)", "ENC1_CCW", 1)
        self.add_setting(e_grid, "E2 Xoay Phải (CW)", "ENC2_CW", 2)
        self.add_setting(e_grid, "E2 Xoay Trái (CCW)", "ENC2_CCW", 3)
        e_box.setLayout(e_grid)
        self.settings_layout.addWidget(e_box)

        # Nút Save
        save_btn = QPushButton("💾 XUẤT CẤU HÌNH (SAVE TO CONFIG.JSON)")
        save_btn.clicked.connect(self.save_config)
        self.settings_layout.addWidget(save_btn)

        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll, 55)

    def add_setting(self, layout, label_text, config_key, row):
        label = QLabel(label_text)
        combo = QComboBox()

        # Thêm nhóm phím với Header không thể chọn
        for category, keys in HID_KEYS.items():
            combo.addItem(f"--- {category} ---")
            combo.model().item(combo.count()-1).setEnabled(False)  # Header ko chọn dc
            combo.addItems(keys)

        layout.addWidget(label, row, 0)
        layout.addWidget(combo, row, 1)
        self.combos[config_key] = combo

    def load_current_config(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    data = json.load(f)
                    for key, val in data.items():
                        if key in self.combos:
                            index = self.combos[key].findText(val)
                            if index >= 0:
                                self.combos[key].setCurrentIndex(index)
        except:
            pass

    def save_config(self):
        # 1. Thu thập dữ liệu từ giao diện
        config_data = {}
        for key, combo in self.combos.items():
            text = combo.currentText()
            # Bỏ qua các dòng tiêu đề (Header)
            if not text.startswith("--- "):
                config_data[key] = text

        # 2. Mở hộp thoại cho phép người dùng chọn nơi lưu file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu cấu hình Tay cầm",
            "config.json",  # Tên file mặc định
            "JSON Files (*.json);;All Files (*)"
        )

        # Nếu người dùng bấm Cancel (hủy) trong hộp thoại
        if not file_path:
            return

        # 3. Tiến hành lưu file với định dạng chuẩn
        try:
            # Sử dụng indent=2 để xuất ra định dạng JSON 2 dấu cách giống hệt file mẫu của bạn
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)

            QMessageBox.information(
                self,
                "Thành công",
                f"Đã lưu cấu hình thành công vào:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Configurator()
    window.show()
    sys.exit(app.exec())
