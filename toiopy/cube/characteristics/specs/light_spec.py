from typing import List

from toiopy.data import (
    Buffer,
    LightOperation,
    TurnOnLightType,
    TurnOnLightWithScenarioType,
    TurnOffLightType,
    TurnOnLightWithScenarioTypeData,
)
from toiopy.cube.util import clamp


class LightSpec:

    def turn_on_light(self, operation: LightOperation) -> TurnOnLightType:
        duration = clamp(operation.duration_ms / 10, 0, 255)
        red = clamp(operation.red, 0, 255)
        green = clamp(operation.green, 0, 255)
        blue = clamp(operation.blue, 0, 255)

        data_list = [3, duration, 1, 1, red, green, blue]
        data = LightOperation(duration * 10, red, green, blue)
        return TurnOnLightType(Buffer.from_data(data_list), data)

    def turn_on_light_with_scenario(self, operations: List[LightOperation], repeat_count: int) -> TurnOnLightWithScenarioType:
        arrange_data = TurnOnLightWithScenarioTypeData(
            [], clamp(repeat_count, 0, 255), 0
        )

        num_operations = min(operations.length, 29)
        buffer = Buffer.alloc(3 + 6 * num_operations)
        buffer.write_uint8(4, 0)
        buffer.write_uint8(arrange_data.repeat_count, 1)
        buffer.write_uint8(num_operations, 2)

        total_duration_ms = 0

        for i in range(num_operations):
            operation = operations[i]
            duration = clamp(operation.duration_ms / 10, 0, 255)
            red = clamp(operation.red, 0, 255)
            green = clamp(operation.green, 0, 255)
            blue = clamp(operation.blue, 0, 255)

            total_duration_ms += duration

            arrange_data.operations.append(
                LightOperation(duration * 10, red, green, blue)
            )

            buffer.write_uint8(duration, 3 + 6 * i)
            buffer.write_uint8(1, 4 + 6 * i)
            buffer.write_uint8(1, 5 + 6 * i)
            buffer.write_uint8(red, 6 + 6 * i)
            buffer.write_uint8(green, 7 + 6 * i)
            buffer.write_uint8(blue, 8 + 6 * i)

        arrange_data.total_duration_ms = total_duration_ms * 10 * arrange_data.repeat_count

        return TurnOnLightWithScenarioType(buffer, arrange_data)

    def turnOffLight(self) -> TurnOffLightType:
        return TurnOffLightType(Buffer.from_data([1]))
