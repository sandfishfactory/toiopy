from typing import List, Any
from struct import unpack_from, pack, pack_into
from abc import ABCMeta


class Buffer:

    def __init__(self, byte_data: bytearray):
        self.__byte_data = byte_data
        # 8bit符号なし整数（unsigned char）
        self.bytelength = len(byte_data)

    @classmethod
    def from_data(cls, data_array: List):
        size = len(data_array)
        byte_data = pack('B'*size, *data_array)
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

    @classmethod
    def alloc(cls, size: int):
        return cls(bytearray(size))


class DataType:

    def __init__(self, buffer: Uint8Array, data: Any = None, data_type: str = ''):
        self.buffer = buffer
        self.data = data
        self.data_type = data_type


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

    def __init__(self, x: int, y: int, angle: int, rotate_type: int):
        self.x = x
        self.y = y
        self.angle = angle
        self.rotate_type = rotate_type


class MoveToOptions:

    def __init__(self, move_type: int, max_speed: int, speed_type: int, timeout: int, overwrite: bool):
        self.move_type = move_type
        self.max_speed = max_speed
        self.speed_type = speed_type
        self.timeout = timeout
        self.overwrite = overwrite


class MoveToTypeData:

    def __init__(self, targets: List[MoveToTarget], options: MoveToOptions):
        self.targets = targets
        self.options = options


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
