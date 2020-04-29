from uuid import UUID
from typing import Optional, List

from Adafruit_BluefruitLE.interfaces.device import Device
from Adafruit_BluefruitLE.interfaces.gatt import GattService, GattCharacteristic

from toiopy.data import (
    ToioException,
    ToioEventEmitter,
    MoveToOptions,
    LightOperation,
    SoundOperation,
    ButtonTypeData,
    BatteryTypeData,
    SensorTypeData,
)
from toiopy.characteristics import (
    BatteryCharacteristic,
    ButtonCharacteristic,
    ConfigurationCharacteristic,
    IdCharacteristic,
    LightCharacteristic,
    MotorCharacteristic,
    SensorCharacteristic,
    SoundCharacteristic,
)
from toiopy.util import set_timeout


class Cube:

    TOIO_SERVICE_ID = UUID("10b201005b3b45719508cf3efcd7bbae")

    _services = [TOIO_SERVICE_ID]
    _characteristics = [
        BatteryCharacteristic.UUID,
        ButtonCharacteristic.UUID,
        ConfigurationCharacteristic.UUID,
        IdCharacteristic.UUID,
        LightCharacteristic.UUID,
        MotorCharacteristic.UUID,
        SensorCharacteristic.UUID,
        SoundCharacteristic.UUID,
    ]

    _battery_characteristic: Optional[BatteryCharacteristic] = None

    def __init__(self, peripheral: Device):
        self._peripheral: Device = peripheral
        self._event_emitter: ToioEventEmitter = ToioEventEmitter()

        self._motor_characteristic: Optional[MotorCharacteristic] = None
        self._light_characteristic: Optional[LightCharacteristic] = None
        self._sound_characteristic: Optional[SoundCharacteristic] = None
        self._sensor_characteristic: Optional[SensorCharacteristic] = None
        self._button_characteristic: Optional[ButtonCharacteristic] = None
        self._battery_characteristic: Optional[BatteryCharacteristic] = None
        self._configuration_characteristic: Optional[ConfigurationCharacteristic] = None

    @property
    def id(self):
        return self._peripheral.id

    def connect(self):
        try:
            self._peripheral.connect()
            self._peripheral.discover(self._services, self._characteristics)
            service: GattService = self._peripheral.find_service(Cube.TOIO_SERVICE_ID)
            characteristics: List[GattCharacteristic] = service.list_characteristics()
            if characteristics:
                self._set_characteristics(characteristics)

            ble_protocol_version = self.get_ble_protocol_version()
            print("ble_protocol_version:{0}\n".format(ble_protocol_version))
            self._init_characteristics(ble_protocol_version)
            print("connected\n")

        except ToioException as e:
            print(e)

    def disconnect(self):
        if self._peripheral.is_connected:
            self._peripheral.disconnect()
            print("disconnect")

    def on(self, event: str, listener):
        self._event_emitter.on(event, listener)
        return self

    def off(self, event: str, listener):
        self._event_emitter.remove_listener(event, listener)
        return self

    # ID Detection

    # Motor Control
    def move(self, left: int, right: int, duration: int):
        if self._motor_characteristic:
            self._motor_characteristic.move(left, right, duration)
        else:
            raise ToioException("motor_characteristic is null")

    def move_to(self, targets, options=MoveToOptions(0, 115, 0, 0, True)):
        if self._motor_characteristic:
            self._motor_characteristic.move_to(targets, options)
        else:
            raise ToioException("motor_characteristic is null")

    def stop(self):
        if self._motor_characteristic:
            self._motor_characteristic.stop()
        else:
            raise ToioException("motor_characteristic is null")

    # LED
    def turn_on_light(self, operation: LightOperation):
        if self._light_characteristic:
            return self._light_characteristic.turn_on_light(operation)
        else:
            raise ToioException("light_characteristic is null")

    def turn_on_light_with_scenario(
        self, operations: List[LightOperation], repeat_count: int = 0
    ):
        if self._light_characteristic:
            return self._light_characteristic.turn_on_light_with_scenario(
                operations, repeat_count
            )
        else:
            raise ToioException("light_characteristic is null")

    def turn_off_light(self):
        if self._light_characteristic:
            return self._light_characteristic.turn_off_light()
        else:
            raise ToioException("light_characteristic is null")

    # Sound
    def play_preset_sound(self, sound_id: int):
        if self._sound_characteristic:
            return self._sound_characteristic.play_preset_sound(sound_id)
        else:
            raise ToioException("sound_characteristic is null")

    def play_sound(self, operations: List[SoundOperation], repeat_count: int = 0):
        if self._sound_characteristic:
            return self._sound_characteristic.play_sound(operations, repeat_count)
        else:
            raise ToioException("sound_characteristic is null")

    def stop_sound(self):
        if self._sound_characteristic:
            return self._sound_characteristic.stop_sound()
        else:
            raise ToioException("sound_characteristic is null")

    # Sensor
    def get_slope_status(self) -> Optional[SensorTypeData]:
        if self._sensor_characteristic:
            return self._sensor_characteristic.get_slope_status()
        else:
            raise ToioException("sensor_characteristic is null")

    def get_collision_status(self) -> Optional[SensorTypeData]:
        if self._sensor_characteristic:
            return self._sensor_characteristic.get_collision_status()
        else:
            raise ToioException("sensor_characteristic is null")

    def get_double_tap_status(self) -> Optional[SensorTypeData]:
        if self._sensor_characteristic:
            return self._sensor_characteristic.get_double_tap_status()
        else:
            raise ToioException("sensor_characteristic is null")

    def get_orientation(self) -> Optional[SensorTypeData]:
        if self._sensor_characteristic:
            return self._sensor_characteristic.get_orientation()
        else:
            raise ToioException("sensor_characteristic is null")

    # button
    def get_button_status(self) -> Optional[ButtonTypeData]:
        if self._button_characteristic:
            return self._button_characteristic.get_button_status()
        else:
            raise ToioException("button_characteristic is null")

    # battery
    def get_battery_status(self) -> Optional[BatteryTypeData]:
        if self._battery_characteristic:
            return self._battery_characteristic.get_battery_status()
        else:
            raise ToioException("battery_characteristic is null")

    # configuration
    def get_ble_protocol_version(self):
        if self._configuration_characteristic:
            return self._configuration_characteristic.get_ble_protocol_version()
        else:
            raise ToioException("configuration_characteristic is null")

    def set_collision_threshold(self, threshold: int):
        if self._configuration_characteristic:
            self._configuration_characteristic.set_collision_threshold(threshold)
        else:
            raise ToioException("configuration_characteristic is null")

    def _set_characteristics(self, characteristics: List[GattCharacteristic]):

        for characteristic in characteristics:
            if IdCharacteristic.UUID == characteristic.uuid:

                IdCharacteristic(characteristic, self._event_emitter)

            elif MotorCharacteristic.UUID == characteristic.uuid:
                characteristic._peripheral = self._peripheral
                self._motor_characteristic = MotorCharacteristic(characteristic)

            elif LightCharacteristic.UUID == characteristic.uuid:

                self._light_characteristic = LightCharacteristic(characteristic)

            elif SoundCharacteristic.UUID == characteristic.uuid:

                self._sound_characteristic = SoundCharacteristic(characteristic)

            elif SensorCharacteristic.UUID == characteristic.uuid:

                self._sensor_characteristic = SensorCharacteristic(
                    characteristic, self._event_emitter
                )

            elif ButtonCharacteristic.UUID == characteristic.uuid:

                self._button_characteristic = ButtonCharacteristic(
                    characteristic, self._event_emitter
                )

            elif BatteryCharacteristic.UUID == characteristic.uuid:

                self._battery_characteristic = BatteryCharacteristic(
                    characteristic, self._event_emitter
                )

            elif ConfigurationCharacteristic.UUID == characteristic.uuid:

                self._configuration_characteristic = ConfigurationCharacteristic(
                    characteristic
                )
        set_timeout(lambda: None, 1000)
        print("set characteristics")

    def _init_characteristics(self, ble_protocol_version: str):
        if self._motor_characteristic:
            self._motor_characteristic.init(ble_protocol_version)
        if self._configuration_characteristic:
            self._configuration_characteristic.init(ble_protocol_version)
