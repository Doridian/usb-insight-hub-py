from argparse import ArgumentParser
from time import sleep

from usb_insight_hub_host.hub import USBInsightHub
from usb_insight_hub_host.renderer import USBRenderer
from usb_insight_hub_host.screen import Screen
from usb_insight_hub_host.screens.vid_pid import VIDPIDScreen

def main():
    parser = ArgumentParser(description="USB Insight Hub Host Application")
    parser.add_argument("--port", required=True, help="Serial port to connect to the USB Insight Hub (e.g., /dev/ttyUSB0)")
    args = parser.parse_args()
    
    hub = USBInsightHub(args.port)
    screens: list[Screen] = [VIDPIDScreen()]
    renderer = USBRenderer(hub, screens)

    while True:
        renderer.render()
        sleep(1)

if __name__ == "__main__":
    main()
