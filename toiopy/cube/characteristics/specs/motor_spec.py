from typing import List

from toiopy.data import (
    Buffer,
    MotorResponse,
    MotorResponseData,
    MoveType,
    MoveTypeData,
    MoveToTarget,
    MoveToOptions,
    MoveToType,
    MoveToTypeData,
)
from toiopy.cube.util import clamp
from toiopy.cube.tag import createTagHandler


class MotorSpec:

    MAX_SPEED = 115
    NUMBER_OF_TARGETS_PER_OPERATION = 29

    def __init__(self):
        self.__tag = createTagHandler()

    def parse(self, buffer: Buffer) -> MotorResponse:

        if buffer.bytelength != 3:
            raise Exception("parse error")

        type_data = buffer.readUInt8(0)

        if type_data == 0x83 or type_data == 0x84:
            data = MotorResponseData(
                buffer.read_uint8(1), buffer.read_uint8(2)
            )
            return MotorResponse(buffer, data)
        else:
            raise Exception("parse error")

    def move(self, left: int, right: int, duration_ms: int = 0) -> MoveType:
        l_sign = 1 if left > 0 else - 1
        r_sign = 1 if right > 0 else - 1

        l_direction = 1 if left > 0 else 2
        r_direction = 1 if right > 0 else 2

        l_power = min(abs(left), MotorSpec.MAX_SPEED)
        r_power = min(abs(right), MotorSpec.MAX_SPEED)

        duration = clamp(duration_ms / 10, 0, 255)

        buffer = Buffer.from_data(
            [2, 1, l_direction, l_power, 2, r_direction, r_power, duration]
        )

        data = MoveTypeData(l_sign * l_power, r_sign * r_power, duration * 10)
        return MoveType(buffer, data)

    def move_to(self, targets: List[MoveToTarget], options: MoveToOptions) -> MoveType:

        operation_id = self.__tag.next()
        num_targets = min(
            len(targets), MotorSpec.NUMBER_OF_TARGETS_PER_OPERATION
        )
        buffer = Buffer.alloc(8 + 6 * num_targets)
        buffer.write_uint8(4, 0)
        buffer.write_uint8(operation_id, 1)
        buffer.write_uint8(options.timeout, 2)
        buffer.write_uint8(options.moveType, 3)
        buffer.write_uint8(options.maxSpeed, 4)
        buffer.write_uint8(options.speedType, 5)
        buffer.write_uint8(0, 6)
        buffer.write_uint8(0 if options.overwrite else 1, 7)

        for i in range(num_targets):
            target: MoveToTarget = targets[i]
            x = target.x if target.x is not None else 0xffff
            y = target.y if target.y is not None else 0xffff

            angle = clamp(
                target.angle if target.angle is not None else 0, 0, 0x1fff
            )
            rotate_type = target.rotate_type if target.rotate_type is not None else 0x00

            if (target.angle is None and target.rotate_type != 0x06):
                rotate_type = 0x05

            buffer.write_uint16le(x, 8 + 6 * i)
            buffer.write_uint16le(y, 10 + 6 * i)
            buffer.write_uint16le(
                (rotate_type << 13) | angle, 12 + 6 * i)

        options.operation_id = operation_id
        data = MoveToTypeData(target[0:num_targets], options)
        return MoveType(buffer, data)
