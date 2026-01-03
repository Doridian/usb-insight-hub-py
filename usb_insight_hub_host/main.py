from argparse import ArgumentParser
from time import sleep

from usb_insight_hub_host.hub import USBInsightHub, USBInfoRequest, USBInfoParams

def main():
    parser = ArgumentParser(description="USB Insight Hub Host Application")
    parser.add_argument("--port", required=True, help="Serial port to connect to the USB Insight Hub (e.g., /dev/ttyUSB0)")
    args = parser.parse_args()
    
    hub = USBInsightHub(args.port)
    try:
        usb_info_request = USBInfoRequest(
            params={
                "CH1": USBInfoParams(dev_name_1="DeviceA", dev_name_2="DeviceB", usb_type="3"),
                "CH2": USBInfoParams(dev_name_1="DeviceC", dev_name_2="", usb_type="2")
            }
        )
        response = hub.send_request(usb_info_request)
        print("Response:", response)
    finally:
        hub.close()

if __name__ == "__main__":
    main()
