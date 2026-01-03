from usb_insight_hub_host.hub import USBInsightHub, PortStrType

class USBInsightHubPort:
    hub: USBInsightHub
    port: PortStrType

    def __init__(self, hub: USBInsightHub, port: PortStrType):
        self.hub = hub
        self.port = port
