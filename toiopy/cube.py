from uuid import UUID
from typing import Optional, List
from time import sleep

from pyee import EventEmitter
from Adafruit_BluefruitLE.interfaces.device import Device
from Adafruit_BluefruitLE.interfaces.gatt import GattService, GattCharacteristic

from toiopy.cube.characteristics import (
    BatteryCharacteristic,
    ButtonCharacteristic,
    ConfigurationCharacteristic,
    IdCharacteristic,
    LightCharacteristic,
    MotorCharacteristic,
    SensorCharacteristic,
    SoundCharacteristic
)


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

        self.__motor_characteristic: Optional[MotorCharacteristic] = None
        self.__light_characteristic: Optional[LightCharacteristic] = None
        self.__sound_characteristic: Optional[SoundCharacteristic] = None
        self.__sensor_characteristic: Optional[SensorCharacteristic] = None
        self.__button_characteristic: Optional[ButtonCharacteristic] = None
        self.__battery_characteristic: Optional[BatteryCharacteristic] = None
        self.__configuration_characteristic: Optional[ConfigurationCharacteristic] = None

    @property
    def id(self):
        return self.__peripheral.id

    def connect(self):
        try:
            self.__peripheral.connect()
            self.__peripheral.discover(self.__services, self.__characteristics)
            service: GattService = self.__peripheral.find_service(
                TOIO_SERVICE_ID
            )

            characteristics: List[GattCharacteristic] = service.list_characteristics(
            )
            if characteristics:
                self.__set_characteristics(characteristics)

            ble_protocol_version = self.get_ble_protocol_version()

            self.__init_characteristics(ble_protocol_version)

        except Exception as e:
            print(e)
            return None

    def disconnect(self):
        sleep(10)
        self.__peripheral.disconnect()

    def on(self, event: str, listener):
        self.__event_emitter.on(event, listener)

    def off(self, event: str, listener):
        self.__event_emitter.remove_listener(event, listener)

    def get_ble_protocol_version(self):
        if self.__configuration_characteristic:
            return self.__configuration_characteristic.get_ble_protocol_version()
        else:
            raise Exception('')

    def __set_characteristics(self, characteristics: List[GattCharacteristic]):

        for characteristic in characteristics:
            if IdCharacteristic.UUID == characteristic.uuid:

                IdCharacteristic(characteristic, self.__event_emitter)

            elif MotorCharacteristic.UUID == characteristic.uuid:

                self.__motor_characteristic = MotorCharacteristic(
                    characteristic
                )

            elif LightCharacteristic.UUID == characteristic.uuid:

                self.__light_characteristic = LightCharacteristic(
                    characteristic
                )

            elif SoundCharacteristic.UUID == characteristic.uuid:

                self.__sound_characteristic = SoundCharacteristic(
                    characteristic
                )

            elif SensorCharacteristic.UUID == characteristic.uuid:

                self.__sensor_characteristic = SensorCharacteristic(
                    characteristic,
                    self.__event_emitter
                )

            elif ButtonCharacteristic.UUID == characteristic.uuid:

                self.__button_characteristic = ButtonCharacteristic(
                    characteristic,
                    self.__event_emitter
                )

            elif BatteryCharacteristic.UUID == characteristic.uuid:

                self.__battery_characteristic = BatteryCharacteristic(
                    characteristic,
                    self.__event_emitter
                )

            elif ConfigurationCharacteristic.UUID == characteristic.uuid:

                self.__configuration_characteristic = ConfigurationCharacteristic(
                    characteristic
                )

            else:
                pass

    def __init_characteristics(self, ble_protocol_version: str):
        if self.__motor_characteristic:
            self.__motor_characteristic.init(ble_protocol_version)
        if self.__configuration_characteristic:
            self.__configuration_characteristic.init(ble_protocol_version)
