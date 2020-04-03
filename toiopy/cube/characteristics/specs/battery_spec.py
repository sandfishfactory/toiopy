from toiopy.data import (
    Buffer,
    BatteryType,
    BatteryTypeData,
)


class BatterySpec:

    def parse(self, buffer: Buffer) -> BatteryType:

        if buffer.bytelength < 1:
            raise Exception("parse error")

        level = buffer.read_uint8(0)
        data = BatteryTypeData(level)
        return BatteryType(buffer, data, 'battery:battery')
