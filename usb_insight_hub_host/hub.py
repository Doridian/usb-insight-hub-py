from serial import Serial
from dataclasses import dataclass
from typing import Any, Literal, override
import json
from os import readlink, listdir
from os.path import basename, exists, join as path_join
from usb_insight_hub_host.usbutil import get_container_id, USB_VERSION_TYPE
from usb_insight_hub_host.devinfo import DEV_ROOT


@dataclass(frozen=True, eq=True, kw_only=True)
class RequestPacket:
    action: str
    params: list[Any] | dict[Any, Any]

    def to_serializable(self) -> Any:
        return self.__dict__


@dataclass(frozen=True, eq=True, kw_only=True)
class USBInfoParams:
    dev_name_1: str
    dev_name_2: str
    usb_type: USB_VERSION_TYPE

    def to_serializable(self) -> Any:
        if self.dev_name_1 == "" and self.dev_name_2 == "":
            return {
                "numDev": "0",
                "usbType": "",
            }
        return {
            "Dev1_name": self.dev_name_1,
            "Dev2_name": self.dev_name_2,
            "numDev": "1" if self.dev_name_2 == "" else "2",
            "usbType": self.usb_type,
        }


@dataclass(frozen=True, eq=True, kw_only=True)
class USBInfoParamsAdvText:
    txt: str
    align: Literal["center", "left", "right"]
    color: Literal[
        "WHITE", "YELLOW", "ORANGE", "BLACK", "RED", "DARKGREY", "CYAN", "BLUE", "GREEN"
    ]

    def to_serializable(self) -> Any:
        res: dict[str, Any] = {
            "txt": self.txt,
        }
        if self.align != "center":
            res["align"] = self.align
        if self.color != "WHITE":
            res["color"] = self.color
        return res


@dataclass(frozen=True, eq=True, kw_only=True)
class USBInfoParamsAdv:
    lines: list[USBInfoParamsAdvText]
    usb_type: USB_VERSION_TYPE

    def to_serializable(self) -> Any:
        if not self.lines:
            return {
                "numDev": "0",
                "usbType": "",
            }

        if len(self.lines) > 3:
            raise ValueError("USBInfoParamsAdv can have at most 3 lines")

        return {
            "Dev1_name": {
                f"T{i + 1}": line.to_serializable() for i, line in enumerate(self.lines)
            },
            "numDev": "10",
            "usbType": self.usb_type,
        }


@dataclass(frozen=True, eq=True, kw_only=True)
class USBInfoParamsImage:
    image: bytes
    usb_type: USB_VERSION_TYPE

    def to_serializable(self) -> Any:
        if not self.image:
            return {
                "numDev": "0",
                "usbType": "",
            }

        return {
            "numDev": "11",
            "usbType": self.usb_type,
        }

USBInfoParamsType = USBInfoParams | USBInfoParamsAdv | USBInfoParamsImage

@dataclass(frozen=True, eq=True, kw_only=True)
class USBInfoRequest(RequestPacket):
    action: Literal["set"] = "set"
    params: dict[int, USBInfoParamsType | None]

    @override
    def to_serializable(self) -> Any:
        params_dict = {
            f"CH{ch}": param.to_serializable()
            for ch, param in self.params.items()
            if param is not None
        }
        return {"action": self.action, "params": params_dict}


@dataclass(frozen=True, eq=True, kw_only=True)
class ResponsePacket:
    status: str
    data: list[Any] | dict[Any, Any]


class USBHubError(Exception):
    raw: str
    response_packet: ResponsePacket

    def __init__(self, raw: str, response_packet: ResponsePacket):
        super().__init__(f"Error response from USB Insight Hub: {raw}")
        self.raw = raw
        self.response_packet = response_packet


class USBInsightHub:
    subdevs: list[str]
    num_ports: int

    IMAGE_W = 226
    IMAGE_H = 90
    IMAGE_BPP = 1

    def __init__(self, port: str):
        super().__init__()
        # Search for the correct hub for the given serial port
        port_real = basename(readlink(port))
        usb_dev_1 = None
        for usb_dev_new in listdir(DEV_ROOT):
            if usb_dev_new.startswith("usb"):
                continue
            if not usb_dev_new.endswith(".4:1.0"):
                continue
            if not exists(path_join(DEV_ROOT, usb_dev_new, "tty", port_real)):
                continue

            usb_dev_1 = usb_dev_new.removesuffix(".4:1.0")
            break

        if usb_dev_1 is None:
            raise ValueError(f"Could not find USB2 device for port {port}")

        # Search for the corresponding USB3 device
        usb_dev_2 = None
        usb_dev_1_container_id = get_container_id(usb_dev_1)
        if not usb_dev_1_container_id:
            raise ValueError(f"USB2 device {usb_dev_1} has no container ID")
        for usb_dev_new in listdir(DEV_ROOT):
            if usb_dev_new.startswith("usb"):
                continue
            if not exists(path_join(DEV_ROOT, usb_dev_new, "bos_descriptors")):
                continue
            usb_dev_2_container_id = get_container_id(usb_dev_new)
            if (
                usb_dev_2_container_id == usb_dev_1_container_id
                and usb_dev_new != usb_dev_1
            ):
                if usb_dev_2 is not None:
                    raise ValueError(
                        f"Multiple USB3 devices found for port {port} with container ID {usb_dev_1_container_id}, USB devices: {usb_dev_1}, {usb_dev_2}, {usb_dev_new}"
                    )
                usb_dev_2 = usb_dev_new

        if usb_dev_2 is None:
            raise ValueError(
                f"Could not find USB3 device for port {port}, USB2 device found: {usb_dev_1}"
            )

        self.subdevs = [usb_dev_1, usb_dev_2]

        self.num_ports = 3
        self.ser = Serial(port, baudrate=115200, timeout=1, dsrdtr=True)

    def close(self):
        self.ser.close()

    def send_image(self, index: int, img: USBInfoParamsImage) -> None:
        if len(img.image) != self.IMAGE_W * self.IMAGE_H * self.IMAGE_BPP:
            raise ValueError(
                f"Image data must be exactly {self.IMAGE_W * self.IMAGE_H * self.IMAGE_BPP} bytes"
            )
        _ = self.ser.write(bytes([index]) + img.image)
        recv = self.ser.readline().decode("utf-8").rstrip()
        if str(index) != recv:
            raise ValueError(f"Invalid response received from USB Insight Hub after sending image: {recv}")

    def send_request(self, request: RequestPacket) -> ResponsePacket:
        _ = self.ser.write(json.dumps(request.to_serializable()).encode("utf-8") + b"\n")
        line = self.ser.readline().decode("utf-8").rstrip()
        if line:
            response_dict = json.loads(line)
            resp = ResponsePacket(**response_dict)
            if resp.status != "ok":
                raise USBHubError(line, resp)
            return resp
        else:
            raise TimeoutError("No response received from USB Insight Hub")
