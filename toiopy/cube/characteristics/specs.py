from enum import Enum
from toiopy.data import (
    Buffer,
    DataType,
    LightOperation,
    TurnOnLightType,
    TurnOnLightWithScenarioType,
    TurnOffLightType,
    TurnOnLightWithScenarioTypeData,
    MotorResponse,
    MotorResponseData,
    MoveType
)
from toiopy.cube.util import clamp
from toiopy.cube.tag import createTagHandler


class StandardId(Enum):
    CARD_TYPHOON = '36700_16'
    CARD_RUSH = '36700_54'
    CARD_AUTO_TACKLE = '36700_18'
    CARD_RANDOM = '36700_56'
    CARD_TACKLE_POWER_UP = '36700_20'
    CARD_SWING_POWER_UP = '36700_58'
    CARD_SIDE_ATTACK = '36700_22'
    CARD_CHASING = '36700_60'

    CARD_LEFT = '36700_24'
    CARD_RIGHT = '36700_62'
    CARD_FRONT = '36700_26'
    CARD_BACK = '36700_64'
    CARD_GO = '36700_28'

    SKUNK_BLUE = '36700_78'
    SKUNK_GREEN = '36700_42'
    SKUNK_YELLOW = '36700_80'
    SKUNK_ORANGE = '36700_44'
    SKUNK_RED = '36700_82'
    SKUNK_BROWN = '36700_46'

    STICKER_SPEED_UP = '36700_66'
    STICKER_SPEED_DOWN = '36700_30'
    STICKER_WOBBLE = '36700_68'
    STICKER_PANIC = '36700_32'
    STICKER_SPIN = '36700_70'
    STICKER_SHOCK = '36700_34'

    MARK_CRAFT_FIGHTER = '36700_48'
    MARK_RHYTHM_AND_GO = '36700_52'
    MARK_SKUNK_CHASER = '36700_86'
    MARK_FINGER_STRIKE = '36700_50'
    MARK_FINGER_STRIKE_1P = '36700_88'
    MARK_FREE_MOVE = '36700_84'


class BatterySpec:

    def parse(self, buffer: Buffer) -> DataType:

        if buffer.bytelength < 1:
            raise Exception("parse error")

        level = buffer.read_uint8(0)
        data = {
            "level": level
        }
        return DataType(buffer, data, 'battery:battery')


class ButtonSpec:

    def parse(self, buffer: Buffer) -> DataType:

        if buffer.bytelength < 2:
            raise Exception("parse error")

        id = buffer.read_uint8(0)

        if id != 1:
            raise Exception("parse error")

        pressed = buffer.read_uint8(1) != 0
        data = {
            'id': id,
            'pressed': pressed
        }
        return DataType(buffer, data, 'button:press')


class IdSpec:

    def parse(self, buffer: Buffer) -> DataType:

        if buffer.bytelength < 1:
            raise Exception("parse error")

        data_type = buffer.read_uint8(0)

        if data_type == 1:
            if buffer.bytelength < 11:
                raise Exception("parse error")
            else:
                data = {
                    'x': buffer.read_uint16le(1),
                    'y': buffer.read_uint16le(3),
                    'angle': buffer.read_uint16le(5),
                    'sensorX': buffer.read_uint16le(7),
                    'sensorY': buffer.read_uint16le(9)
                }
                return DataType(buffer, data, 'id:position-id')
        elif data_type == 2:
            if buffer.bytelength < 7:
                raise Exception("parse error")
            else:
                data = {
                    'standardId': buffer.read_uint32le(1),
                    'angle': buffer.read_uint16le(5)
                }
                return DataType(buffer, data, 'id:standard-id')
        elif data_type == 3:
            return DataType(buffer, data, 'id:position-id-missed')

        elif data_type == 2:
            return DataType(buffer, data, 'id:standard-id-missed')
        else:
            raise Exception("parse error")


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
