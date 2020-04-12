from uuid import UUID
from queue import Queue
import time
from typing import List, Optional

from Adafruit_BluefruitLE.interfaces.gatt import GattCharacteristic

from toiopy.cube.characteristic.specs import (
    BatterySpec,
    ButtonSpec,
    IdSpec,
    LightSpec,
    MotorSpec,
    SensorSpec,
    SoundSpec
)
from toiopy.data import (
    Buffer,
    ToioEventEmitter,
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
)
from toiopy.cube.util import set_timeout, clear_timeout


class BatteryCharacteristic:
    UUID = UUID('10b201085b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, event_emitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__characteristic.start_notify(self.__on_data)
        time.sleep(1)
        self.__event_emitter: EventEmitter = event_emitter
        self.__spec: BatterySpec = BatterySpec()

    def __on_data(self, data):
        try:
            buffer = Buffer.from_data(data)
            parsed_data: BatteryType = self.__spec.parse(buffer)
            self.__event_emitter.emit('battery:battery', parsed_data.data)
        except Exception as e:
            print(e)

    def get_battery_status(self) -> BatteryTypeData:
        data = self.__read()
        return data.data

    def __read(self) -> BatteryType:
        try:
            data: BatteryType = self.__characteristic.read_value()

            if not data:
                return None

            parsed_data = self.__spec.parse(Buffer(data))
            return parsed_data
        except Exception as e:
            print(e)
            return None


class ButtonCharacteristic:
    UUID = UUID('10b201075b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, eventEmitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__event_emitter = eventEmitter
        self.__spec: ButtonSpec = ButtonSpec()

    def __on_data(self, data):
        try:
            buffer = Buffer.from_data(data)
            parsed_data: ButtonType = self.__spec.parse(buffer)
            self.__event_emitter.emit('button:press', parsed_data.data)
        except Exception as e:
            print(e)

    def get_button_status(self) -> ButtonTypeData:
        data = self.__read()
        return data.data

    def __read(self) -> ButtonType:
        try:
            data: ButtonType = self.__characteristic.read_value()

            if not data:
                return None

            parsed_data = self.__spec.parse(Buffer(data))
            return parsed_data
        except Exception as e:
            print(e)
            return None


class ConfigurationCharacteristic:
    UUID = UUID('10b201ff5b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic
        self.__characteristic.start_notify(self.__on_data)
        time.sleep(1)
        self.__ble_protocol_version: Optional[str] = None
        self.__event_emitter: ToioEventEmitter = ToioEventEmitter()

    def init(self, ble_protocol_version: str):
        self.__ble_protocol_version = ble_protocol_version

    def once_data(self, version):
        self.__ble_protocol_version = version
        self.__event_emitter.put(version)

    def get_ble_protocol_version(self):
        if self.__ble_protocol_version:
            return self.__ble_protocol_version
        else:
            byte_data = Buffer.from_data([0x01, 0x00]).byte_data
            self.__characteristic.write_value(
                byte_data
            )
            self.__event_emitter.once(
                'configuration:ble-protocol-version', self.once_data
            )
            return_value = self.__event_emitter.get()
            return return_value

    def set_collision_threshold(self, threshold: int):
        self.__characteristic.write_value(
            Buffer.from_data([0x06, 0x00, threshold]).byte_data
        )

    def __data2result(self, data: Buffer):
        type_data = data.read_uint8(0)
        if type_data == 0x81:
            version = data.to_str('utf-8', start=2, end=7)
            self.__event_emitter.emit(
                'configuration:ble-protocol-version', version)
        else:
            self.__event_emitter.put(None)

    def __on_data(self, data):
        buffer = Buffer.from_data(data)
        self.__data2result(buffer)


class IdCharacteristic:
    UUID = UUID('10b201015b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, eventEmitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__characteristic.start_notify(self.__on_data)
        time.sleep(1)
        self.__event_emitter = eventEmitter

    def __on_data(self, data):
        buffer = Buffer.from_data(data)
        id_spec = IdSpec()

        try:
            ret = id_spec.parse(buffer)

            if ret.data_type == 'id:position-id':
                self.__event_emitter.emit(ret.data_type, ret.data)
            elif ret.data_type == 'id:standard-id':
                self.__event_emitter.emit(ret.data_type, ret.data)
            elif ret.data_type == 'id:position-id-missed' or ret.data_type == 'id:standard-id-missed':
                self.__event_emitter.emit(ret.data_type)
        except Exception as e:
            print(e)


class LightCharacteristic:
    UUID = UUID('10b201035b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic


class MotorCharacteristic:
    UUID = UUID('10b201025b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic
        self.__spec = MotorSpec()
        self.__characteristic.start_notify(self.__on_data)
        time.sleep(5)
        self.__event_emitter = ToioEventEmitter()
        self.__ble_protocol_version: Optional[str] = None
        self.__timer = None

    def init(self, ble_protocol_version: str):
        self.__ble_protocol_version = ble_protocol_version

    def move(self, left: int, right: int, duration_ms: int):

        if self.__timer:
            clear_timeout(self.__timer)
            self.__timer = None

        data = self.__spec.move(left, right, duration_ms)
        print("__characteristic {0}".format(vars(self.__characteristic)))
        print("byte_data {0}".format(data.buffer.byte_data))
        self.__characteristic.write_value(data.buffer.byte_data)

        if (data.data.duration_ms > 0):
            self.__timer = set_timeout(lambda: None, duration_ms)

    def move_to(self, targets, options):
        pass

    def stop(self):
        self.move(0, 0, 0)

    def __on_data(self, data):
        try:
            buffer = Buffer.from_data(data)
            ret = self.__spec.parse(buffer)
            self.__event_emitter.emit(
                'motor:response', ret.data.operationId, ret.data.reason
            )
        except Exception as e:
            print(e)


class SensorCharacteristic:
    UUID = UUID('10b201065b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, eventEmitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__event_emitter = eventEmitter


class SoundCharacteristic:
    UUID = UUID('10b201045b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic
