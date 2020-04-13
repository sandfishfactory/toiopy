from uuid import UUID
from typing import Optional, List
from time import sleep

from Adafruit_BluefruitLE.interfaces.device import Device
from Adafruit_BluefruitLE.interfaces.gatt import GattService, GattCharacteristic

from toiopy.data import ToioException, ToioEventEmitter
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
        BatteryCharacteristic.UUID,
        ButtonCharacteristic.UUID,
        ConfigurationCharacteristic.UUID,
        IdCharacteristic.UUID,
        LightCharacteristic.UUID,
        MotorCharacteristic.UUID,
        SensorCharacteristic.UUID,
        SoundCharacteristic.UUID
    ]

    __battery_characteristic: Optional[BatteryCharacteristic] = None

    def __init__(self, peripheral: Device):
        self.__peripheral: Device = peripheral
        self.__event_emitter: ToioEventEmitter = ToioEventEmitter()

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
            print("-------------------------------------")
            print("connected")
            print("-------------------------------------")
            self.__peripheral.discover(self.__services, self.__characteristics)
            service: GattService = self.__peripheral.find_service(
                Cube.TOIO_SERVICE_ID
            )
            characteristics: List[GattCharacteristic] = \
                service.list_characteristics()
            if characteristics:
                self.__set_characteristics(characteristics)

            ble_protocol_version = self.get_ble_protocol_version()
            print("-------------------------------------")
            print("ble_protocol_version:{0}".format(ble_protocol_version))
            print("-------------------------------------")
            self.__init_characteristics(ble_protocol_version)

        except ToioException as e:
            print(e)

    def disconnect(self):
        if self.__peripheral.is_connected:
            self.__peripheral.disconnect()

    def on(self, event: str, listener):
        self.__event_emitter.on(event, listener)
        return self

    def off(self, event: str, listener):
        self.__event_emitter.remove_listener(event, listener)
        return self

    # ID Detection

    # Motor Control
    def move(self, left: int, right: int, duration: int):
        if self.__motor_characteristic:
            self.__motor_characteristic.move(left, right, duration)

    def stop(self):
        if self.__motor_characteristic:
            self.__motor_characteristic.stop()

    # button
    def get_button_status(self):
        if self.__button_characteristic:
            return self.__button_characteristic.get_button_status()
        else:
            raise ToioException("button_characteristic is null")

    # battery
    def get_battery_status(self):
        if self.__battery_characteristic:
            return self.__battery_characteristic.get_battery_status()
        else:
            raise ToioException("battery_characteristic is null")

    # configuration
    def get_ble_protocol_version(self):
        if self.__configuration_characteristic:
            return self.__configuration_characteristic.get_ble_protocol_version()
        else:
            raise ToioException("configuration_characteristic is null")

    def set_collision_threshold(self, threshold: int):
        if self.__configuration_characteristic:
            self.__configuration_characteristic.set_collision_threshold(
                threshold
            )
        else:
            raise ToioException("configuration_characteristic is null")

    def __set_characteristics(self, characteristics: List[GattCharacteristic]):

        for characteristic in characteristics:
            if IdCharacteristic.UUID == characteristic.uuid:

                IdCharacteristic(characteristic, self.__event_emitter)

            elif MotorCharacteristic.UUID == characteristic.uuid:
                characteristic._peripheral = self.__peripheral
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
        print("-------------------------------------")
        print("set_characteristics")
        print("-------------------------------------")

    def __init_characteristics(self, ble_protocol_version: str):
        if self.__motor_characteristic:
            self.__motor_characteristic.init(ble_protocol_version)
        if self.__configuration_characteristic:
            self.__configuration_characteristic.init(ble_protocol_version)
