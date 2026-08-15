import usb_hid

# Kích hoạt chuẩn Bàn phím, Chuột và Điều khiển Âm lượng (Consumer Control)
usb_hid.enable(
    (usb_hid.Device.KEYBOARD,
     usb_hid.Device.MOUSE,
     usb_hid.Device.CONSUMER_CONTROL)
)