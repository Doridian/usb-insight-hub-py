from usb_insight_hub_host.screen import Screen
from usb_insight_hub_host.hub import USBInfoParams
from usb_insight_hub_host.port import USBInfo, USBInsightHubPort

class VIDPIDScreen(Screen):
    def __init__(self) -> None:
        super().__init__(name="VID/PID Screen", priority=1)

    def display(self, info: USBInfo, port: USBInsightHubPort) -> USBInfoParams | None:
        return USBInfoParams(
            dev_name_1=f"0x{info.vid:04x}",
            dev_name_2=f"0x{info.pid:04x}",
            usb_type=info.version,
        )
