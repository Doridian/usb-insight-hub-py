from serial import Serial
from dataclasses import dataclass
from typing import Any, Literal
import json
from os import readlink, listdir
from os.path import basename, exists, join as path_join
from usb_insight_hub_host.usbutil import DEV_ROOT, get_container_id

PortStrType = Literal["CH1", "CH2", "CH3"]

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
    usb_type: Literal["2", "3"]

    def to_serializable(self) -> Any:
        return {
            "Dev1_name": self.dev_name_1,
            "Dev2_name": self.dev_name_2,
            "numDev": "1" if self.dev_name_2 == "" else "2",
            "usbType": self.usb_type
        }

@dataclass(frozen=True, eq=True, kw_only=True)
class USBInfoRequest(RequestPacket):
    action: Literal["set"] = "set"
    params: dict[PortStrType, USBInfoParams]

    def to_serializable(self) -> Any:
        params_dict = {ch: param.to_serializable() for ch, param in self.params.items()}
        return {
            "action": self.action,
            "params": params_dict
        }

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
    usb2_dev: str
    usb3_dev: str

    def __init__(self, port: str):
        # Search for the correct hub for the given serial port
        port_real = basename(readlink(port))
        usb2_dev = None
        for usb_dev in listdir(DEV_ROOT):
            if usb_dev.startswith("usb"):
                continue
            if not usb_dev.endswith(".4:1.0"):
                continue
            if not exists(path_join(DEV_ROOT, usb_dev, "tty", port_real)):
                continue

            usb2_dev = usb_dev.removesuffix(".4:1.0")
            break

        if usb2_dev is None:
            raise ValueError(f"Could not find USB2 device for port {port}")
        self.usb2_dev = usb2_dev

        # Search for the corresponding USB3 device
        usb3_dev = None
        usb2_container_id = get_container_id(usb2_dev)
        if not usb2_container_id:
            raise ValueError(f"USB2 device {usb2_dev} has no container ID")
        for usb_dev in listdir(DEV_ROOT):
            if usb_dev.startswith("usb"):
                continue
            if not exists(path_join(DEV_ROOT, usb_dev, "bos_descriptors")):
                continue
            usb3_container_id = get_container_id(usb_dev)
            if usb3_container_id == usb2_container_id and usb_dev != usb2_dev:
                if usb3_dev is not None:
                    raise ValueError(f"Multiple USB3 devices found for port {port} with container ID {usb2_container_id}, USB2 device: {usb2_dev}, USB3 candidates: {usb3_dev}, {usb_dev}")
                usb3_dev = usb_dev

        if usb3_dev is None:
            raise ValueError(f"Could not find USB3 device for port {port}, USB2 device found: {usb2_dev}")
        self.usb3_dev = usb3_dev

        self.ser = Serial(port, baudrate=115200, timeout=1, dsrdtr=True)

    def close(self):
        self.ser.close()

    def send_request(self, request: RequestPacket) -> ResponsePacket:
        self.ser.write(json.dumps(request.to_serializable()).encode('utf-8') + b'\n')
        line = self.ser.readline().decode('utf-8').rstrip()
        if line:
            response_dict = json.loads(line)
            resp = ResponsePacket(**response_dict)
            if resp.status != "ok":
                raise USBHubError(line, resp)
            return resp
        else:
            raise TimeoutError("No response received from USB Insight Hub")
