from dataclasses import dataclass
from os.path import join as path_join
from os import SEEK_CUR
from io import BufferedReader
from typing import Literal
from usb_insight_hub_host.devinfo import DEV_ROOT

HUB_VID = 0x303A
HUB_PID = 0x1001
CONTAINER_CAPABILITY_TYPE = 4
USB_VERSION_TYPE = Literal["2", "3"]


@dataclass(frozen=True, eq=True, kw_only=True)
class BOSCapability:
    capability_type: int
    data: bytes


class LimitedReader:
    io: BufferedReader
    cur_pos: int
    total_len: int

    def __init__(self, io: BufferedReader):
        super().__init__()
        self.io = io
        self.cur_pos = 0
        self.total_len = -1

    def read(self, size: int) -> bytes:
        if size <= 0:
            return b""

        if self.total_len > -1 and size > self.total_len - self.cur_pos:
            raise EOFError("End of LimitedReader reached")

        data = self.io.read(size)
        if len(data) < size:
            raise EOFError("End of LimitedReader underlying IO reached")

        self.cur_pos += size
        return data

    def one(self) -> int:
        return self.read(1)[0]

    def skip(self, size: int) -> None:
        if size <= 0:
            return

        if self.total_len > -1 and size > self.total_len - self.cur_pos:
            raise EOFError("End of LimitedReader reached")

        _ = self.io.seek(size, SEEK_CUR)
        self.cur_pos += size


def get_container_id(dev: str) -> str | None:
    caps = decode_bos_capabilities(dev)
    if CONTAINER_CAPABILITY_TYPE not in caps:
        return None
    return caps[CONTAINER_CAPABILITY_TYPE].hex()


def decode_bos_capabilities(dev: str) -> dict[int, bytes]:
    capabilities: dict[int, bytes] = {}

    with open(path_join(DEV_ROOT, dev, "bos_descriptors"), "rb") as _file:
        rdr = LimitedReader(_file)
        desc_len = rdr.one()
        if desc_len < 5:
            raise ValueError(f"BOS root descriptor too short {desc_len} < 5")

        desc_type = rdr.one()
        if desc_type != 0x0F:
            raise ValueError(f"Invalid BOS root descriptor type: {desc_type}")

        rdr.total_len = int.from_bytes(rdr.read(2), "little")

        total_caps = rdr.one()

        if desc_len > 5:
            rdr.skip(desc_len - 5)

        for _ in range(total_caps):
            cap_len = rdr.one()
            if cap_len < 3:
                raise ValueError(f"BOS capability descriptor too short: {cap_len} < 3")

            cap_desc_type = rdr.one()
            if cap_desc_type != 0x10:
                raise ValueError(
                    f"Invalid BOS capability descriptor type: {cap_desc_type}"
                )
            cap_type = rdr.one()
            cap_data = rdr.read(cap_len - 3)

            capabilities[cap_type] = cap_data

    return capabilities
