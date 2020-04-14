from uuid import UUID
from queue import Queue
import time
from typing import List, Optional

from Adafruit_BluefruitLE.interfaces.gatt import GattCharacteristic

from toiopy.characteristic.specs import (
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
    ToioException,
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
from toiopy.util import set_timeout, clear_timeout


class BatteryCharacteristic:
    UUID = UUID('10b201085b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic, event_emitter):
        self.__characteristic: GattCharacteristic = characteristic
        self.__characteristic.start_notify(self.__on_data)
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
            data = self.__characteristic.read_value()

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
            data = self.__characteristic.read_value()

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
        self.__spec: LightSpec = LightSpec()
        self.__timer = None

    def turn_on_light(self, operation: LightOperation):

        if self.__timer:
            clear_timeout(self.__timer)
            self.__timer = None

        data = self.__spec.turn_on_light(operation)
        self.__characteristic.write_value(data.buffer.byte_data)

        if (data.data.duration_ms > 0):
            self.__timer = set_timeout(lambda: None, data.data.duration_ms)

    def turn_on_light_with_scenario(self, operations: List[LightOperation], repeat_count: int = 0):

        if not operations:
            raise ToioException('invalid argument: empty operation')

        if self.__timer:
            clear_timeout(self.__timer)
            self.__timer = None

        data = self.__spec.turn_on_light_with_scenario(
            operations, repeat_count
        )
        self.__characteristic.write_value(data.buffer.byte_data)

        if (data.data.total_duration_ms > 0):
            self.__timer = set_timeout(
                lambda: None, data.data.total_duration_ms
            )

    def turn_off_light(self):

        if self.__timer:
            clear_timeout(self.__timer)
            self.__timer = None

        data = self.__spec.turn_off_light()
        self.__characteristic.write_value(data.buffer.byte_data)


class MotorCharacteristic:
    UUID = UUID('10b201025b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic
        self.__spec = MotorSpec()
        self.__characteristic.start_notify(self.__on_data)
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
        self.__characteristic.write_value(data.buffer.byte_data)

        if (data.data.duration_ms > 0):
            self.__timer = set_timeout(lambda: None, duration_ms)

    def move_to(self, targets, options):
        print("not implemented")
        pass
        """
        if self.__ble_protocol_version != '2.1.0':
            print("ble protocol version is old")

        if self.__timer:
            clear_timeout(self.__timer)
            self.__timer = None

        def create_handler(targets, options):

            data = self.__spec.move_to(targets, options)

            def handle_response(operation_id, reason):
                if operation_id == data.data.options.operation_id:
                    self.__event_emitter.remove_listener(
                        'motor:response', handle_response
                    )
                if reason != 0 and reason != 5:
                    print("error")
            self.__characteristic.write_value(data.buffer.byte_data)
            self.__event_emitter.on('motor:response', handle_response)
        """

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
        self.__spec: SensorSpec = SensorSpec()
        self.__characteristic.start_notify(self.__on_data)
        self.__event_emitter: ToioEventEmitter = eventEmitter
        self.__prev_status: SensorTypeData = SensorTypeData()

    def get_slope_status(self):
        parsedData: SensorTypeData = self.__read()
        return SensorTypeData(is_sloped=parsedData.data.is_sloped)

    def get_collision_status(self):
        parsedData: SensorTypeData = self.__read()
        return SensorTypeData(is_collision_detected=parsedData.data.is_collision_detected)

    def get_double_tap_status(self):
        parsedData: SensorTypeData = self.__read()
        return SensorTypeData(is_double_tapped=parsedData.data.is_double_tapped)

    def get_orientation(self):
        parsedData: SensorTypeData = self.__read()
        return SensorTypeData(orientation=parsedData.data.orientation)

    def __read(self):
        try:
            data = self.__characteristic.read_value()

            if not data:
                raise ToioException('cannot read any data from characteristic')

            parsed_data = self.__spec.parse(Buffer(data))
            return parsed_data
        except Exception as e:
            print(e)
            return None

    def __on_data(self, data):
        try:
            buffer = Buffer.from_data(data)
            parsed_data = self.__spec.parse(buffer)

            if self.__prev_status.is_sloped != parsed_data.data.is_sloped:
                self.__event_emitter.emit(
                    'sensor:slope', SensorTypeData(
                        is_sloped=parsed_data.data.is_sloped
                    )
                )
            if parsed_data.data.is_collision_detected:
                self.__event_emitter.emit(
                    'sensor:collision', SensorTypeData(
                        is_collision_detected=parsed_data.data.is_collision_detected
                    )
                )
            if parsed_data.data.is_double_tapped:
                self.__event_emitter.emit(
                    'sensor:double-tap', SensorTypeData(
                        is_double_tapped=parsed_data.data.is_double_tapped
                    )
                )
            if self.__prev_status.orientation != parsed_data.data.orientation:
                self.__event_emitter.emit(
                    'sensor:orientation', SensorTypeData(
                        orientation=parsed_data.data.orientation
                    )
                )
            self.__prev_status = parsed_data.data
        except Exception as e:
            print(e)


class SoundCharacteristic:
    UUID = UUID('10b201045b3b45719508cf3efcd7bbae')

    def __init__(self, characteristic):
        self.__characteristic: GattCharacteristic = characteristic
        self.__spec: SoundSpec = SoundSpec()
        self.__timer = None

    def play_preset_sound(self, sound_id: int):

        if self.__timer:
            clear_timeout(self.__timer)
            self.__timer = None

        data = self.__spec.play_preset_sound(sound_id)
        self.__characteristic.write_value(data.buffer.byte_data)

        if (data.data.duration_ms > 0):
            self.__timer = set_timeout(lambda: None, data.data.duration_ms)

    def play_sound(self, operations: List[SoundOperation], repeat_count: int = 0):

        if self.__timer:
            clear_timeout(self.__timer)
            self.__timer = None

        data = self.__spec.play_sound(operations, repeat_count)
        self.__characteristic.write_value(data.buffer.byte_data)

        if (data.data.total_duration_ms > 0):
            self.__timer = set_timeout(
                lambda: None, data.data.total_duration_ms
            )

    def stop_sound(self):

        if self.__timer:
            clear_timeout(self.__timer)
            self.__timer = None

        data = self.__spec.stop_sound()
        self.__characteristic.write_value(data.buffer.byte_data)
