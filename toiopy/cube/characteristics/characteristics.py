from uuid import UUID

from pyee import EventEmitter
from Adafruit_BluefruitLE.interfaces.gatt import GattCharacteristic

from toiopy.cube.characteristics.specs.battery_spec import BatterySpec
from toiopy.data import Buffer, BatteryType, BatteryTypeData


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

            parsed_data = self.__spec.parse(data)
            return parsed_data
        except Exception as e:
            print(e)
            return None


class ButtonCharacteristic:
    UUID = UUID('10b201075b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, eventEmitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__event_emitter = eventEmitter


class ConfigurationCharacteristic:
    UUID = UUID('10b201ff5b3b45719508cf3efcd7bbae')

    __event_emitter: EventEmitter = EventEmitter()

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic
        self.__ble_protocol_version: Optional[str] = None

    def __on_data(self, data):
        self.__data2result(data)

    def init(self, ble_protocol_version: str):
        self.__ble_protocol_version = ble_protocol_version

    def __data2result(self, data: bytearray):
        type_data = data.read_uint8(0)
        if type_data == 0x81:
            version = data.to_str('utf-8', start=2, end=7)
            return version
        else:
            return None

    def get_ble_protocol_version(self):
        if self.__ble_protocol_version:
            return self.__ble_protocol_version
        else:
            self.__characteristic.write_value(
                Buffer.from_data([0x01, 0x00]).byte_data
            )
            read_data = self.__characteristic.read_value()
            self.__ble_protocol_version = self.__data2result(read_data)
            return self.__ble_protocol_version

    def setCollisionThreshold(self, threshold: int):
        self.__characteristic.write_value(
            Buffer.from_data([0x06, 0x00, threshold]).byte_data
        )


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
