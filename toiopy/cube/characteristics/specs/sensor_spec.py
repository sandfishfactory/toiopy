from toiopy.data import (
    Buffer,
    SensorType,
    SensorTypeData
)


class SensorSpec:

    def parse(self, buffer: Buffer) -> SensorType:

        if buffer.bytelength < 3:
            raise Exception("parse error")

        type_data = buffer.read_uint8(0)

        if type_data != 1:
            raise Exception("parse error")

        is_sloped = buffer.read_uint8(1) == 0
        is_collision_detected = buffer.read_uint8(2) == 1
        is_double_tapped = buffer.read_uint8(3) == 1
        orientation = buffer.read_uint8(4)

        data = SensorTypeData(
            is_sloped, is_collision_detected, is_double_tapped, orientation
        )

        return SensorType(buffer, data, 'sensor:detection')
