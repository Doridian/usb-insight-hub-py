from usb_insight_hub_host.hub import USBInfoParams
from usb_insight_hub_host.port import USBInsightHubPort

from usb_insight_hub_host.screens.vid_pid import VIDPIDScreen

class USBPortRenderer:
    def __init__(self, port: USBInsightHubPort):
        self.port = port

    def render(self) -> USBInfoParams:
        return VIDPIDScreen().display(self.port)
