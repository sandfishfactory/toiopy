from typing import List

from toiopy.data import (
    Buffer,
    SoundOperation,
    PlayPresetSoundType,
    PlayPresetSoundTypeData,
    PlaySoundType,
    PlaySoundTypeData,
    StopSoundType,
)
from toiopy.cube.util import clamp


class SoundSpec:

    def play_preset_sound(self, sound_id: int) -> PlayPresetSoundType:
        arranged_sound_id = clamp(sound_id, 0, 10)
        data = PlayPresetSoundTypeData(sound_id)
        return PlayPresetSoundType(Buffer.from_data([2, arranged_sound_id, 255]), data)

    def play_sound(self, operations: List[SoundOperation], repeat_count: int) -> PlaySoundType:
        arrange_data = PlaySoundTypeData([], clamp(repeat_count, 0, 255), 0)

        num_operations = min(len(operations), 59)

        buffer = Buffer.alloc(3 + 3 * num_operations)
        buffer.write_uint8(3, 0)
        buffer.write_uint8(arrange_data.repeat_count, 1)
        buffer.write_uint8(num_operations, 2)

        total_duration_ms = 0

        for i in range(num_operations):
            operation: SoundOperation = operations[i]
            duration = clamp(operation.duration_ms / 10, 1, 255)
            note_name = operation.note_name

            total_duration_ms += duration
            data = SoundOperation(duration * 10, note_name)
            arrange_data.operations.append(data)

            buffer.write_uint8(duration, 3 + 3 * i)
            buffer.write_uint8(note_name, 4 + 3 * i)
            buffer.write_uint8(255, 5 + 3 * i)

        arrange_data.total_duration_ms = total_duration_ms * 10 * arrange_data.repeat_count

        return PlaySoundType(buffer, arrange_data)

    def stop_sound(self) -> StopSoundType:
        return StopSoundType(Buffer.from_data([1]))
