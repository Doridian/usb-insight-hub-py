from argparse import ArgumentParser
from time import sleep
from datetime import timedelta

from usb_insight_hub_host.hub import USBInsightHub, USBSetPortRequest
from usb_insight_hub_host.renderer import USBRenderer
from usb_insight_hub_host.screens import ALL_SCREEN_CONSTRUCTORS


def main():
    parser = ArgumentParser(description="USB Insight Hub Host Application")
    _ = parser.add_argument(
        "--port", "-p",
        required=True,
        help="Serial port to connect to the USB Insight Hub (e.g., /dev/ttyUSB0)",
    )
    _ = parser.add_argument("--cycle-time-seconds", "-t", type=int, default=5, help="Screen cycle time in seconds (default: 5)")
    args = parser.parse_args()

    hub = USBInsightHub(args.port)
    _ = hub.send_request(USBSetPortRequest(params={"wifi_enabled": "false"}))

    renderer = USBRenderer(
        hub=hub,
        screens=[screen() for screen in ALL_SCREEN_CONSTRUCTORS],
        cycle_time=timedelta(seconds=args.cycle_time_seconds),
    )

    while True:
        print("<render>")
        renderer.render()
        print("</render>")
        sleep(1)


if __name__ == "__main__":
    main()
