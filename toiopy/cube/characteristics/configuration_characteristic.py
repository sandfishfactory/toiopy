from uuid import UUID
from typing import Optional

from pyee import EventEmitter
from Adafruit_BluefruitLE.interfaces.gatt import GattCharacteristic

from toiopy.cube.characteristics.specs.battery_spec import BatterySpec
from toiopy.data import Buffer, BatteryType, BatteryTypeData


class ConfigurationCharacteristic:
    UUID = UUID('10b201ff5b3b45719508cf3efcd7bbae')

    __event_emitter: EventEmitter = EventEmitter()

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic
        self.__characteristic.start_notify(self.__on_data)
        self.__ble_protocol_version: Optional[str] = None

    def __on_data(self, data):
        self.__data2result(data)

    def init(self, ble_protocol_version: str):
        self.__ble_protocol_version = ble_protocol_version

    def get_battery_status(self) -> BatteryTypeData:
        data = self.__read()
        return data.data

    def __data2result(self, data: Buffer):
        type_data = data.read_uint8(0)

        if type_data == 0x81:
            version = data.to_str('utf-8', start=2, end=7)
            self.__event_emitter.emit(
                'configuration:ble-protocol-version',
                version
            )

    def get_ble_protocol_version(self):

        if self.__ble_protocol_version:
            return self.__ble_protocol_version
        else:
            self.__characteristic.start_notify(self.__subscribe)

    def __subscribe(self):
        pass
