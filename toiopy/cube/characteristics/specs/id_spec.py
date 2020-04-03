from toiopy.data import (
    Buffer,
    BatteryType,
    BatteryTypeData,
    ButtonType,
    ButtonTypeData,
    StandardId,
    PositionIdType,
    PositionIdInfo,
    StandardIdType,
    StandardIdInfo,
    IdMissedType,
)


class IdSpec:

    def parse(self, buffer: Buffer) -> DataType:

        if buffer.bytelength < 1:
            raise Exception("parse error")

        data_type = buffer.read_uint8(0)

        if data_type == 1:
            if buffer.bytelength < 11:
                raise Exception("parse error")
            else:
                data = PositionIdInfo(
                    buffer.read_uint16le(1),
                    buffer.read_uint16le(3),
                    buffer.read_uint16le(5),
                    buffer.read_uint16le(7),
                    buffer.read_uint16le(9)
                )
                return PositionIdType(buffer, data, 'id:position-id')
        elif data_type == 2:
            if buffer.bytelength < 7:
                raise Exception("parse error")
            else:
                data = StandardIdInfo(
                    StandardId(buffer.read_uint32le(1)),
                    buffer.read_uint16le(5)
                )
                return StandardIdType(buffer, data, 'id:standard-id')
        elif data_type == 3:
            return IdMissedType(buffer, 'id:position-id-missed')

        elif data_type == 2:
            return IdMissedType(buffer, data, 'id:standard-id-missed')
        else:
            raise Exception("parse error")
