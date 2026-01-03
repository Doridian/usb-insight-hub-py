from usb_insight_hub_host.hub import USBInsightHub, PortStrType
from functools import cached_property
from usb_insight_hub_host.devinfo import DevInfo

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
    port: PortStrType
    subdevs: list[str]

    # HOW TO FIND PORT (separate for USB2 and USB3!):
    # Find device in /sys/bus/usb/devices with idVendor 303a and idProduct 100a
    # Assume the serial device is at /sys/bus/usb/devices/9-1.1.4/ (will have /sys/bus/usb/devices/9-1.1.4/9-1.1.4:1.0/tty/ttyACM#)
    # Hub is located at /sys/bus/usb/devices/9-1.1/
    # Ports are located at /sys/bus/usb/devices/9-1.1.[123]/ respectively

    # You can match hubs with bos_descriptors, deserialize as per BOS_DESCRITOR.md

    def __init__(self, hub: USBInsightHub, port: PortStrType):
        self.hub = hub
        self.port = port
        # TODO: Find self.subdevs

    def get_info(self) -> USBInfo | None:
        for subdev in self.subdevs:
            info = USBInfo(subdev)
            if info.vid and info.pid:
                return info

        return None
