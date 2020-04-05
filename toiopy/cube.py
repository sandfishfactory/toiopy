from uuid import UUID
from typing import Optional
from time import sleep

from pyee import EventEmitter
from Adafruit_BluefruitLE.interfaces.device import Device

from toiopy.cube.characteristics.battery_characteristic import BatteryCharacteristic


class Cube:

    TOIO_SERVICE_ID = UUID('10b201005b3b45719508cf3efcd7bbae')

    __services = [TOIO_SERVICE_ID]
    __characteristics = [
        BatteryCharacteristic.UUID
    ]

    __battery_characteristic: Optional[BatteryCharacteristic] = None

    def __init__(self, peripheral: Device):
        self.__peripheral: Device = peripheral
        self.__event_emitter: EventEmitter = EventEmitter()

    @property
    def id(self):
        return self.__peripheral.id

    def connect(self):
        try:
            self.__peripheral.connect()
            self.__peripheral.discover(self.__services, self.__characteristics)

            if self.__characteristics:
                self.__set_characteristics()
        except Exception as e:
            print(e)
            return None

    def disconnect(self):
        sleep(10)
        self.__peripheral.disconnect()

    def __set_characteristics(self, characteristics):
        pass

    def __init_characteristics(self, ble_protocol_version: str):
        pass
