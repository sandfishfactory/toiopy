from uuid import UUID
from queue import Queue
import time
from typing import List, Optional

from pyee import BaseEventEmitter
from Adafruit_BluefruitLE.interfaces.gatt import GattCharacteristic

from toiopy.cube.characteristic.specs import (
    BatterySpec,
    ButtonSpec,
)
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


class BatteryCharacteristic:
    UUID = UUID('10b201085b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, event_emitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__characteristic.start_notify(self.__on_data)
        self.__event_emitter: EventEmitter = event_emitter
        self.__spec: BatterySpec = BatterySpec()

    def __on_data(self, data):
        try:
            parsed_data: BatteryType = self.__spec.parse(data)
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
            parsed_data: ButtonType = self.__spec.parse(data)
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
        print("##### ConfigurationCharacteristic #####")
        self.__characteristic: GattCharacteristic = characteristic
        self.__characteristic.start_notify(self.__on_data)
        time.sleep(2)
        print(vars(self.__characteristic))
        self.__ble_protocol_version: Optional[str] = None
        self.__event_emitter: BaseEventEmitter = BaseEventEmitter()
        self.__queue = Queue()

    def init(self, ble_protocol_version: str):
        self.__ble_protocol_version = ble_protocol_version

    def once_data(self, version):
        print("##### ConfigurationCharacteristic once_data #####")
        print(version)
        self.__ble_protocol_version = version
        self.__queue.put(version)

    def get_ble_protocol_version(self):
        if self.__ble_protocol_version:
            return self.__ble_protocol_version
        else:
            print(
                "##### ConfigurationCharacteristic get_ble_protocol_version write_value #####"
            )
            byte_data = Buffer.from_data([0x01, 0x00]).byte_data
            print("byte_data: {0}".format(byte_data))
            self.__characteristic.write_value(
                byte_data
            )
            print(
                "##### ConfigurationCharacteristic get_ble_protocol_version __queue #####"
            )
            self.__event_emitter.once(
                'configuration:ble-protocol-version', self.once_data
            )
            return_value = self.__queue.get()
            print("return_value: {0}".format(return_value))
            return return_value

    def set_collision_threshold(self, threshold: int):
        self.__characteristic.write_value(
            Buffer.from_data([0x06, 0x00, threshold]).byte_data
        )

    def __data2result(self, data: bytearray):
        print("##### ConfigurationCharacteristic __data2result #####")
        buffer = Buffer.from_data(data)
        type_data = buffer.read_uint8(0)
        if type_data == 0x81:
            version = buffer.to_str('utf-8', start=2, end=7)
            print("##### ConfigurationCharacteristic __queue.put #####")
            self.__event_emitter.emit(
                'configuration:ble-protocol-version', version)
        else:
            self.__queue.put(None)

    def __on_data(self, data):
        print("##### ConfigurationCharacteristic __on_data #####")
        print("data: {0}".format(data))
        self.__data2result(data)


class IdCharacteristic:
    UUID = UUID('10b201015b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, eventEmitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__event_emitter = eventEmitter


class LightCharacteristic:
    UUID = UUID('10b201035b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic


class MotorCharacteristic:
    UUID = UUID('10b201025b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic

    def init(self, ble_protocol_version: str):
        pass


class SensorCharacteristic:
    UUID = UUID('10b201065b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, eventEmitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__event_emitter = eventEmitter


class SoundCharacteristic:
    UUID = UUID('10b201045b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic
