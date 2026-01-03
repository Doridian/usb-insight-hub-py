from usb_insight_hub_host.hub import USBInfoParams
from usb_insight_hub_host.port import USBInsightHubPort

from usb_insight_hub_host.screen import Screen
from usb_insight_hub_host.screens.vid_pid import VIDPIDScreen

EMPTY_PORT_INFO = USBInfoParams(
    dev_name_1="",
    dev_name_2="",
    usb_type="2",
)

class USBPortRenderer:
    screens: list[Screen]
    def __init__(self, port: USBInsightHubPort):
        self.screens = [VIDPIDScreen()]
        self.port = port

    def render(self) -> USBInfoParams:
        info = self.port.get_info()
        if info is None:
            return EMPTY_PORT_INFO

        for screen in sorted(self.screens, key=lambda s: s.priority, reverse=True):
            if not screen.valid_for(info, self.port):
                continue
            result = screen.display(info, self.port)
            if result is not None:
                return result

        return EMPTY_PORT_INFO
