from abc import ABC, abstractmethod
from usb_insight_hub_host.hub import USBInsightHubPort, USBInfoParams

class Screen(ABC):
    priority: int
    name: str

    def __init__(self, name: str, priority: int) -> None:
        self.name = name
        self.priority = priority

    @abstractmethod
    def display(self, port: USBInsightHubPort) -> USBInfoParams:
        pass

    @abstractmethod
    def valid_for(self, port: USBInsightHubPort) -> bool:
        pass
