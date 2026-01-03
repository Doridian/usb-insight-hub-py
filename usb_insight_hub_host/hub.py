from serial import Serial
from dataclasses import dataclass
from typing import Any, Literal
import json

_port_str_type = Literal["CH1", "CH2", "CH3"]

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
    params: dict[_port_str_type, USBInfoParams]

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
    def __init__(self, port: str):
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

class USBInsightHubPort:
    hub: USBInsightHub
    port: _port_str_type

    def __init__(self, hub: USBInsightHub, port: _port_str_type):
        self.hub = hub
        self.port = port
