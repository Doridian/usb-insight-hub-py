from usb_insight_hub_host.hub import (
    USBPortInfo,
    USBPortInfoImage,
    USBPortInfoType,
    USBSetPortInfoRequest,
    USBInsightHub,
)
from usb_insight_hub_host.port import USBInsightHubPort
from usb_insight_hub_host.screens.base import Screen

from datetime import datetime, timedelta

EMPTY_PORT_INFO = USBPortInfo(
    dev_name_1="",
    dev_name_2="",
    usb_type="2",
)


class USBRenderer:
    screens: list[Screen]
    cycle_index: int
    last_cycle: datetime
    hub: USBInsightHub
    cycle_time: timedelta
    ports: list[USBInsightHubPort]

    def __init__(self, hub: USBInsightHub, screens: list[Screen], cycle_time: timedelta):
        super().__init__()
        self.screens = sorted(screens, key=lambda s: s.priority, reverse=True)
        self.hub = hub
        self.cycle_index = 0
        self.cycle_time = cycle_time
        self.last_cycle = datetime.now()

        ports: list[USBInsightHubPort] = []
        for port_idx in range(1, self.hub.num_ports + 1):
            ports.append(USBInsightHubPort(hub, port_idx))
        self.ports = ports

    def next_cycle(self) -> None:
        self.cycle_index += 1
        self.last_cycle = datetime.now()

    def render(self) -> None:
        if datetime.now() - self.last_cycle >= self.cycle_time:
            self.next_cycle()
        usb_info_request = USBSetPortInfoRequest(
            params={port.idx: self._render_port(port) for port in self.ports}
        )
        _ = self.hub.send_request(usb_info_request)

    def _render_port(self, port: USBInsightHubPort) -> USBPortInfoType | None:
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

        screen = valid_screens[self.cycle_index % len(valid_screens)]

        result = screen.display(infos)
        if result is None:
            print(f"WARNING: None render for port {port.idx} by {screen.ID}!")

        if isinstance(result, USBPortInfoImage):
            self.hub.send_image(port.idx, result)

        return result
