from usb_insight_hub_host.screen import Screen
from usb_insight_hub_host.hub import USBInfoParamsType, USBInfoParams
from usb_insight_hub_host.port import USBInfo, USBInsightHubPort

class VIDPIDScreen(Screen):
    ID = "vid_pid"

    def __init__(self) -> None:
        super().__init__(priority=1)

    def display(self, info: USBInfo, port: USBInsightHubPort) -> USBInfoParamsType | None:
        return USBInfoParams(
            dev_name_1=f"V {info.vid:04x}",
            dev_name_2=f"P {info.pid:04x}",
            usb_type=info.version,
        )
