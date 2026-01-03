from usb_insight_hub_host.hub import USBInsightHub, PortIdxType
from functools import cached_property
from usb_insight_hub_host.devinfo import DevInfo
from usb_insight_hub_host.usbutil import USB_VERSION_TYPE

class USBInfo(DevInfo):
    @cached_property
    def vid(self) -> int:
        return self.read_int_subfile("idVendor", base=16, default=0)

    @cached_property
    def pid(self) -> int:
        return self.read_int_subfile("idProduct", base=16, default=0)

    @cached_property
    def speed(self) -> int:
        return self.read_int_subfile("speed", default=0)

class USBInsightHubPort:
    hub: USBInsightHub
    idx: PortIdxType
    _usb2_dev: str
    _usb3_dev: str

    def __init__(self, hub: USBInsightHub, idx: PortIdxType):
        self.hub = hub
        self.idx = idx
        self._usb2_dev = f"{hub.usb2_dev}.{idx}"
        self._usb3_dev = f"{hub.usb3_dev}.{idx}"

    def _get_info_generic(self, dev: str, version: USB_VERSION_TYPE) -> USBInfo | None:
        if not dev:
            return None
        info = USBInfo(dev, version=version)
        if info.vid and info.pid:
            return info
        return None
    
    def get_info_usb2(self) -> USBInfo | None:
        return self._get_info_generic(self._usb2_dev, version="2")
    
    def get_info_usb3(self) -> USBInfo | None:
        return self._get_info_generic(self._usb3_dev, version="3")

    def get_info(self) -> USBInfo | None:
        info = self.get_info_usb3()
        if info is not None:
            return info
        
        return self.get_info_usb2()
