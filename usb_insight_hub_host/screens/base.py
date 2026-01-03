from abc import ABC, abstractmethod
from usb_insight_hub_host.hub import USBInfoParamsType
from usb_insight_hub_host.port import USBInfo
from usb_insight_hub_host.usbutil import USB_VERSION_TYPE


class Screen(ABC):
    priority: int
    ID: str
    DEFAULT_PRIORITY: int = 0

    def __init__(self, priority: int | None = None) -> None:
        self.priority = self.DEFAULT_PRIORITY if priority is None else priority

    @abstractmethod
    def display(self, info: list[USBInfo]) -> USBInfoParamsType | None:
        pass

    def valid_for(self, info: list[USBInfo]) -> bool:
        return True


class SimpleScreen(Screen):
    # If we have two, prefer the one with the higher speed
    # This is only ever true for hubs, really
    def _select_usb_info_best_speed(self, infos: list[USBInfo]) -> USBInfo | None:
        best_speed = 0
        best_info = None
        for info in infos:
            speed = info.speed
            if speed > best_speed:
                best_speed = speed
                best_info = info
        return best_info

    def select_usb_info(self, infos: list[USBInfo]) -> USBInfo | None:
        return self._select_usb_info_best_speed(infos)

    def usb_info_by_version(
        self, infos: list[USBInfo], version: USB_VERSION_TYPE
    ) -> USBInfo | None:
        for info in infos:
            if info.version() == version:
                return info
        return None

    def display(self, info: list[USBInfo]) -> USBInfoParamsType | None:
        best_speed = self._select_usb_info_best_speed(info)
        selected = self.select_usb_info(info)
        if selected is None or best_speed is None:
            return None
        return self.display_single(selected, best_speed.version())

    def valid_for(self, info: list[USBInfo]) -> bool:
        selected = self.select_usb_info(info)
        if selected is None:
            return False
        return self.valid_for_single(selected)

    @abstractmethod
    def display_single(
        self, info: USBInfo, max_version: USB_VERSION_TYPE
    ) -> USBInfoParamsType | None:
        pass

    def valid_for_single(self, info: USBInfo) -> bool:
        return True
