from typing import override
from usb_insight_hub_host.screens.base import SimpleScreen
from usb_insight_hub_host.hub import USBInfoParamsType, USBInfoParamsImage
from usb_insight_hub_host.port import USBInfo
from usb_insight_hub_host.usbutil import USB_VERSION_TYPE


class ImageScreen(SimpleScreen):
    ID = "image"
    DEFAULT_PRIORITY = 10

    @override
    def display_single(
        self, info: USBInfo, max_version: USB_VERSION_TYPE
    ) -> USBInfoParamsType | None:
        data = b""
        for row in range(90):
            for col in range(226):
                val = col % 0xFF
                data += val.to_bytes(1, "little")
        return USBInfoParamsImage(
            image=data, # Rainbows
            usb_type=max_version,
        )
