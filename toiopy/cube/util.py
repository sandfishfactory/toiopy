

def clamp(value: int, min_value: int, max_value: int) -> int:
    return max([min([value, max_value]), min_value])
