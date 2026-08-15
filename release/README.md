# 📦 Standalone Releases & Pre-built Executable

Ứng dụng **Controller Configurator Pro** được đóng gói sẵn thành file thực thi .exe độc lập dành cho Windows.

## 🚀 Tải về nhanh
- Bản build sẵn: Controller Configurator Pro.exe (chạy trực tiếp không cần cài Python hay thư viện).
- Vui lòng kiểm tra mục **[Releases](../../releases)** trên GitHub để tải phiên bản mới nhất.

## 🛠️ Tự đóng gói từ mã nguồn (Build with PyInstaller)
Nếu bạn muốn tự compile file .exe từ mã nguồn Python:

`ash
# 1. Di chuyển vào thư mục configurator-gui
cd configurator-gui

# 2. Cài đặt PyInstaller
pip install pyinstaller pyqt6

# 3. Đóng gói ứng dụng thành file exe đơn nhất
pyinstaller --noconsole --onefile --name Controller Configurator Pro main.py
`
File thực thi sau khi build sẽ nằm trong thư mục dist/.
