from usb_insight_hub_host.screen import Screen
from usb_insight_hub_host.hub import USBInfoParams
from usb_insight_hub_host.port import USBInsightHubPort

class VIDPIDScreen(Screen):
    def __init__(self) -> None:
        super().__init__(name="VID/PID Screen", priority=10)

    def display(self, port: USBInsightHubPort) -> USBInfoParams:
        return USBInfoParams(
            dev_name_1="0xTODO",
            dev_name_2="0xTODO",
            usb_type="3"
        )

    def valid_for(self, port: USBInsightHubPort) -> bool:
        return True
