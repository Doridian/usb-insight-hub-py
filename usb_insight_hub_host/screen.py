from abc import ABC, abstractmethod
from usb_insight_hub_host.hub import USBInfoParamsType
from usb_insight_hub_host.port import USBInfo, USBInsightHubPort

class Screen(ABC):
    priority: int
    ID: str

    def __init__(self, priority: int) -> None:
        self.priority = priority

    @abstractmethod
    def display(self, info: USBInfo, port: USBInsightHubPort) -> USBInfoParamsType | None:
        pass

    def valid_for(self, info: USBInfo, port: USBInsightHubPort) -> bool:
        return True
