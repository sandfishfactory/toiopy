from toiopy.data import (
    Buffer,
    ButtonType,
    ButtonTypeData
)


class ButtonSpec:

    def parse(self, buffer: Buffer) -> ButtonType:

        if buffer.bytelength < 2:
            raise Exception("parse error")

        id = buffer.read_uint8(0)

        if id != 1:
            raise Exception("parse error")

        pressed = buffer.read_uint8(1) != 0
        data = ButtonTypeData(id, pressed)
        return ButtonType(buffer, data, 'button:press')
