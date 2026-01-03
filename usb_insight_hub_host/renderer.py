from usb_insight_hub_host.hub import USBInfoParams, USBInfoParamsType, USBInfoRequest, USBInsightHub
from usb_insight_hub_host.port import USBInsightHubPort
from usb_insight_hub_host.screens.base import Screen

from datetime import datetime, timedelta

EMPTY_PORT_INFO = USBInfoParams(
    dev_name_1="",
    dev_name_2="",
    usb_type="2",
)

PORT_CYCLE_TIME = timedelta(seconds=1)

class USBRenderer:
    screens: list[Screen]
    screen_offset: int
    screen_last_cycle: datetime
    hub: USBInsightHub
    ports: list[USBInsightHubPort]

    def __init__(self, hub: USBInsightHub, screens: list[Screen]):
        self.screens = sorted(screens, key=lambda s: s.priority, reverse=True)
        self.hub = hub
        self.screen_offset = 0
        self.screen_last_cycle = datetime.now()

        ports: list[USBInsightHubPort] = []
        for port_idx in range(1, self.hub.num_ports + 1):
            ports.append(USBInsightHubPort(hub, port_idx))
        self.ports = ports

    def next_cycle(self) -> None:
        self.screen_offset += 1
        self.screen_last_cycle = datetime.now()

    def render(self) -> USBInfoParamsType | None:
        if datetime.now() - self.screen_last_cycle >= PORT_CYCLE_TIME:
            self.next_cycle()
        usb_info_request = USBInfoRequest(
            params={port.idx: self._render_port(port) for port in self.ports}
        )
        _ = self.hub.send_request(usb_info_request)

    def _render_port(self, port: USBInsightHubPort) -> USBInfoParamsType | None:
        infos = port.get_infos()
        if not infos:
            return EMPTY_PORT_INFO
    
        current_priority = None
        valid_screens: list[Screen] = []
        for screen in self.screens:
            # The list is sorted, this relies on that here
            if current_priority is not None and screen.priority != current_priority:
                break

            if not screen.valid_for(infos):
                continue

            current_priority = screen.priority
            valid_screens.append(screen)

        if not valid_screens:
            return EMPTY_PORT_INFO

        screen = valid_screens[self.screen_offset % len(valid_screens)]

        result = screen.display(infos)
        if result is None:
            print(f"WARNING: None render for port {port.idx} by {screen.ID}!")
        return result
