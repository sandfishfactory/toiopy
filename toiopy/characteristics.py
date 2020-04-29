from uuid import UUID
from typing import List, Optional, Union

from Adafruit_BluefruitLE.interfaces.gatt import GattCharacteristic

from toiopy.characteristic.specs import (
    BatterySpec,
    ButtonSpec,
    IdSpec,
    LightSpec,
    MotorSpec,
    SensorSpec,
    SoundSpec,
)
from toiopy.data import (
    Buffer,
    ToioEventEmitter,
    ToioException,
    BatteryType,
    BatteryTypeData,
    ButtonType,
    ButtonTypeData,
    PositionIdType,
    StandardIdType,
    IdMissedType,
    LightOperation,
    TurnOnLightType,
    TurnOnLightWithScenarioType,
    TurnOffLightType,
    MotorResponse,
    MoveType,
    MoveToTarget,
    MoveToOptions,
    SensorType,
    SensorTypeData,
    SoundOperation,
    PlayPresetSoundType,
    PlaySoundType,
    StopSoundType,
)
from toiopy.util import set_timeout, clear_timeout


class BatteryCharacteristic:
    UUID = UUID("10b201085b3b45719508cf3efcd7bbae")

    def __init__(
        self, characteristic: GattCharacteristic, event_emitter: ToioEventEmitter
    ):
        self._characteristic: GattCharacteristic = characteristic
        self._characteristic.start_notify(self._on_data)
        self._event_emitter: ToioEventEmitter = event_emitter
        self._spec: BatterySpec = BatterySpec()

    def _on_data(self, data):
        try:
            buffer = Buffer.from_data(data)
            parsed_data: BatteryType = self._spec.parse(buffer)
            self._event_emitter.emit("battery:battery", parsed_data.data)
        except Exception as e:
            print(e)

    def get_battery_status(self) -> Optional[BatteryTypeData]:
        data: Optional[BatteryType] = self._read()
        return data.data if data is not None else None

    def _read(self) -> Optional[BatteryType]:
        try:
            data = self._characteristic.read_value()

            if not data:
                return None

            parsed_data = self._spec.parse(Buffer(data))
            return parsed_data
        except Exception as e:
            print(e)
            return None


class ButtonCharacteristic:
    UUID = UUID("10b201075b3b45719508cf3efcd7bbae")

    def __init__(
        self, characteristic: GattCharacteristic, eventEmitter: ToioEventEmitter
    ):
        self._characteristic: GattCharacteristic = characteristic
        self._event_emitter = eventEmitter
        self._spec: ButtonSpec = ButtonSpec()

    def _on_data(self, data):
        try:
            buffer = Buffer.from_data(data)
            parsed_data: ButtonType = self._spec.parse(buffer)
            self._event_emitter.emit("button:press", parsed_data.data)
        except Exception as e:
            print(e)

    def get_button_status(self) -> Optional[ButtonTypeData]:
        data: Optional[ButtonType] = self._read()
        return data.data if data is not None else None

    def _read(self) -> Optional[ButtonType]:
        try:
            data = self._characteristic.read_value()

            if not data:
                return None

            parsed_data = self._spec.parse(Buffer(data))
            return parsed_data
        except Exception as e:
            print(e)
            return None


class ConfigurationCharacteristic:
    UUID = UUID("10b201ff5b3b45719508cf3efcd7bbae")

    def __init__(self, characteristic: GattCharacteristic):
        self._characteristic: GattCharacteristic = characteristic
        self._characteristic.start_notify(self._on_data)
        self._ble_protocol_version: Optional[str] = None
        self._event_emitter: ToioEventEmitter = ToioEventEmitter()

    def init(self, ble_protocol_version: str):
        self._ble_protocol_version = ble_protocol_version

    def once_data(self, version):
        self._ble_protocol_version = version
        self._event_emitter.put(version)

    def get_ble_protocol_version(self):
        if self._ble_protocol_version:
            return self._ble_protocol_version
        else:
            byte_data = Buffer.from_data([0x01, 0x00]).byte_data
            self._characteristic.write_value(byte_data)
            self._event_emitter.once(
                "configuration:ble-protocol-version", self.once_data
            )
            return_value = self._event_emitter.get()
            return return_value

    def set_collision_threshold(self, threshold: int):
        self._characteristic.write_value(
            Buffer.from_data([0x06, 0x00, threshold]).byte_data
        )

    def _data2result(self, data: Buffer):
        type_data = data.read_uint8(0)
        if type_data == 0x81:
            version = data.to_str("utf-8", start=2, end=7)
            self._event_emitter.emit("configuration:ble-protocol-version", version)
        else:
            self._event_emitter.put(None)

    def _on_data(self, data):
        buffer = Buffer.from_data(data)
        self._data2result(buffer)


class IdCharacteristic:
    UUID = UUID("10b201015b3b45719508cf3efcd7bbae")

    def __init__(
        self, characteristic: GattCharacteristic, eventEmitter: ToioEventEmitter
    ):
        self._characteristic: GattCharacteristic = characteristic
        self._characteristic.start_notify(self._on_data)
        self._event_emitter = eventEmitter

    def _on_data(self, data):
        buffer = Buffer.from_data(data)
        id_spec: IdSpec = IdSpec()

        try:
            ret: Union[PositionIdType, StandardIdType, IdMissedType] = id_spec.parse(
                buffer
            )

            if ret.data_type == "id:position-id":
                self._event_emitter.emit(ret.data_type, ret.data)
            elif ret.data_type == "id:standard-id":
                self._event_emitter.emit(ret.data_type, ret.data)
            elif (
                ret.data_type == "id:position-id-missed"
                or ret.data_type == "id:standard-id-missed"
            ):
                self._event_emitter.emit(ret.data_type)
        except Exception as e:
            print(e)


class LightCharacteristic:
    UUID = UUID("10b201035b3b45719508cf3efcd7bbae")

    def __init__(self, characteristic: GattCharacteristic):
        self._characteristic: GattCharacteristic = characteristic
        self._spec: LightSpec = LightSpec()
        self._timer = None

    def turn_on_light(self, operation: LightOperation):

        if self._timer:
            clear_timeout(self._timer)
            self._timer = None

        data: TurnOnLightType = self._spec.turn_on_light(operation)
        self._characteristic.write_value(data.buffer.byte_data)

        if data is not None and data.data is not None and data.data.duration_ms > 0:
            self._timer = set_timeout(lambda: None, data.data.duration_ms)

    def turn_on_light_with_scenario(
        self, operations: List[LightOperation], repeat_count: int = 0
    ):

        if not operations:
            raise ToioException("invalid argument: empty operation")

        if self._timer:
            clear_timeout(self._timer)
            self._timer = None

        data: TurnOnLightWithScenarioType = self._spec.turn_on_light_with_scenario(
            operations, repeat_count
        )
        self._characteristic.write_value(data.buffer.byte_data)

        if (
            data is not None
            and data.data is not None
            and data.data.total_duration_ms > 0
        ):
            self._timer = set_timeout(lambda: None, data.data.total_duration_ms)

    def turn_off_light(self):

        if self._timer:
            clear_timeout(self._timer)
            self._timer = None

        data: TurnOffLightType = self._spec.turn_off_light()
        self._characteristic.write_value(data.buffer.byte_data)


class MotorCharacteristic:
    UUID = UUID("10b201025b3b45719508cf3efcd7bbae")

    def __init__(self, characteristic: GattCharacteristic):
        self._characteristic: GattCharacteristic = characteristic
        self._spec = MotorSpec()
        self._characteristic.start_notify(self._on_data)
        self._event_emitter = ToioEventEmitter()
        self._ble_protocol_version: Optional[str] = None
        self._timer = None

    def init(self, ble_protocol_version: str):
        self._ble_protocol_version = ble_protocol_version

    def move(self, left: int, right: int, duration_ms: int):

        if self._timer:
            clear_timeout(self._timer)
            self._timer = None

        data: MoveType = self._spec.move(left, right, duration_ms)
        self._characteristic.write_value(data.buffer.byte_data)

        if data is not None and data.data is not None and data.data.duration_ms > 0:
            self._timer = set_timeout(lambda: None, duration_ms)

    def move_to(self, targets: List[MoveToTarget], options: MoveToOptions):
        print("not implemented")
        pass
        """
        if self._ble_protocol_version != '2.1.0':
            print("ble protocol version is old")

        if self._timer:
            clear_timeout(self._timer)
            self._timer = None

        def create_handler(targets, options):

            data = self._spec.move_to(targets, options)

            def handle_response(operation_id, reason):
                if operation_id == data.data.options.operation_id:
                    self._event_emitter.remove_listener(
                        'motor:response', handle_response
                    )
                if reason != 0 and reason != 5:
                    print("error")
            self._characteristic.write_value(data.buffer.byte_data)
            self._event_emitter.on('motor:response', handle_response)
        """

    def stop(self):
        self.move(0, 0, 0)

    def _on_data(self, data):
        try:
            buffer = Buffer.from_data(data)
            ret: MotorResponse = self._spec.parse(buffer)
            self._event_emitter.emit(
                "motor:response", ret.data.operationId, ret.data.reason
            )
        except Exception as e:
            print(e)


class SensorCharacteristic:
    UUID = UUID("10b201065b3b45719508cf3efcd7bbae")

    def __init__(
        self, characteristic: GattCharacteristic, eventEmitter: ToioEventEmitter
    ):
        self._characteristic: GattCharacteristic = characteristic
        self._spec: SensorSpec = SensorSpec()
        self._characteristic.start_notify(self._on_data)
        self._event_emitter: ToioEventEmitter = eventEmitter
        self._prev_status: SensorTypeData = SensorTypeData()

    def get_slope_status(self) -> Optional[SensorTypeData]:
        parsedData: Optional[SensorType] = self._read()
        if parsedData is not None and parsedData.data is not None:
            return (
                SensorTypeData(is_sloped=parsedData.data.is_sloped)
                if parsedData is not None
                else None
            )
        else:
            raise ToioException("cannot read any data from characteristic")

    def get_collision_status(self) -> Optional[SensorTypeData]:
        parsedData: Optional[SensorType] = self._read()
        if parsedData is not None and parsedData.data is not None:
            return (
                SensorTypeData(
                    is_collision_detected=parsedData.data.is_collision_detected
                )
                if parsedData is not None
                else None
            )
        else:
            raise ToioException("cannot read any data from characteristic")

    def get_double_tap_status(self) -> Optional[SensorTypeData]:
        parsedData: Optional[SensorType] = self._read()
        if parsedData is not None and parsedData.data is not None:
            return (
                SensorTypeData(is_double_tapped=parsedData.data.is_double_tapped)
                if parsedData is not None
                else None
            )
        else:
            raise ToioException("cannot read any data from characteristic")

    def get_orientation(self) -> Optional[SensorTypeData]:
        parsedData: Optional[SensorType] = self._read()
        if parsedData is not None and parsedData.data is not None:
            return (
                SensorTypeData(orientation=parsedData.data.orientation)
                if parsedData is not None
                else None
            )
        else:
            raise ToioException("cannot read any data from characteristic")

    def _read(self) -> Optional[SensorType]:
        try:
            data = self._characteristic.read_value()

            if not data:
                raise ToioException("cannot read any data from characteristic")

            parsed_data: SensorType = self._spec.parse(Buffer(data))
            return parsed_data
        except Exception as e:
            print(e)
            return None

    def _on_data(self, data):
        try:
            buffer = Buffer.from_data(data)
            parsed_data: SensorType = self._spec.parse(buffer)

            if self._prev_status.is_sloped != parsed_data.data.is_sloped:
                self._event_emitter.emit(
                    "sensor:slope", SensorTypeData(is_sloped=parsed_data.data.is_sloped)
                )
            if parsed_data.data.is_collision_detected:
                self._event_emitter.emit(
                    "sensor:collision",
                    SensorTypeData(
                        is_collision_detected=parsed_data.data.is_collision_detected
                    ),
                )
            if parsed_data.data.is_double_tapped:
                self._event_emitter.emit(
                    "sensor:double-tap",
                    SensorTypeData(is_double_tapped=parsed_data.data.is_double_tapped),
                )
            if self._prev_status.orientation != parsed_data.data.orientation:
                self._event_emitter.emit(
                    "sensor:orientation",
                    SensorTypeData(orientation=parsed_data.data.orientation),
                )
            self._prev_status = parsed_data.data
        except Exception as e:
            print(e)


class SoundCharacteristic:
    UUID = UUID("10b201045b3b45719508cf3efcd7bbae")

    def __init__(self, characteristic: GattCharacteristic):
        self._characteristic: GattCharacteristic = characteristic
        self._spec: SoundSpec = SoundSpec()
        self._timer = None

    def play_preset_sound(self, sound_id: int):

        if self._timer:
            clear_timeout(self._timer)
            self._timer = None

        data: PlayPresetSoundType = self._spec.play_preset_sound(sound_id)
        self._characteristic.write_value(data.buffer.byte_data)

        if data is not None and data.data is not None and data.data.duration_ms > 0:
            self._timer = set_timeout(lambda: None, data.data.duration_ms)

    def play_sound(self, operations: List[SoundOperation], repeat_count: int = 0):

        if self._timer:
            clear_timeout(self._timer)
            self._timer = None

        data: PlaySoundType = self._spec.play_sound(operations, repeat_count)
        self._characteristic.write_value(data.buffer.byte_data)

        if (
            data is not None
            and data.data is not None
            and data.data.total_duration_ms > 0
        ):
            self._timer = set_timeout(lambda: None, data.data.total_duration_ms)

    def stop_sound(self):

        if self._timer:
            clear_timeout(self._timer)
            self._timer = None

        data: StopSoundType = self._spec.stop_sound()
        self._characteristic.write_value(data.buffer.byte_data)
