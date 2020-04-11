from typing import List

from toiopy.data import (
    Buffer,
    DataType,
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
    LightOperation,
    TurnOnLightType,
    TurnOnLightWithScenarioType,
    TurnOffLightType,
    TurnOnLightWithScenarioTypeData,
    MotorResponse,
    MotorResponseData,
    MoveType,
    MoveTypeData,
    MoveToTarget,
    MoveToOptions,
    MoveToType,
    MoveToTypeData,
    SensorType,
    SensorTypeData,
    SoundOperation,
    PlayPresetSoundType,
    PlayPresetSoundTypeData,
    PlaySoundType,
    PlaySoundTypeData,
    StopSoundType,
    ToioException,
)
from toiopy.cube.util import clamp
from toiopy.cube.tag import createTagHandler


class BatterySpec:

    def parse(self, buffer: Buffer) -> BatteryType:

        if buffer.bytelength < 1:
            raise ToioException("parse error")

        level = buffer.read_uint8(0)
        data = BatteryTypeData(level)
        return BatteryType(buffer, data, 'battery:battery')


class ButtonSpec:

    def parse(self, buffer: Buffer) -> ButtonType:

        if buffer.bytelength < 2:
            raise ToioException("parse error")

        id = buffer.read_uint8(0)

        if id != 1:
            raise ToioException("parse error")

        pressed = buffer.read_uint8(1) != 0
        data = ButtonTypeData(id, pressed)
        return ButtonType(buffer, data, 'button:press')


class IdSpec:

    def parse(self, buffer: Buffer) -> DataType:

        if buffer.bytelength < 1:
            raise ToioException("parse error")

        data_type = buffer.read_uint8(0)

        if data_type == 1:
            if buffer.bytelength < 11:
                raise ToioException("parse error")
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
                raise ToioException("parse error")
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
            raise ToioException("parse error")


class LightSpec:

    def turn_on_light(self, operation: LightOperation) -> TurnOnLightType:
        duration = clamp(operation.duration_ms / 10, 0, 255)
        red = clamp(operation.red, 0, 255)
        green = clamp(operation.green, 0, 255)
        blue = clamp(operation.blue, 0, 255)

        data_list = [3, duration, 1, 1, red, green, blue]
        data = LightOperation(duration * 10, red, green, blue)
        return TurnOnLightType(Buffer.from_data(data_list), data)

    def turn_on_light_with_scenario(self, operations: List[LightOperation], repeat_count: int) -> TurnOnLightWithScenarioType:
        arrange_data = TurnOnLightWithScenarioTypeData(
            [], clamp(repeat_count, 0, 255), 0
        )

        num_operations = min(operations.length, 29)
        buffer = Buffer.alloc(3 + 6 * num_operations)
        buffer.write_uint8(4, 0)
        buffer.write_uint8(arrange_data.repeat_count, 1)
        buffer.write_uint8(num_operations, 2)

        total_duration_ms = 0

        for i in range(num_operations):
            operation = operations[i]
            duration = clamp(operation.duration_ms / 10, 0, 255)
            red = clamp(operation.red, 0, 255)
            green = clamp(operation.green, 0, 255)
            blue = clamp(operation.blue, 0, 255)

            total_duration_ms += duration

            arrange_data.operations.append(
                LightOperation(duration * 10, red, green, blue)
            )

            buffer.write_uint8(duration, 3 + 6 * i)
            buffer.write_uint8(1, 4 + 6 * i)
            buffer.write_uint8(1, 5 + 6 * i)
            buffer.write_uint8(red, 6 + 6 * i)
            buffer.write_uint8(green, 7 + 6 * i)
            buffer.write_uint8(blue, 8 + 6 * i)

        arrange_data.total_duration_ms = total_duration_ms * 10 * arrange_data.repeat_count

        return TurnOnLightWithScenarioType(buffer, arrange_data)

    def turnOffLight(self) -> TurnOffLightType:
        return TurnOffLightType(Buffer.from_data([1]))


class MotorSpec:

    MAX_SPEED = 115
    NUMBER_OF_TARGETS_PER_OPERATION = 29

    def __init__(self):
        self.__tag = createTagHandler()

    def parse(self, buffer: Buffer) -> MotorResponse:

        if buffer.bytelength != 3:
            raise ToioException("parse error")

        type_data = buffer.readUInt8(0)

        if type_data == 0x83 or type_data == 0x84:
            data = MotorResponseData(
                buffer.read_uint8(1), buffer.read_uint8(2)
            )
            return MotorResponse(buffer, data)
        else:
            raise ToioException("parse error")

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


class SensorSpec:

    def parse(self, buffer: Buffer) -> SensorType:

        if buffer.bytelength < 3:
            raise ToioException("parse error")

        type_data = buffer.read_uint8(0)

        if type_data != 1:
            raise ToioException("parse error")

        is_sloped = buffer.read_uint8(1) == 0
        is_collision_detected = buffer.read_uint8(2) == 1
        is_double_tapped = buffer.read_uint8(3) == 1
        orientation = buffer.read_uint8(4)

        data = SensorTypeData(
            is_sloped, is_collision_detected, is_double_tapped, orientation
        )

        return SensorType(buffer, data, 'sensor:detection')


class SoundSpec:

    def play_preset_sound(self, sound_id: int) -> PlayPresetSoundType:
        arranged_sound_id = clamp(sound_id, 0, 10)
        data = PlayPresetSoundTypeData(sound_id)
        return PlayPresetSoundType(Buffer.from_data([2, arranged_sound_id, 255]), data)

    def play_sound(self, operations: List[SoundOperation], repeat_count: int) -> PlaySoundType:
        arrange_data = PlaySoundTypeData([], clamp(repeat_count, 0, 255), 0)

        num_operations = min(len(operations), 59)

        buffer = Buffer.alloc(3 + 3 * num_operations)
        buffer.write_uint8(3, 0)
        buffer.write_uint8(arrange_data.repeat_count, 1)
        buffer.write_uint8(num_operations, 2)

        total_duration_ms = 0

        for i in range(num_operations):
            operation: SoundOperation = operations[i]
            duration = clamp(operation.duration_ms / 10, 1, 255)
            note_name = operation.note_name

            total_duration_ms += duration
            data = SoundOperation(duration * 10, note_name)
            arrange_data.operations.append(data)

            buffer.write_uint8(duration, 3 + 3 * i)
            buffer.write_uint8(note_name, 4 + 3 * i)
            buffer.write_uint8(255, 5 + 3 * i)

        arrange_data.total_duration_ms = total_duration_ms * 10 * arrange_data.repeat_count

        return PlaySoundType(buffer, arrange_data)

    def stop_sound(self) -> StopSoundType:
        return StopSoundType(Buffer.from_data([1]))
