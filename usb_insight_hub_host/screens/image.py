from typing import override
from usb_insight_hub_host.screens.base import SimpleScreen
from usb_insight_hub_host.hub import USBPortInfoType, USBPortInfoImage
from usb_insight_hub_host.port import USBInfo
from usb_insight_hub_host.usbutil import USB_VERSION_TYPE


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
                data += col.to_bytes(2, "little")
        return USBPortInfoImage(
            image=data, # Rainbows
            bpp=16,
            usb_type=max_version,
        )
