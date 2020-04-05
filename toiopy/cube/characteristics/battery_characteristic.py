from uuid import UUID

from pyee import EventEmitter
from Adafruit_BluefruitLE.interfaces.gatt import GattCharacteristic

from toiopy.cube.characteristics.specs.battery_spec import BatterySpec
from toiopy.data import BatteryType, BatteryTypeData


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
