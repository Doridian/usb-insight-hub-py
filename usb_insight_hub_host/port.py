from usb_insight_hub_host.hub import USBInsightHub
from functools import cached_property
from usb_insight_hub_host.devinfo import DevInfo
from usb_insight_hub_host.usbutil import USB_VERSION_TYPE

class USBInfo(DevInfo):
    port_index: int

    @cached_property
    def vid(self) -> int:
        return self.read_int_subfile("idVendor", base=16, default=0)

    @cached_property
    def pid(self) -> int:
        return self.read_int_subfile("idProduct", base=16, default=0)

    @cached_property
    def speed(self) -> int:
        return self.read_int_subfile("speed", default=0)
    
    def version(self) -> USB_VERSION_TYPE:
        return "3" if self.speed >= 5000 else "2"

class USBInsightHubPort:
    hub: USBInsightHub
    idx: int
    subdevs: list[str]

    def __init__(self, hub: USBInsightHub, idx: int):
        self.hub = hub
        self.idx = idx
        self.subdevs = [f"{dev}.{idx}" for dev in hub.subdevs]

    def _get_info_generic(self, dev: str) -> USBInfo | None:
        if not dev:
            return None
        info = USBInfo(dev)
        if info.vid and info.pid:
            info.port_index = self.idx
            return info
        return None

    def get_infos(self) -> list[USBInfo]:
        infos: list[USBInfo] = []

        for subdev in self.subdevs:
            info = self._get_info_generic(subdev)
            if info is not None:
                infos.append(info)

        return infos
