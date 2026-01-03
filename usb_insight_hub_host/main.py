from argparse import ArgumentParser
from time import sleep
from typing import cast

from usb_insight_hub_host.hub import USBInsightHub, USBInfoRequest, PortIdxType
from usb_insight_hub_host.port import USBInsightHubPort
from usb_insight_hub_host.renderer import USBPortRenderer
from usb_insight_hub_host.renderer import USBPortRenderer

def main():
    parser = ArgumentParser(description="USB Insight Hub Host Application")
    parser.add_argument("--port", required=True, help="Serial port to connect to the USB Insight Hub (e.g., /dev/ttyUSB0)")
    args = parser.parse_args()
    
    hub = USBInsightHub(args.port)

    renderers: dict[PortIdxType, USBPortRenderer] = {
        ch: USBPortRenderer(USBInsightHubPort(hub, ch)) for ch in cast(list[PortIdxType], [1, 2, 3])
    }

    while True:
        usb_info_request = USBInfoRequest(
            params={ch: renderer.render() for ch, renderer in renderers.items()}
        )
        _ = hub.send_request(usb_info_request)
        sleep(1)  # Wait for 1 second before sending the next request

if __name__ == "__main__":
    main()
