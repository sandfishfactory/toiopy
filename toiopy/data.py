from typing import List, Any, Optional
from struct import unpack_from, pack, pack_into
from abc import ABCMeta
from enum import Enum, auto


class StandardId(Enum):
    CARD_TYPHOON = 3670016
    CARD_RUSH = 3670054
    CARD_AUTO_TACKLE = 3670018
    CARD_RANDOM = 3670056
    CARD_TACKLE_POWER_UP = 3670020
    CARD_SWING_POWER_UP = 3670058
    CARD_SIDE_ATTACK = 3670022
    CARD_CHASING = 3670060

    CARD_LEFT = 3670024
    CARD_RIGHT = 3670062
    CARD_FRONT = 3670026
    CARD_BACK = 3670064
    CARD_GO = 3670028

    SKUNK_BLUE = 3670078
    SKUNK_GREEN = 3670042
    SKUNK_YELLOW = 3670080
    SKUNK_ORANGE = 3670044
    SKUNK_RED = 3670082
    SKUNK_BROWN = 3670046

    STICKER_SPEED_UP = 3670066
    STICKER_SPEED_DOWN = 3670030
    STICKER_WOBBLE = 3670068
    STICKER_PANIC = 3670032
    STICKER_SPIN = 3670070
    STICKER_SHOCK = 3670034

    MARK_CRAFT_FIGHTER = 3670048
    MARK_RHYTHM_AND_GO = 3670052
    MARK_SKUNK_CHASER = 3670086
    MARK_FINGER_STRIKE = 3670050
    MARK_FINGER_STRIKE_1P = 3670088
    MARK_FREE_MOVE = 3670084


names = """
C0,CS0,D0,DS0,E0,F0,FS0,G0,GS0,A0,AS0,B0,
C1,CS1,D1,DS1,E1,F1,FS1,G1,GS1,A1,AS1,B1,
C2,CS2,D2,DS2,E2,F2,FS2,G2,GS2,A2,AS2,B2,
C3,CS3,D3,DS3,E3,F3,FS3,G3,GS3,A3,AS3,B3,
C4,CS4,D4,DS4,E4,F4,FS4,G4,GS4,A4,AS4,B4,
C5,CS5,D5,DS5,E5,F5,FS5,G5,GS5,A5,AS5,B5,
C6,CS6,D6,DS6,E6,F6,FS6,G6,GS6,A6,AS6,B6,
C7,CS7,D7,DS7,E7,F7,FS7,G7,GS7,A7,AS7,B7,
C8,CS8,D8,DS8,E8,F8,FS8,G8,GS8,A8,AS8,B8,
C9,CS9,D9,DS9,E9,F9,FS9,G9,GS9,A9,AS9,B9,
C10,CS10,D10,DS10,E10,F10,FS10,G10,
NO_SOUND
"""
Note = Enum('Note', names.replace('\n', ''), module=__name__,
            qualname='toiopy.data.Note', start=0)


class Buffer:

    def __init__(self, byte_data: bytearray):
        self.__byte_data = byte_data
        # 8bit符号なし整数（unsigned char）
        self.bytelength = len(byte_data)

    @property
    def byte_data(self):
        return bytearray(self.__byte_data)

    @classmethod
    def from_data(cls, data_array: List):
        size = len(data_array)
        byte_data = pack('B' * size, *data_array)
        return cls(byte_data)

    def read_uint8(self, offset: int):
        # unpackした結果はtupleになっている
        return unpack_from('B', self.__byte_data, offset)[0]

    def read_uint16le(self, offset: int):
        # unpackした結果はtupleになっている
        return unpack_from('<H', self.__byte_data, offset)[0]

    def read_uint32le(self, offset: int):
        # unpackした結果はtupleになっている
        return unpack_from('<I', self.__byte_data, offset)[0]

    def write_uint8(self, value: int, offset: int):
        return pack_into('B', self.__byte_data, offset, value)

    def write_uint16le(self, value: int, offset: int):
        return pack_into('<H', self.__byte_data, offset, value)

    def to_str(self, encoding: str = 'utf-8', start: int = 0, end: Optional[int] = None):

        if end is None:
            end = self.bytelength

        return self.__byte_data[start:end].decode(encoding)

    @classmethod
    def alloc(cls, size: int):
        return cls(bytearray(size))


class ToioException(Exception):
    pass


class DataType:

    def __init__(self, buffer: Buffer, data: Any = None, data_type: str = ''):
        self.buffer = buffer
        self.data = data
        self.data_type = data_type


class BatteryTypeData:

    def __init__(self, level: int):
        self.level = level


class ButtonTypeData:

    def __init__(self, id: int, pressed: bool):
        self.id = id
        self.pressed = pressed


class PositionIdInfo:

    def __init__(self, x: int, y: int, angle: int, sensor_x: int, sensor_y: int):
        self.x = x
        self.y = y
        self.angle = angle
        self.sensor_x = sensor_x
        self.sensor_y = sensor_y


class StandardIdInfo:

    def __init__(self, standard_id: StandardId, angle: int):
        self.standard_id = standard_id
        self.angle = angle


class LightOperation:

    def __init__(self, duration_ms: int, red: int, green: int, blue: int):
        self.duration_ms = duration_ms
        self.red = red
        self.green = green
        self.blue = blue


class TurnOnLightWithScenarioTypeData:

    def __init__(self, operations: List[LightOperation], repeat_count: int, total_duration_ms: int):
        self.operations = operations
        self.repeat_count = repeat_count
        self.total_duration_ms = total_duration_ms


class MotorResponseData:

    def __init__(self, operation_id: int, reason: int):
        self.operation_id = operation_id
        self.reason = reason


class MoveTypeData:

    def __init__(self, left: int, right: int, duration_ms: int):
        self.left = left
        self.right = right
        self.duration_ms = duration_ms


class MoveToTarget:

    def __init__(self, x: Optional[int], y: Optional[int], angle: Optional[int], rotate_type: Optional[int]):
        self.x = x
        self.y = y
        self.angle = angle
        self.rotate_type = rotate_type


class MoveToOptions:

    def __init__(self, move_type: int, max_speed: int, speed_type: int, timeout: int, overwrite: bool, operation_id: int = None):
        self.move_type = move_type
        self.max_speed = max_speed
        self.speed_type = speed_type
        self.timeout = timeout
        self.overwrite = overwrite
        self.operation_id = operation_id


class MoveToTypeData:

    def __init__(self, targets: List[MoveToTarget], options: MoveToOptions):
        self.targets = targets
        self.options = options


class SensorTypeData:

    def __init__(self, is_sloped: bool, is_collision_detected: bool, is_double_tapped: bool, orientation: int):
        self.is_sloped = is_sloped
        self.is_collision_detected = is_collision_detected
        self.is_double_tapped = is_double_tapped
        self.orientation = orientation


class SoundOperation:

    def __init__(self, duration_ms: int, note_name):
        self.duration_ms = duration_ms
        self.note_name = note_name


class PlayPresetSoundTypeData:

    def __init__(self, sound_id: int):
        self.sound_id = sound_id


class PlaySoundTypeData:

    def __init__(self, operations: List[SoundOperation], repeat_count: int, total_duration_ms: int):
        self.operations = operations
        self.repeat_count = repeat_count
        self.total_duration_ms = total_duration_ms


class BatteryType(DataType):

    def __init__(self, buffer: Buffer, data: BatteryTypeData, data_type: str):
        self.buffer = buffer
        self.data = data
        self.data_type = data_type


class ButtonType(DataType):

    def __init__(self, buffer: Buffer, data: ButtonTypeData, data_type: str):
        self.buffer = buffer
        self.data = data
        self.data_type = data_type


class PositionIdType(DataType):

    def __init__(self, buffer: Buffer, data: PositionIdInfo, data_type: str):
        self.buffer = buffer
        self.data = data
        self.data_type = data_type


class StandardIdType(DataType):

    def __init__(self, buffer: Buffer, data: StandardIdInfo, data_type: str):
        self.buffer = buffer
        self.data = data
        self.data_type = data_type


class IdMissedType(DataType):

    def __init__(self, buffer: Buffer, data_type: str):
        self.buffer = buffer
        self.data_type = data_type


class TurnOnLightType(DataType):

    def __init__(self, buffer: Buffer, data: LightOperation):
        self.buffer = buffer
        self.data = data


class TurnOnLightWithScenarioType(DataType):

    def __init__(self, buffer: Buffer, data: TurnOnLightWithScenarioTypeData):
        self.buffer = buffer
        self.data = data


class TurnOffLightType(DataType):

    def __init__(self, buffer: Buffer):
        self.buffer = buffer


class MotorResponse(DataType):

    def __init__(self, buffer: Buffer, data: MotorResponseData):
        self.buffer = buffer
        self.data = data


class MoveType(DataType):

    def __init__(self, buffer: Buffer, data: MoveTypeData):
        self.buffer = buffer
        self.data = data


class MoveToType(DataType):

    def __init__(self, buffer: Buffer, data: MoveToTypeData):
        self.buffer = buffer
        self.data = data


class SensorType(DataType):

    def __init__(self, buffer: Buffer, data: SensorTypeData, data_type: str):
        self.buffer = buffer
        self.data = data
        self.data_type = data_type


class PlayPresetSoundType(DataType):

    def __init__(self, buffer: Buffer, data: PlayPresetSoundTypeData):
        self.buffer = buffer
        self.data = data


class PlaySoundType(DataType):

    def __init__(self, buffer: Buffer, data: PlaySoundTypeData):
        self.buffer = buffer
        self.data = data


class StopSoundType(DataType):

    def __init__(self, buffer: Buffer):
        self.buffer = buffer
