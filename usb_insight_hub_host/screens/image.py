from typing import override
from usb_insight_hub_host.screens.base import SimpleScreen
from usb_insight_hub_host.hub import USBPortInfoType, USBPortInfoImage
from usb_insight_hub_host.port import USBInfo
from usb_insight_hub_host.usbutil import USB_VERSION_TYPE

def hsv_to_rgb(h:float, s:float, v:float) -> tuple[float, float, float]:
    if not s:
        return (v, v, v)

    if h == 1.0:
        h = 0.0

    i = int(h*6.0)
    f = h*6.0 - i

    w = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))

    if i==0: return (v, t, w)
    elif i==1: return (q, v, w)
    elif i==2: return (w, v, t)
    elif i==3: return (w, q, v)
    elif i==4: return (t, w, v)
    elif i==5: return (v, w, q)
    else: raise ValueError("i value out of range")

def hsv_to_rgb565(h:float, s:float, v:float) -> int:
    r, g, b = hsv_to_rgb(h, s, v)
    r5 = int(r * 31) & 0x1F
    g6 = int(g * 63) & 0x3F
    b5 = int(b * 31) & 0x1F
    return (r5 << 11) | (g6 << 5) | b5

class ImageScreen(SimpleScreen):
    ID = "image"
    DEFAULT_PRIORITY = 10

    @override
    def display_single(
        self, info: USBInfo, max_version: USB_VERSION_TYPE
    ) -> USBPortInfoType | None:
        data = b""
        for _ in range(90):
            for col in range(226):
                v = hsv_to_rgb565(h=((col + info.port_index * 60) % 226) / 226.0, s=1.0, v=1.0)
                data += v.to_bytes(2, "big")
        return USBPortInfoImage(
            image=data, # Rainbows
            bpp=16,
            usb_type=max_version,
        )
