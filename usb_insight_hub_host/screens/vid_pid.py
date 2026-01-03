from usb_insight_hub_host.screens.base import SimpleScreen
from usb_insight_hub_host.hub import USBInfoParamsType, USBInfoParams
from usb_insight_hub_host.port import USBInfo, USBInsightHubPort
from usb_insight_hub_host.usbutil import USB_VERSION_TYPE

class VIDPIDScreen(SimpleScreen):
    ID = "vid_pid"
    VID_PREFIX = "V"
    PID_PREFIX = "P"
    DEFAULT_PRIORITY = 1

    def display_single(self, info: USBInfo, max_version: USB_VERSION_TYPE) -> USBInfoParamsType | None:
        return USBInfoParams(
            dev_name_1=f"{self.VID_PREFIX} {info.vid:04x}",
            dev_name_2=f"{self.PID_PREFIX} {info.pid:04x}",
            usb_type=max_version,
        )

class VIDPID3Screen(VIDPIDScreen):
    ID = "vid_pid_3"
    USB_VERSION: USB_VERSION_TYPE = "3"
    VID_PREFIX = "V3"
    PID_PREFIX = "P3"
    DEFAULT_PRIORITY = 2

    def select_usb_info(self, infos: list[USBInfo]) -> USBInfo | None:
        return self.usb_info_by_version(infos, self.USB_VERSION)

    def valid_for(self, info: list[USBInfo]) -> bool:
        if len(info) < 2:
            return False
        selected = self.select_usb_info(info)
        return selected is not None

class VIDPID2Screen(VIDPID3Screen):
    ID = "vid_pid_2"
    USB_VERSION = "2"
    USB_VERSION = "2"
    VID_PREFIX = "V2"
    PID_PREFIX = "P2"
    DEFAULT_PRIORITY = 2
