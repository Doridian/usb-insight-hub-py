from serial import Serial
from dataclasses import dataclass
from typing import Any, Literal
import json

@dataclass(frozen=True, eq=True, kw_only=True)
class RequestPacket:
    action: str
    params: list[Any] | dict[Any, Any]

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

@dataclass(frozen=True, eq=True, kw_only=True)
class USBInfoParams:
    Dev1_name: str
    Dev2_name: str
    numDev: Literal["1", "2"]
    usbType: Literal["2", "3"]

@dataclass(frozen=True, eq=True, kw_only=True)
class USBInfoRequest(RequestPacket):
    action: Literal["set"] = "set"
    params: dict[Literal["CH1", "CH2", "CH3"], USBInfoParams]

    def to_json(self) -> str:
        params_dict = {ch: param.__dict__ for ch, param in self.params.items()}
        return json.dumps({
            "action": self.action,
            "params": params_dict
        })

@dataclass(frozen=True, eq=True, kw_only=True)
class ResponsePacket:
    status: str
    data: list[Any] | dict[Any, Any]

class USBInsightHub:
    def __init__(self, port: str):
        self.ser = Serial(port, baudrate=115200, timeout=1, dsrdtr=True)

    def close(self):
        self.ser.close()

    def send_request(self, request: RequestPacket) -> ResponsePacket:
        self.ser.write(request.to_json().encode('utf-8') + b'\n')
        line = self.ser.readline().decode('utf-8').rstrip()
        if line:
            response_dict = json.loads(line)
            return ResponsePacket(**response_dict)
        else:
            raise TimeoutError("No response received from USB Insight Hub")
